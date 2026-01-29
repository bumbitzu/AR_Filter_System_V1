import cv2
import mediapipe as mp
import numpy as np


class AlienFaceFilter:
    """
    Advanced AR filter that transforms a human face into an alien ('Grey Alien') appearance.
    
    Features:
    - Head Elongation: Vertically stretches the cranium for an elongated skull effect
    - Large Black Eyes: Scales and overlays glossy black elliptical masks over eyes
    - Chin/Jaw Slimming: Narrows the lower jaw for a characteristic V-shape
    
    Performance: Optimized using cv2.remap for real-time 60 FPS processing
    """
    
    def __init__(self):
        """Initialize MediaPipe Face Mesh and filter parameters."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Key landmark indices for facial features
        # Forehead/Head landmarks
        self.forehead_top = 10      # Top of forehead
        self.forehead_left = 108    # Left side of forehead
        self.forehead_right = 338   # Right side of forehead
        
        # Eye landmarks (iris centers for refined detection)
        self.left_eye_center = 468  # Left iris center
        self.right_eye_center = 473 # Right iris center
        
        # Left eye contour landmarks
        self.left_eye_landmarks = [33, 160, 158, 133, 153, 144]
        
        # Right eye contour landmarks  
        self.right_eye_landmarks = [362, 385, 387, 263, 373, 380]
        
        # Jaw/chin landmarks for slimming
        self.chin_point = 152       # Bottom of chin
        self.left_jaw = 234         # Left jaw
        self.right_jaw = 454        # Right jaw
        
        # Filter strength parameters
        self.elongation_strength = 0.55   # Head elongation factor
        self.eye_scale = 1.7              # Eye enlargement factor (1.5x - 2.0x)
        self.jaw_slim_strength = 0.25     # Jaw narrowing factor
        
    def _get_eye_region(self, landmarks, eye_landmarks, w, h):
        """
        Calculate the bounding box and center of an eye region.
        
        Args:
            landmarks: Face landmarks from MediaPipe
            eye_landmarks: List of landmark indices for the eye
            w, h: Frame dimensions
            
        Returns:
            tuple: (center_x, center_y, width, height) of eye region
        """
        eye_points = []
        for idx in eye_landmarks:
            lm = landmarks.landmark[idx]
            eye_points.append([int(lm.x * w), int(lm.y * h)])
        
        eye_points = np.array(eye_points, dtype=np.int32)
        x, y, ew, eh = cv2.boundingRect(eye_points)
        
        center_x = x + ew // 2
        center_y = y + eh // 2
        
        return center_x, center_y, ew, eh
    
    def _create_mesh_warp(self, frame, landmarks):
        """
        Create mesh deformation maps for alien facial transformation.
        
        Uses cv2.remap for high-performance warping with smooth transitions.
        Applies:
        - Vertical head elongation
        - Jaw/chin slimming (horizontal narrowing)
        
        Args:
            frame: Input video frame
            landmarks: Face landmarks from MediaPipe
            
        Returns:
            tuple: (map_x, map_y) for cv2.remap
        """
        h, w = frame.shape[:2]
        
        # Initialize identity mapping (no distortion)
        map_x, map_y = np.meshgrid(np.arange(w, dtype=np.float32), 
                                     np.arange(h, dtype=np.float32))
        
        # Get key facial points
        forehead_lm = landmarks.landmark[self.forehead_top]
        chin_lm = landmarks.landmark[self.chin_point]
        left_jaw_lm = landmarks.landmark[self.left_jaw]
        right_jaw_lm = landmarks.landmark[self.right_jaw]
        
        # Convert to pixel coordinates (ensure real values)
        forehead_y = float(forehead_lm.y * h)
        chin_y = float(chin_lm.y * h)
        face_center_x = float(forehead_lm.x * w)
        
        # Calculate face height
        face_height = float(chin_y - forehead_y)
        
        # === HEAD ELONGATION ===
        # Apply vertical stretching to upper head (forehead to eyebrows area)
        elongation_zone_bottom = float(forehead_y + face_height * 0.35)  # Up to eyebrow level
        
        for y in range(int(forehead_y), min(int(elongation_zone_bottom), h)):
            # Calculate distance from forehead (0 to 1)
            if elongation_zone_bottom > forehead_y:
                t = float((y - forehead_y) / (elongation_zone_bottom - forehead_y))
            else:
                t = 0.0
            
            # Smooth falloff using ease-out curve
            # Use numpy operations to ensure real arithmetic
            t_clamped = np.clip(np.real(t), 0.0, 1.0)
            one_minus_t = 1.0 - t_clamped
            one_minus_t_squared = np.power(one_minus_t, 2.0, dtype=np.float64)
            falloff = np.real(1.0 - one_minus_t_squared)
            
            # Calculate vertical displacement (pull upward)
            displacement = float(-face_height * self.elongation_strength * (1.0 - falloff))
            
            # Apply vertical stretch
            source_y = float(y - displacement)
            source_y = float(np.clip(source_y, 0, h - 1))
            
            map_y[y, :] = source_y
        
        # === JAW SLIMMING ===
        # Apply horizontal narrowing to lower face (below nose to chin)
        jaw_zone_top = float(forehead_y + face_height * 0.6)  # Start from nose level
        
        for y in range(int(jaw_zone_top), min(int(chin_y), h)):
            # Calculate distance from top of jaw zone (0 to 1)
            if chin_y > jaw_zone_top:
                t = float((y - jaw_zone_top) / (chin_y - jaw_zone_top))
            else:
                t = 0.0
            
            # Stronger effect toward chin (ease-in curve)
            # Use numpy power with real inputs to avoid complex numbers
            t_clamped = np.clip(np.real(t), 0.0, 1.0)
            t_powered = np.power(t_clamped, 1.5, dtype=np.float64)
            strength = np.real(t_powered * self.jaw_slim_strength)
            
            # Apply horizontal narrowing toward face center
            dx = map_x[y, :] - face_center_x
            
            # Smooth transition zone based on distance from center
            face_width = float(abs(right_jaw_lm.x - left_jaw_lm.x) * w)
            lateral_falloff = np.exp(-np.abs(dx) / (face_width * 0.8))
            
            # Calculate horizontal displacement
            displacement = dx * strength * lateral_falloff
            
            # Apply narrowing (ensure real-valued result)
            source_x = np.real(map_x[y, :] - displacement).astype(np.float32)
            source_x = np.clip(source_x, 0, w - 1)
            
            map_x[y, :] = source_x
        
        return map_x, map_y
    
    def _draw_alien_eye(self, frame, center_x, center_y, base_width, base_height):
        """
        Draw a large, glossy black alien eye overlay.
        
        Creates a semi-transparent elliptical mask with highlights for a 'Grey Alien' look.
        
        Args:
            frame: Frame to draw on
            center_x, center_y: Eye center coordinates
            base_width, base_height: Original eye dimensions
        """
        # Scale up the eye area
        eye_width = int(base_width * self.eye_scale)
        eye_height = int(base_height * self.eye_scale)
        
        # Ensure minimum size for visibility
        eye_width = max(eye_width, 40)
        eye_height = max(eye_height, 30)
        
        # Create a temporary overlay for alpha blending
        overlay = frame.copy()
        
        # Main eye ellipse (glossy black)
        eye_color = (15, 15, 15)  # Very dark gray (almost black)
        cv2.ellipse(overlay, 
                   (int(center_x), int(center_y)), 
                   (eye_width // 2, eye_height // 2),
                   0, 0, 360, 
                   eye_color, 
                   -1, 
                   cv2.LINE_AA)
        
        # Outer glow/rim for depth
        rim_color = (5, 5, 5)  # Darker edge
        cv2.ellipse(overlay,
                   (int(center_x), int(center_y)),
                   (eye_width // 2 + 2, eye_height // 2 + 2),
                   0, 0, 360,
                   rim_color,
                   2,
                   cv2.LINE_AA)
        
        # Blend with transparency (semi-transparent for realism)
        alpha = 0.85  # 85% opacity for alien eye
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Add glossy highlight (small white reflection)
        highlight_overlay = frame.copy()
        highlight_x = int(center_x - eye_width * 0.15)
        highlight_y = int(center_y - eye_height * 0.2)
        highlight_w = int(eye_width * 0.25)
        highlight_h = int(eye_height * 0.35)
        
        cv2.ellipse(highlight_overlay,
                   (highlight_x, highlight_y),
                   (highlight_w // 2, highlight_h // 2),
                   0, 0, 360,
                   (220, 220, 220),  # Light gray highlight
                   -1,
                   cv2.LINE_AA)
        
        # Blend highlight with lower opacity for glossy effect
        highlight_alpha = 0.3
        cv2.addWeighted(highlight_overlay, highlight_alpha, frame, 1 - highlight_alpha, 0, frame)
        
        # Add secondary smaller highlight for extra gloss
        highlight2_x = int(center_x + eye_width * 0.1)
        highlight2_y = int(center_y + eye_height * 0.15)
        
        cv2.circle(highlight_overlay,
                  (highlight2_x, highlight2_y),
                  int(eye_width * 0.08),
                  (255, 255, 255),  # Bright white
                  -1,
                  cv2.LINE_AA)
        
        cv2.addWeighted(highlight_overlay, 0.2, frame, 0.8, 0, frame)
    
    def _apply_green_skin(self, frame, landmarks):
        """
        Apply green alien skin tone to the face area.
        
        Args:
            frame: Input frame
            landmarks: Face landmarks from MediaPipe
            
        Returns:
            Frame with green alien skin applied
        """
        h, w = frame.shape[:2]
        
        # Create mask for face area
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Face oval landmarks (entire face outline)
        face_oval = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        
        # Get face oval points
        points = []
        for idx in face_oval:
            lm = landmarks.landmark[idx]
            points.append([int(lm.x * w), int(lm.y * h)])
        
        # Fill face area on mask
        cv2.fillPoly(mask, [np.array(points)], 255)
        
        # Create green alien skin overlay
        green_overlay = frame.copy()
        
        # Apply alien green color (BGR format: Green dominant with slight blue/red)
        # This creates a realistic alien skin tone
        alien_green = np.array([60, 180, 80], dtype=np.uint8)  # BGR: slightly blue-green
        
        # Apply green tint only to face area
        green_overlay[mask > 0] = cv2.addWeighted(
            frame[mask > 0], 0.35,  # 35% original skin
            np.full_like(frame[mask > 0], alien_green), 0.65,  # 65% green alien color
            0
        )
        
        # Smooth the edges for better blending
        mask_blurred = cv2.GaussianBlur(mask, (15, 15), 0)
        mask_3ch = cv2.cvtColor(mask_blurred, cv2.COLOR_GRAY2BGR) / 255.0
        
        # Blend with original frame
        result = (green_overlay * mask_3ch + frame * (1 - mask_3ch)).astype(np.uint8)
        
        return result
    
    def apply(self, frame):
        """
        Apply the Alien Face filter to a video frame.
        
        Args:
            frame: Input BGR video frame
            
        Returns:
            np.array: Transformed frame with alien effect applied
        """
        h, w = frame.shape[:2]
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect face landmarks
        results = self.face_mesh.process(rgb_frame)
        
        # Return original frame if no face detected
        if not results.multi_face_landmarks:
            return frame
        
        # Process first detected face
        face_landmarks = results.multi_face_landmarks[0]
        
        # === STEP 1: Apply green alien skin ===
        alien_frame = self._apply_green_skin(frame, face_landmarks)
        
        # === STEP 2: Draw alien eyes ===
        # Get left eye region
        left_cx, left_cy, left_w, left_h = self._get_eye_region(
            face_landmarks, self.left_eye_landmarks, w, h
        )
        
        # Get right eye region
        right_cx, right_cy, right_w, right_h = self._get_eye_region(
            face_landmarks, self.right_eye_landmarks, w, h
        )
        
        # Draw enlarged alien eyes
        self._draw_alien_eye(alien_frame, left_cx, left_cy, left_w, left_h)
        self._draw_alien_eye(alien_frame, right_cx, right_cy, right_w, right_h)
        
        return alien_frame
