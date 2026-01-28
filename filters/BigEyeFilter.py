import math

import cv2
import mediapipe as mp
import numpy as np

class BigEyeFilter:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)
        # Landmarks for left eye center (468) and right eye center (473)
        self.eye_indices = [468, 473]

    def _smooth_skin(self, frame, results):
        if not results.multi_face_landmarks:
            return frame

        # 1. Create a strong blur of the whole image
        # Bilateral is slow but beautiful; we use a faster approximation here:
        # Gaussian blur + a high-pass filter trick
        smooth = cv2.bilateralFilter(frame, 5, 75, 75)

        # 2. Create a mask for the skin area only
        h, w = frame.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)

        # This list of landmarks outlines the face "oval"
        face_oval = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                     397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                     172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

        for face_landmarks in results.multi_face_landmarks:
            points = []
            for idx in face_oval:
                lm = face_landmarks.landmark[idx]
                points.append([int(lm.x * w), int(lm.y * h)])

            # Fill the face oval with white on the mask
            cv2.fillPoly(mask, [np.array(points)], 255)

            # Subtract the eyes and mouth from the mask so they stay sharp
            for feature in [self.mp_face_mesh.FACEMESH_LEFT_EYE,
                            self.mp_face_mesh.FACEMESH_RIGHT_EYE,
                            self.mp_face_mesh.FACEMESH_LIPS]:
                feature_pts = []
                for connection in feature:
                    lm = face_landmarks.landmark[connection[0]]
                    feature_pts.append([int(lm.x * w), int(lm.y * h)])
                cv2.fillPoly(mask, [np.array(feature_pts)], 0)

        # 3. Blend the smooth skin with the original
        # This makes it look realistic rather than "plastic"
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
        output = (frame * (1 - mask_3ch) + smooth * mask_3ch).astype(np.uint8)
        return output

    def apply(self, frame, strength=0.35, radius=70):
        h, w = frame.shape[:2]
        rgb_frame = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), dtype=np.uint8)
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return frame

        # FIRST: Smooth the skin
        frame = self._smooth_skin(frame, results)

        # SECOND: Do the Big Eyes Remap
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        map_x = map_x.astype(np.float32)
        map_y = map_y.astype(np.float32)

        for face_landmarks in results.multi_face_landmarks:
            for idx in [468, 473]:
                lm = face_landmarks.landmark[idx]
                cx, cy = lm.x * w, lm.y * h
                dx, dy = map_x - cx, map_y - cy
                distance = np.sqrt(dx ** 2 + dy ** 2)
                mask = distance < radius
                rescale = np.power(distance / radius, strength)
                map_x[mask] = cx + dx[mask] * rescale[mask]
                map_y[mask] = cy + dy[mask] * rescale[mask]

        final_map_x = np.ascontiguousarray(map_x, dtype=np.float32)
        final_map_y = np.ascontiguousarray(map_y, dtype=np.float32)

        return cv2.remap(frame, final_map_x, final_map_y, cv2.INTER_LINEAR)
