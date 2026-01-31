import cv2
import mediapipe as mp
import numpy as np
import os

from core.FaceMeshFactory import create_face_mesh


class DevilHornsFilter:
    def __init__(self):
        self.face_mesh = create_face_mesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # Landmarks pentru poziționare și rotație
        self.landmark_top_head = 10
        self.left_temple = 234
        self.right_temple = 454
        self.left_eye = 33
        self.right_eye = 263

        self._load_horns()

    def _load_horns(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        asset_path = os.path.join(project_root, 'assets', 'devil_horns.png')
        self.horns_img = cv2.imread(asset_path, cv2.IMREAD_UNCHANGED)
        if self.horns_img is None or self.horns_img.shape[2] != 4:
            raise ValueError("devil_horns.png not found or missing alpha channel.")

    def _calculate_scale_factor(self, face_landmarks, frame_width):
        left_x = face_landmarks.landmark[self.left_temple].x * frame_width
        right_x = face_landmarks.landmark[self.right_temple].x * frame_width
        temple_distance = abs(right_x - left_x)
        scale_factor = (temple_distance * 1.2) / self.horns_img.shape[1]
        return scale_factor

    def _calculate_rotation_angle(self, face_landmarks):
        left_eye = face_landmarks.landmark[self.left_eye]
        right_eye = face_landmarks.landmark[self.right_eye]
        delta_y = right_eye.y - left_eye.y
        delta_x = right_eye.x - left_eye.x
        angle = np.arctan2(delta_y, delta_x) * (180.0 / np.pi)
        return -angle * 0.3  # mai subtil pentru realism

    def _rotate_image(self, image, angle):
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

    def _get_horns_position(self, face_landmarks, frame_width, frame_height, scaled_height):
        forehead = face_landmarks.landmark[self.landmark_top_head]
        x = int(forehead.x * frame_width)
        y = int(forehead.y * frame_height) - int(scaled_height * 0.3)
        return x, y

    def _overlay_image_alpha(self, frame, overlay_img, x, y):
        overlay_h, overlay_w = overlay_img.shape[:2]
        frame_h, frame_w = frame.shape[:2]

        x1 = x - overlay_w // 2
        y1 = y - overlay_h // 2
        x2 = x1 + overlay_w
        y2 = y1 + overlay_h

        if x1 >= frame_w or y1 >= frame_h or x2 <= 0 or y2 <= 0:
            return frame

        overlay_x1 = max(0, -x1)
        overlay_y1 = max(0, -y1)
        overlay_x2 = overlay_w - max(0, x2 - frame_w)
        overlay_y2 = overlay_h - max(0, y2 - frame_h)

        frame_x1 = max(0, x1)
        frame_y1 = max(0, y1)
        frame_x2 = min(frame_w, x2)
        frame_y2 = min(frame_h, y2)

        overlay_roi = overlay_img[overlay_y1:overlay_y2, overlay_x1:overlay_x2]
        if overlay_roi.shape[2] != 4:
            return frame

        alpha = overlay_roi[:, :, 3:4] / 255.0
        frame_roi = frame[frame_y1:frame_y2, frame_x1:frame_x2]
        blended = (frame_roi * (1 - alpha) + overlay_roi[:, :, :3] * alpha).astype(np.uint8)
        frame[frame_y1:frame_y2, frame_x1:frame_x2] = blended

        return frame

    def apply(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb)
        if not result.multi_face_landmarks:
            return frame

        h, w = frame.shape[:2]
        for face in result.multi_face_landmarks:
            scale_factor = self._calculate_scale_factor(face, w)
            new_width = int(self.horns_img.shape[1] * scale_factor)
            new_height = int(self.horns_img.shape[0] * scale_factor)

            if new_width < 10 or new_height < 10:
                continue

            horns_scaled = cv2.resize(self.horns_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            angle = self._calculate_rotation_angle(face)
            horns_rotated = self._rotate_image(horns_scaled, angle)

            horns_x, horns_y = self._get_horns_position(face, w, h, new_height)

            frame = self._overlay_image_alpha(frame, horns_rotated, horns_x, horns_y)

        return frame
