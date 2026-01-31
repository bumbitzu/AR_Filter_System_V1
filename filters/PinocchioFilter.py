import cv2
import mediapipe as mp
import numpy as np
import time

from core.FaceMeshFactory import create_face_mesh

class PinocchioFilter:
    """
    AR filter that creates a Pinocchio nose adapting to head rotation.
    """
    
    def __init__(self):
        """Initialize MediaPipe Face Mesh and filter parameters."""
        self.face_mesh = create_face_mesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        
        # Key landmark indices for PnP (Head Pose)
        self.nose_tip = 4
        self.chin = 152
        self.left_eye = 33
        self.right_eye = 263
        self.left_mouth = 61
        self.right_mouth = 291
        
        # Generic 3D Model of a Face (Standard for AR)
        # Coordinates usually normalized around nose tip (0,0,0)
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left Mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype="double")

        # Filter parameters
        self.start_time = None
        self.growth_duration = 30.0
        self.min_length = 20
        self.max_length = 250
        
        # Smear parameters
        self.base_width = 30
        self.tip_width = 8
        self.num_segments = 60
        
    def _calculate_growth_factor(self):
        if self.start_time is None:
            self.start_time = time.time()
            return 0.0
        elapsed = time.time() - self.start_time
        progress = min(elapsed / self.growth_duration, 1.0)
        return float(progress ** 1.5)
    
    def _extract_nose_texture(self, frame, nose_x, nose_y, radius):
        h, w = frame.shape[:2]
        x1, y1 = max(0, nose_x - radius), max(0, nose_y - radius)
        x2, y2 = min(w, nose_x + radius), min(h, nose_y + radius)
        
        roi = frame[y1:y2, x1:x2].copy()
        mask = np.zeros(roi.shape[:2], dtype=np.uint8)
        
        # Ensure center is relative to ROI
        center_x = min(radius, roi.shape[1] // 2)
        center_y = min(radius, roi.shape[0] // 2)
        
        cv2.circle(mask, (radius, radius), radius, 255, -1)
        
        if roi.shape[0] > 0 and roi.shape[1] > 0:
            roi_masked = cv2.bitwise_and(roi, roi, mask=mask)
            return roi_masked, mask
        return None, None
    
    def _get_average_skin_color(self, texture, mask):
        if texture is None or mask is None:
            return (180, 140, 120)
        mean_color = cv2.mean(texture, mask=mask)[:3]
        return tuple(int(c) for c in mean_color)

    def _get_nose_direction(self, face_landmarks, frame_shape, nose_length_px):
        """
        Calculates the 2D end-point of the nose based on 3D head rotation.
        """
        h, w, _ = frame_shape
        
        # 1. Get 2D Image Points from Landmarks
        image_points = np.array([
            (face_landmarks.landmark[self.nose_tip].x * w, face_landmarks.landmark[self.nose_tip].y * h),
            (face_landmarks.landmark[self.chin].x * w, face_landmarks.landmark[self.chin].y * h),
            (face_landmarks.landmark[self.left_eye].x * w, face_landmarks.landmark[self.left_eye].y * h),
            (face_landmarks.landmark[self.right_eye].x * w, face_landmarks.landmark[self.right_eye].y * h),
            (face_landmarks.landmark[self.left_mouth].x * w, face_landmarks.landmark[self.left_mouth].y * h),
            (face_landmarks.landmark[self.right_mouth].x * w, face_landmarks.landmark[self.right_mouth].y * h)
        ], dtype="double")

        # 2. Camera Internals (Approximate)
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        dist_coeffs = np.zeros((4, 1)) # Assuming no lens distortion

        # 3. Solve PnP to get Rotation Vector
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            # Fallback if PnP fails
            return face_landmarks.landmark[self.nose_tip].x * w, face_landmarks.landmark[self.nose_tip].y * h

        # 4. Project a 3D point "forward" from the nose tip
        # We project a point at (0, 0, Z) where Z is how "long" the nose is in 3D space
        # Usually +Z is forward in this model space
        nose_end_point_3D = np.array([[0.0, 0.0, 500.0]]) # 500 arbitrary units forward
        
        nose_end_point_2D, _ = cv2.projectPoints(
            nose_end_point_3D, rotation_vector, translation_vector, camera_matrix, dist_coeffs
        )

        # Get the coordinates
        target_x = nose_end_point_2D[0][0][0]
        target_y = nose_end_point_2D[0][0][1]
        
        return target_x, target_y
    
    def _draw_extruded_nose(self, frame, start_x, start_y, target_x, target_y, length, texture, mask):
        if texture is None: return frame
        
        h, w = frame.shape[:2]
        
        # Calculate Direction Vector (dx, dy) based on PnP result
        vec_x = target_x - start_x
        vec_y = target_y - start_y
        
        # Normalize vector
        magnitude = np.sqrt(vec_x**2 + vec_y**2)
        if magnitude == 0: return frame
        
        dx = vec_x / magnitude
        dy = vec_y / magnitude

        avg_color = self._get_average_skin_color(texture, mask)
        
        # Draw Segments
        for i in range(self.num_segments):
            t = i / self.num_segments
            
            # Position along the calculated vector
            curr_x = int(start_x + dx * length * t)
            curr_y = int(start_y + dy * length * t)
            
            # Tapered width
            width = int(self.base_width * (1.0 - t) + self.tip_width * t)
            if width < 2: continue
            
            # Resize and Blend Logic
            try:
                tex_size = width * 2
                resized_texture = cv2.resize(texture, (tex_size, tex_size))
                resized_mask = cv2.resize(mask, (tex_size, tex_size))
                
                x1 = curr_x - tex_size // 2
                y1 = curr_y - tex_size // 2
                x2 = x1 + tex_size
                y2 = y1 + tex_size
                
                if x1 >= 0 and y1 >= 0 and x2 < w and y2 < h:
                    roi = frame[y1:y2, x1:x2]
                    mask_3ch = cv2.cvtColor(resized_mask, cv2.COLOR_GRAY2BGR) / 255.0
                    blended = (resized_texture * mask_3ch + roi * (1 - mask_3ch)).astype(np.uint8)
                    frame[y1:y2, x1:x2] = blended
            except:
                continue
        
        # Draw Tip
        tip_x = int(start_x + dx * length)
        tip_y = int(start_y + dy * length)
        if 0 <= tip_x < w and 0 <= tip_y < h:
            cv2.circle(frame, (tip_x, tip_y), self.tip_width, avg_color, -1)
            
        return frame
    
    def apply(self, frame):
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return frame
            
        face_landmarks = results.multi_face_landmarks[0]
        
        # 1. Get Nose Anchor
        nose_tip_lm = face_landmarks.landmark[self.nose_tip]
        nose_x = int(nose_tip_lm.x * w)
        nose_y = int(nose_tip_lm.y * h)
        
        # 2. Calculate Scale (based on distance)
        bridge = face_landmarks.landmark[168]
        bottom = face_landmarks.landmark[1]
        face_scale = (abs(bridge.y - bottom.y) * h) / 60.0
        
        # 3. Determine Direction (The Fix!)
        # Get the target point where the nose "looks" at
        target_x, target_y = self._get_nose_direction(face_landmarks, frame.shape, 200)

        # 4. Growth logic
        growth = self._calculate_growth_factor()
        nose_length = int(self.min_length + (self.max_length - self.min_length) * growth)
        
        # 5. Extract and Draw
        scaled_base = int(self.base_width * face_scale)
        scaled_tip = int(self.tip_width * face_scale)
        
        # Override widths for drawing
        orig_base, orig_tip = self.base_width, self.tip_width
        self.base_width, self.tip_width = scaled_base, scaled_tip
        
        texture, mask = self._extract_nose_texture(frame, nose_x, nose_y, scaled_base//2)
        
        frame = self._draw_extruded_nose(frame, nose_x, nose_y, target_x, target_y, 
                                       nose_length, texture, mask)
                                       
        # Restore widths
        self.base_width, self.tip_width = orig_base, orig_tip
        
        return frame

    def reset(self):
        self.start_time = None

# --- Main Execution ---
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    filter = PinocchioFilter()
    
    print("Apasa 'q' pentru a iesi, 'r' pentru resetare lungime.")
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success: break
        
        frame = cv2.flip(frame, 1) # Mirror for selfie feel
        output = filter.apply(frame)
        
        cv2.imshow('Pinocchio AR Corrected', output)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        if key == ord('r'): filter.reset()
        
    cap.release()
    cv2.destroyAllWindows()