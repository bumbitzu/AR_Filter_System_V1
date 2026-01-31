import cv2
import numpy as np
import mediapipe as mp
import math

from core.FaceMeshFactory import create_face_mesh

class CubeHeadFilter:
    def __init__(self):
        self.face_mesh = create_face_mesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.base_map_x = None
        self.base_map_y = None
        
        # Filter Parameters
        self.debug_printed = False
        
        # Tuning
        self.warp_grid_shape = (80, 80)
        self.strength = 1.0
        self.square_factor = 0.85 

    def get_landmarks(self, image):
        """Extracts landmarks from the image."""
        h, w = image.shape[:2]
        results = self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0]
        points = np.array([(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark])
        return points

    def apply(self, frame, landmarks=None):
        h, w = frame.shape[:2]
        
        if landmarks is None:
            landmarks = self.get_landmarks(frame)
            
        if landmarks is None:
            return frame
            
        if not self.debug_printed:
            print(f"🧊 Cube Head Active! Rotation Supported.")
            self.debug_printed = True

        # Lazy Init Maps
        if self.base_map_x is None or self.base_map_x.shape != (h, w):
            self.base_map_x, self.base_map_y = np.meshgrid(
                np.arange(w, dtype=np.float32),
                np.arange(h, dtype=np.float32)
            )

        # Create low-res grid for Warp
        grid_h, grid_w = 80, int(80 * (w / h)) 
        x_lin = np.linspace(0, w, grid_w, dtype=np.float32)
        y_lin = np.linspace(0, h, grid_h, dtype=np.float32)
        grid_x, grid_y = np.meshgrid(x_lin, y_lin)
        
        offset_x = np.zeros_like(grid_x)
        offset_y = np.zeros_like(grid_y)
        
        # -- Logic: Cube Transformation (Rotation Aware) --
        
        idx_center = 168 # Nose bridge
        idx_chin = 152
        idx_forehead = 10
        idx_left = 234
        idx_right = 454
        
        pt_center = landmarks[idx_center]
        pt_chin = landmarks[idx_chin]
        pt_forehead = landmarks[idx_forehead]
        
        # 1. Calculate Rotation Basis Vectors
        # Up Vector: Chin to Forehead (Positive Y is down in image, so we consider Forehead-Chin as 'Up' in face space inverted? 
        # Let's define Face UP as Forehead - Chin)
        vec_v = pt_forehead - pt_chin
        
        face_height = np.linalg.norm(vec_v)
        
        # Normalize Vertical Vector (Up axis)
        if face_height > 0:
            ux = vec_v[0] / face_height
            uy = vec_v[1] / face_height
        else:
            ux, uy = 0, -1
            
        # Horizontal Vector (Right axis) = Perpendicular to Up
        # If Up is (ux, uy), Right is (-uy, ux) (Standard 90 deg rotation)
        rx, ry = -uy, ux
        
        # Calculate Dimensions based on landmarks
        # We need a radius for the square
        half_w = np.linalg.norm(landmarks[idx_left] - landmarks[idx_right]) * 0.65
        radius = (face_height * 0.55 + half_w) / 2.0
        
        # 2. Project Grid to Local Coordinates
        # Vector from center to grid point
        dx = grid_x - pt_center[0]
        dy = grid_y - pt_center[1]
        
        # Local X (Horizontal dist) = Dot(d, Right)
        local_x = dx * rx + dy * ry
        # Local Y (Vertical dist) = Dot(d, Up)
        local_y = dx * ux + dy * uy
        
        # Distance in local space (should be same as global dist)
        dist = np.sqrt(local_x*local_x + local_y*local_y)
        angle = np.arctan2(local_y, local_x)
        
        # 3. Calculate "Square Distance" in LOCAL SPACE
        # We want the square to align with local axes
        denom = np.maximum(np.abs(np.cos(angle)), np.abs(np.sin(angle)))
        # dist_square is the distance to the edge of a square if we projected current point onto it
        dist_square = dist * denom
        
        # 4. Warp Logic (Same as before, but using local_x/y implied by dist/dist_square)
        
        norm_dist = dist / radius
        
        # Mask
        mask_weight = np.clip(norm_dist, 0.0, 1.5)
        mask_weight = np.clip((mask_weight - 0.3) / 0.7, 0.0, 1.0)
        mask_weight = mask_weight * mask_weight * (3 - 2 * mask_weight)
        
        decay = np.clip((1.5 - norm_dist) / 0.5, 0.0, 1.0) 
        mask_weight *= decay
        
        factor = self.square_factor * mask_weight
        
        # Interpolate radius
        # We pull from Identity (dist) to Square (dist_square)
        # Note: At corner, dist_square < dist. So r_new < dist. We pull from inside -> out.
        r_new = dist * (1.0 - factor) + dist_square * factor
        
        ratio = r_new / (dist + 0.001)
        
        # Calculate Local Offsets
        # local_map_pos = (local_x, local_y) * ratio
        # local_offset = local_map_pos - (local_x, local_y)
        
        local_off_x = local_x * (ratio - 1.0)
        local_off_y = local_y * (ratio - 1.0)
        
        # 5. Rotate Offsets back to Global Space
        # global_off_x = local_off_x * rx + local_off_y * ux
        # global_off_y = local_off_x * ry + local_off_y * uy
        
        offset_x += local_off_x * rx + local_off_y * ux
        offset_y += local_off_x * ry + local_off_y * uy

        # 6. Upscale and Apply
        full_offset_x = cv2.resize(offset_x, (w, h), interpolation=cv2.INTER_LINEAR)
        full_offset_y = cv2.resize(offset_y, (w, h), interpolation=cv2.INTER_LINEAR)
        
        map_x = self.base_map_x + full_offset_x
        map_y = self.base_map_y + full_offset_y
        
        output = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        
        return output
