import cv2
import numpy as np
import mediapipe as mp

class SharpChinFilter:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.base_map_x = None
        self.base_map_y = None
        
        # Filter Parameters
        self.warp_grid_shape = (40, 40) # Grid size for warp calculation
        self.shrink_strength = 3.5      # GREATLY INCREASED for V-Line
        self.chin_drop = 0.12           # Increased drop
        self.radius_rel = 0.50          # Increased coverage (up to mid-cheeks)
        self.debug_printed = False
        
    def get_landmarks(self, image):
        """Extracts landmarks from the image."""
        h, w = image.shape[:2]
        # Performance: Skip format conversion if already valid (but OpenCV uses BGR)
        results = self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0]
        points = np.array([(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark])
        return points

    def apply(self, frame, landmarks=None):
        h, w = frame.shape[:2]
        
        # 1. Get Landmarks if not provided
        if landmarks is None:
            landmarks = self.get_landmarks(frame)
            
        if landmarks is None:
            return frame
            
        if not self.debug_printed:
            print(f"🔥 Sharp Chin Active! Strength: {self.shrink_strength}, Radius: {self.radius_rel}")
            self.debug_printed = True
            
        # 2. Setup reusable base maps (lazy initialization)
        if self.base_map_x is None or self.base_map_x.shape != (h, w):
            self.base_map_x, self.base_map_y = np.meshgrid(
                np.arange(w, dtype=np.float32),
                np.arange(h, dtype=np.float32)
            )
            
        # 3. Define Low-Res Grid for Warp Calculation
        # We compute offsets on a coarse grid and resize up for performance
        gx, gy = self.warp_grid_shape
        # Ensure aspect ratio is handled if needed, but simple grid is usually fine
        # We'll use a specific resolution relative to image aspect
        grid_h, grid_w = 60, int(60 * (w / h))
        
        # Cached grid coordinates
        x_lin = np.linspace(0, w, grid_w, dtype=np.float32)
        y_lin = np.linspace(0, h, grid_h, dtype=np.float32)
        grid_x, grid_y = np.meshgrid(x_lin, y_lin)
        
        offset_x = np.zeros_like(grid_x)
        offset_y = np.zeros_like(grid_y)
        
        # 4. Filter Logic
        # Landmark indices
        CHIN_IDX = 152
        NOSE_TOP_IDX = 168 # Roughly between eyes
        
        chin_pt = landmarks[CHIN_IDX]
        nose_top_pt = landmarks[NOSE_TOP_IDX]
        
        face_height = np.linalg.norm(chin_pt - nose_top_pt)
        effect_radius = face_height * self.radius_rel
        
        # Vectorized Distance Calculation
        # dx, dy from grid points to chin center
        dx = grid_x - chin_pt[0]
        dy = grid_y - chin_pt[1]
        dist_sq = dx*dx + dy*dy
        dist = np.sqrt(dist_sq)
        
        # Mask for area of effect
        mask = dist < effect_radius
        
        # --- A. V-Line Warping (Face Slimming) ---
        # "Pucker" effect: Pull background INWARDS -> Source pixels from OUTWARDS
        # Vector points from center OUTWARDS.
        # offset = vec * strength * falloff
        
        # Normalized distance 0..1
        norm_dist = dist[mask] / effect_radius
        
        # Falloff function (Smoothstep or Cosine)
        # 1 at center, 0 at edge
        weight = (1 - norm_dist) ** 2
        
        # Apply horizontal shrinkage
        # We push `map_x` AWAY from the chin center based on horizontal distance
        # Only affect lower face (somewhat based on Y)? 
        # A simple radial pinch works well for V-line if centered on jaw/chin.
        
        # Calculate push vectors
        push_x = dx[mask] * weight * self.shrink_strength
        # push_y = dy[mask] * weight * self.shrink_strength * 0.5 # Less vertical distortion
        
        # Update offsets
        # map_x = x + offset. If offset > 0, we look right.
        # If we are to the right of face (dx > 0), we want to look further right to pull background in.
        # So offset should be positive. dx is positive. correct.
        offset_x[mask] += push_x
        
        # --- B. Pointed Chin (Elongation) ---
        # We want to stretch the chin DOWN.
        # So pixels below chin should look UP (negative y offset).
        # Pixel at chin should stay or move down?
        # To make chin "pointy", we typically pull the jaw sides in (done above)
        # And pulll the chin tip down.
        # Pulling tip down: map_y uses value from UP.
        
        # Directional warp: only affect Y, based on proximity to chin
        # Strength strongest at chin, fading out.
        
        elongation = face_height * self.chin_drop
        
        # Only pull down (offset_y < 0) to "smear" the chin downwards
        # Actually, to move chin DOWN, the pixels BELOW the chin must show the chin.
        # Pixel P (below chin) shows Chin (above P).
        # Source Y = P_y + offset. Offset must be negative.
        # Offset should be proportional to weight.
        
        offset_y[mask] -= elongation * weight
        
        # 5. Upscale Offsets and Apply Remap
        # Resize to (w, h)
        full_offset_x = cv2.resize(offset_x, (w, h), interpolation=cv2.INTER_LINEAR)
        full_offset_y = cv2.resize(offset_y, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # 6. Apply to Map
        map_x = self.base_map_x + full_offset_x
        map_y = self.base_map_y + full_offset_y
        
        # 7. Remap
        # borderMode=cv2.BORDER_REPLICATE ensures no black edges if we pull too much
        output = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        
        return output
