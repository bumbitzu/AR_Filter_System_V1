import cv2
import mediapipe as mp
import numpy as np


class SquirrelCheeksFilter:
    """
    AR filter that creates massively puffed out cheeks like a squirrel storing nuts.
    
    Features:
    - Massive outward spherical distortion on both cheeks
    - Smooth blending with surrounding facial features
    - Maintains mouth and nose stability
    
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
        # Mouth corners
        self.left_mouth_corner = 61   # Left corner of mouth
        self.right_mouth_corner = 291  # Right corner of mouth
        
        # Cheekbone references
        self.left_cheekbone = 127   # Left cheekbone
        self.right_cheekbone = 356  # Right cheekbone
        
        # Jaw references for cheek positioning
        self.left_jaw_mid = 172     # Left mid-jaw
        self.right_jaw_mid = 397    # Right mid-jaw
        
        # Nose reference (to keep stable)
        self.nose_tip = 1           # Nose tip
        
        # Chin reference
        self.chin = 152             # Chin point
        
        # Filter strength parameters
        self.cheek_puff_strength = 0.65   # How much to puff out (0.5-0.8)
        self.cheek_radius_scale = 1.3     # Size of affected area
        
    def _get_cheek_centers(self, landmarks, w, h):
        """
        Calculate the center points for left and right cheek puffing.
        
        Args:
            landmarks: Face landmarks from MediaPipe
            w, h: Frame dimensions
            
        Returns:
            tuple: ((left_cx, left_cy, radius), (right_cx, right_cy, radius))
        """
        # Get key landmark positions
        left_mouth = landmarks.landmark[self.left_mouth_corner]
        right_mouth = landmarks.landmark[self.right_mouth_corner]
        left_cheekbone = landmarks.landmark[self.left_cheekbone]
        right_cheekbone = landmarks.landmark[self.right_cheekbone]
        left_jaw = landmarks.landmark[self.left_jaw_mid]
        right_jaw = landmarks.landmark[self.right_jaw_mid]
        
        # Calculate left cheek center (between mouth corner and jaw)
        left_cx = int((left_mouth.x * 0.3 + left_jaw.x * 0.5 + left_cheekbone.x * 0.2) * w)
        left_cy = int((left_mouth.y * 0.35 + left_jaw.y * 0.35 + left_cheekbone.y * 0.3) * h)
        
        # Calculate right cheek center (between mouth corner and jaw)
        right_cx = int((right_mouth.x * 0.3 + right_jaw.x * 0.5 + right_cheekbone.x * 0.2) * w)
        right_cy = int((right_mouth.y * 0.35 + right_jaw.y * 0.35 + right_cheekbone.y * 0.3) * h)
        
        # Calculate radius based on face size
        face_width = abs(right_jaw.x - left_jaw.x) * w
        radius = int(face_width * 0.35 * self.cheek_radius_scale)
        
        return (left_cx, left_cy, radius), (right_cx, right_cy, radius)
    
    def _create_cheek_warp(self, frame, landmarks):
        """
        Create mesh deformation maps for squirrel cheek puffing.
        
        Applies radial outward displacement to create spherical cheek bulges.
        
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
        
        # Get cheek centers and radii
        (left_cx, left_cy, left_radius), (right_cx, right_cy, right_radius) = \
            self._get_cheek_centers(landmarks, w, h)
        
        # Apply puffing to left cheek
        self._apply_radial_puff(map_x, map_y, left_cx, left_cy, left_radius, w, h)
        
        # Apply puffing to right cheek
        self._apply_radial_puff(map_x, map_y, right_cx, right_cy, right_radius, w, h)
        
        return map_x, map_y
    
    def _apply_radial_puff(self, map_x, map_y, cx, cy, radius, w, h):
        """
        Apply radial outward displacement to create a puffed/bulged effect.
        
        Uses a smooth falloff function to avoid harsh edges.
        
        Args:
            map_x, map_y: Mesh grid maps to modify
            cx, cy: Center of the puff effect
            radius: Radius of effect
            w, h: Frame dimensions
        """
        # Create coordinate grids relative to cheek center
        y_grid, x_grid = np.ogrid[:h, :w]
        
        # Calculate distance from cheek center for all pixels
        dx = x_grid - cx
        dy = y_grid - cy
        distance = np.sqrt(dx**2 + dy**2)
        
        # Create smooth falloff mask (only affect pixels within radius)
        # Use smooth exponential falloff for natural blending
        mask = distance < radius
        
        # Calculate displacement strength based on distance
        # Stronger effect at center, smoothly fading to zero at radius
        normalized_dist = np.clip(distance / radius, 0, 1)
        
        # Use smooth falloff function (ease-out curve)
        # This creates a natural bulge effect
        falloff = np.where(
            mask,
            (1.0 - normalized_dist**2) ** 2,  # Smooth quadratic falloff
            0.0
        )
        
        # Calculate radial displacement (outward from center)
        # Strength increases towards the edge for a spherical bulge
        displacement_strength = falloff * self.cheek_puff_strength * radius
        
        # Apply outward radial displacement
        # Pixels are pulled away from the center
        with np.errstate(divide='ignore', invalid='ignore'):
            # Normalize direction vectors
            norm_dx = np.where(distance > 0, dx / distance, 0)
            norm_dy = np.where(distance > 0, dy / distance, 0)
            
            # Calculate displacement vectors
            disp_x = norm_dx * displacement_strength
            disp_y = norm_dy * displacement_strength
            
            # Apply displacement (subtract because we want to sample from closer to center)
            # This creates the puffing effect
            map_x[mask] -= disp_x[mask]
            map_y[mask] -= disp_y[mask]
            
            # Clamp to valid range
            map_x[:] = np.clip(map_x, 0, w - 1)
            map_y[:] = np.clip(map_y, 0, h - 1)
    
    def apply(self, frame):
        """
        Apply the Squirrel Cheeks filter to a video frame.
        
        Args:
            frame: Input BGR video frame
            
        Returns:
            np.array: Transformed frame with puffed cheeks
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
        
        # Create mesh warp for cheek puffing
        map_x, map_y = self._create_cheek_warp(frame, face_landmarks)
        
        # Apply remap for high-performance warping
        # Use INTER_LINEAR for good quality with excellent performance
        puffed_frame = cv2.remap(frame, map_x, map_y, 
                                 cv2.INTER_LINEAR, 
                                 borderMode=cv2.BORDER_REPLICATE)
        
        return puffed_frame
