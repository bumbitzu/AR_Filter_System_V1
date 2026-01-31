import cv2
import numpy as np
import mediapipe as mp
import math

from core.FaceMeshFactory import create_face_mesh

class GiantForeheadFilter:
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
        
        # Tuning - EXTREME MODE
        self.warp_grid_shape = (80, 80)
        self.strength = 1.2  # Increased base strength (was 1.0)
        self.radius_mult = 3.5 # Increased radius to grab more background (was 3.0)

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
            print(f"🔥 Giant Forehead Active! EXTREME Tuning.")
            self.debug_printed = True

        # Lazy Init Maps
        if self.base_map_x is None or self.base_map_x.shape != (h, w):
            self.base_map_x, self.base_map_y = np.meshgrid(
                np.arange(w, dtype=np.float32),
                np.arange(h, dtype=np.float32)
            )

        # Create low-res grid
        grid_h, grid_w = 80, int(80 * (w / h)) 
        x_lin = np.linspace(0, w, grid_w, dtype=np.float32)
        y_lin = np.linspace(0, h, grid_h, dtype=np.float32)
        grid_x, grid_y = np.meshgrid(x_lin, y_lin)
        
        offset_x = np.zeros_like(grid_x)
        offset_y = np.zeros_like(grid_y)

        # -- Logic : Expand Upwards Relative to Face Rotation --
        
        idx_nose_bridge = 168 
        idx_hairline = 10     
        
        pt_center = landmarks[idx_nose_bridge] 
        pt_top = landmarks[idx_hairline]
        
        center_x, center_y = pt_center
        
        # 1. Calculate Face Coordinate System
        vec_up = pt_top - pt_center
        face_size = np.linalg.norm(vec_up)
        
        if face_size > 0:
            ux = vec_up[0] / face_size
            uy = vec_up[1] / face_size
        else:
            ux, uy = 0, -1
            
        rx, ry = -uy, ux
        
        # 2. Project Grid to Local Face Coordinates
        dx = grid_x - center_x
        dy = grid_y - center_y
        
        local_x = dx * rx + dy * ry
        local_y = dx * ux + dy * uy
        
        dist = np.sqrt(local_x*local_x + local_y*local_y)
        
        # 3. Calculate Weights
        radius = face_size * self.radius_mult
        norm_dist = dist / radius
        weight_radial = np.clip(1.0 - norm_dist, 0.0, 1.0)
        weight_radial = weight_radial ** 2 
        
        v_progress = local_y / face_size
        
        # Keep the high start point (0.55) to protect eyebrows
        weight_dir = np.clip((v_progress - 0.70) / 0.5, 0.0, 1.0)
        weight_dir = weight_dir * weight_dir * (3 - 2 * weight_dir)
        
        final_weight = weight_radial * weight_dir
        
        mask = final_weight > 0.01
        
        if np.any(mask):
            # 4. Calculate Displacement in Local Space
            # STRONGER PARAMETERS
            sx = self.strength * 0.5  # REDUCED from 1.1 to 0.1 for narrower forehead
            sy = self.strength * 2.5  # Kept high for vertical height
            
            pull_local_x = -local_x[mask] * final_weight[mask] * sx
            pull_local_y = -local_y[mask] * final_weight[mask] * sy
            
            # 5. Rotate Pull Vector back to Global Space
            pull_global_x = pull_local_x * rx + pull_local_y * ux
            pull_global_y = pull_local_x * ry + pull_local_y * uy
            
            offset_x[mask] += pull_global_x
            offset_y[mask] += pull_global_y

            # 6. Anti-Cloning Clamping (Rotation Aware)
            src_x = grid_x[mask] + offset_x[mask]
            src_y = grid_y[mask] + offset_y[mask]
            
            src_dx = src_x - center_x
            src_dy = src_y - center_y
            src_local_y = src_dx * ux + src_dy * uy
            
            limit_val = face_size * 0.48
            
            violation = limit_val - src_local_y
            violation = np.maximum(violation, 0)
            
            corr_x = violation * ux
            corr_y = violation * uy
            
            offset_x[mask] += corr_x
            offset_y[mask] += corr_y
            
        # 7. Upscale and Apply
        full_offset_x = cv2.resize(offset_x, (w, h), interpolation=cv2.INTER_LINEAR)
        full_offset_y = cv2.resize(offset_y, (w, h), interpolation=cv2.INTER_LINEAR)
        
        map_x = self.base_map_x + full_offset_x
        map_y = self.base_map_y + full_offset_y
        
        output = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        
        return output
