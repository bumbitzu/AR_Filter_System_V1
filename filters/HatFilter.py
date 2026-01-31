import cv2
import mediapipe as mp
import numpy as np
import os
import math

from core.FaceMeshFactory import create_face_mesh


class HatFilter:
    def __init__(self):
        self.face_mesh = create_face_mesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        
        self.forehead_top = 10
        self.left_temple = 234
        self.right_temple = 454
        self.left_eye_outer = 33
        self.right_eye_outer = 362

        self.hat_img = None
        self._load_hat()

    def _load_hat(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        asset_path = os.path.join(project_root, 'assets', 'hat.png')
        
        self.hat_img = cv2.imread(asset_path, cv2.IMREAD_UNCHANGED)
        if self.hat_img is None:
            raise FileNotFoundError(f"Nu am putut încărca imaginea: {asset_path}")
        if self.hat_img.shape[2] != 4:
            raise ValueError("Imaginea trebuie să aibă canal alpha (4 canale)")

    def _calculate_scale(self, face_landmarks, w, h):
        x1 = face_landmarks.landmark[self.left_temple].x * w
        x2 = face_landmarks.landmark[self.right_temple].x * w
        distance = abs(x2 - x1)
        return (distance * 2.0) / self.hat_img.shape[1]  # 1.4 = scalare ușor mai mare

    def _calculate_rotation(self, face_landmarks):
        p1 = face_landmarks.landmark[self.left_eye_outer]
        p2 = face_landmarks.landmark[self.right_eye_outer]
        angle = math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))
        return -angle * 0.5  # mai subtil decât 1.0

    def _rotate_image(self, img, angle):
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(img, rot_matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    def _get_hat_position(self, face_landmarks, w, h, hat_h):
        x = int(face_landmarks.landmark[self.forehead_top].x * w)
        y = int(face_landmarks.landmark[self.forehead_top].y * h) - int(hat_h * 0.45)  # poziționat mai jos
        return x, y

    def _overlay_image_alpha(self, frame, overlay, x, y):
        oh, ow = overlay.shape[:2]
        x1, y1 = x - ow // 2, y - oh // 2
        x2, y2 = x1 + ow, y1 + oh

        if x1 >= frame.shape[1] or y1 >= frame.shape[0] or x2 <= 0 or y2 <= 0:
            return frame

        # Region of interest
        fx1, fy1 = max(0, x1), max(0, y1)
        fx2, fy2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

        ox1, oy1 = fx1 - x1, fy1 - y1
        ox2, oy2 = ox1 + (fx2 - fx1), oy1 + (fy2 - fy1)

        roi = overlay[oy1:oy2, ox1:ox2]
        alpha = roi[:, :, 3:4] / 255.0
        frame_roi = frame[fy1:fy2, fx1:fx2]
        blended = (roi[:, :, :3] * alpha + frame_roi * (1 - alpha)).astype(np.uint8)

        frame[fy1:fy2, fx1:fx2] = blended
        return frame

    def apply(self, frame):
        if self.hat_img is None:
            return frame

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return frame

        for face in results.multi_face_landmarks:
            scale = self._calculate_scale(face, w, h)
            new_size = (
                int(self.hat_img.shape[1] * scale),
                int(self.hat_img.shape[0] * scale)
            )
            if new_size[0] < 10 or new_size[1] < 10:
                continue

            resized = cv2.resize(self.hat_img, new_size, interpolation=cv2.INTER_AREA)
            angle = self._calculate_rotation(face)
            rotated = self._rotate_image(resized, angle)
            x, y = self._get_hat_position(face, w, h, rotated.shape[0])
            frame = self._overlay_image_alpha(frame, rotated, x, y)

        return frame
