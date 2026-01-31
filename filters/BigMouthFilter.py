import cv2
import mediapipe as mp
import numpy as np
import math

from core.FaceMeshFactory import create_face_mesh

class BigMouthFilter:
    def __init__(self):
        self.face_mesh = create_face_mesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        
        # Parameters for Big Mouth Effect
        self.radius_factor = 0.6  # Increased from 0.4 to covering more cheek/chin
        self.strength = 1.6       # Adjusted strength for new radius

    def get_landmarks(self, image):
        """Extracts 468 landmarks from the image."""
        h, w = image.shape[:2]
        results = self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if not results.multi_face_landmarks:
            return None
        
        landmarks = results.multi_face_landmarks[0]
        points = []
        for lm in landmarks.landmark:
            # Denormalize coordinates
            points.append((int(lm.x * w), int(lm.y * h)))
            
        return np.array(points, dtype=np.int32)

    def get_delaunay_triangles(self, rect, points):
        """
        Computes Delaunay Triangulation using cv2.Subdiv2D.
        """
        subdiv = cv2.Subdiv2D(rect)
        
        points_map = {} 
        for i, p in enumerate(points):
            pt = (float(p[0]), float(p[1]))
            if pt not in points_map:
                points_map[pt] = i
                subdiv.insert(pt)
            
        triangle_list = subdiv.getTriangleList()
        
        triangles = []
        for t in triangle_list:
            pts = [(t[0], t[1]), (t[2], t[3]), (t[4], t[5])]
            
            indices = []
            for pt in pts:
                if pt in points_map:
                    indices.append(points_map[pt])
            
            if len(indices) == 3:
                triangles.append(indices)
                
        return triangles

    def warp_triangles(self, img, src_points, dst_points, triangles):
        """
        Warps texture from source to destination triangles.
        Optimized to avoid dark seams by overwriting destination.
        """
        output = img.copy()
        
        for tri_indices in triangles:
            src_tri = src_points[tri_indices]
            dst_tri = dst_points[tri_indices]
            
            # Optimization: Skip static triangles
            if np.array_equal(src_tri, dst_tri):
                continue

            # Get bounding boxes
            r_src = cv2.boundingRect(np.float32([src_tri]))
            r_dst = cv2.boundingRect(np.float32([dst_tri]))
            
            x_src, y_src, w_src, h_src = r_src
            x_dst, y_dst, w_dst, h_dst = r_dst
            
            if w_src == 0 or h_src == 0 or w_dst == 0 or h_dst == 0:
                continue

            # Crop source
            src_rect_img = img[y_src:y_src+h_src, x_src:x_src+w_src]
            if src_rect_img.size == 0: continue

            # Mask for destination triangle (local coords)
            dst_tri_local = []
            for i in range(3):
                dst_tri_local.append((dst_tri[i][0] - x_dst, dst_tri[i][1] - y_dst))
            
            dst_tri_local = np.array(dst_tri_local, dtype=np.int32)
            
            # Create mask
            mask = np.zeros((h_dst, w_dst), dtype=np.uint8)
            cv2.fillConvexPoly(mask, dst_tri_local, 255)
            
            # Affine Transform
            src_tri_local = np.float32([(p[0] - x_src, p[1] - y_src) for p in src_tri])
            dst_tri_local_float = np.float32(dst_tri_local)
            
            M = cv2.getAffineTransform(src_tri_local, dst_tri_local_float)
            
            # Warp
            warped_patch = cv2.warpAffine(src_rect_img, M, (w_dst, h_dst), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
            
            # Paste directly using mask logic logic
            # To avoid dark halos: We rely on the fact that we are expanding the face.
            # We simply overwrite the destination pixels where the mask is active.
            
            dest_region = output[y_dst:y_dst+h_dst, x_dst:x_dst+w_dst]
            
            # Safety check for size match
            if dest_region.shape != warped_patch.shape:
                continue
                
            # Use boolean indexing for speed and no blending artifacts
            # This replaces pixels in `dest_region` with `warped_patch` where `mask` is 255
            dest_region[mask == 255] = warped_patch[mask == 255]
            
        return output

    def apply(self, frame):
        h, w = frame.shape[:2]
        src_points = self.get_landmarks(frame)
        
        if src_points is None:
            return frame
            
        # 1. Identify Mouth Center
        # Use a more robust center point (average of lips + chin/nose influence)
        # Lips: 13 (upper), 14 (lower), 61 (left), 291 (right)
        mouth_pts_indices = [13, 14, 61, 291] 
        mouth_center = np.mean(src_points[mouth_pts_indices], axis=0)
        
        # 2. Radius and Falloff
        face_top = src_points[10]
        face_bottom = src_points[152]
        face_height = np.linalg.norm(face_top - face_bottom)
        
        radius = face_height * self.radius_factor
        
        # 3. Compute Destination Points
        dst_points = src_points.copy()
        
        for i, point in enumerate(src_points):
            vec = point - mouth_center
            dist = np.linalg.norm(vec)
            
            if dist < radius:
                # Smooth falloff using cosine or squared distance for continuity
                # Normalized distance (0 at center, 1 at edge)
                norm_dist = dist / radius
                
                # Smooth deformation function: (1 - x)^2 or (1 + cos(x*pi))/2
                # Let's use squared falloff for eased transition to 0
                alpha = (1.0 - norm_dist) ** 2
                
                # Apply distortion
                # Move AWAY from center (Blow up / Fish Eye)
                dst_points[i] = point + vec * alpha * self.strength
        
        # 4. Triangulation & Rendering
        rect = (0, 0, w, h)
        triangles = self.get_delaunay_triangles(rect, src_points)
        output = self.warp_triangles(frame, src_points, dst_points, triangles)
        
        return output
