import cv2
import mediapipe as mp
import numpy as np

from core.FaceMeshFactory import create_face_mesh

class PermanentSmileFilter:
    def __init__(self, smile_strength=1.0):
        self.smile_strength = smile_strength  # 0.0 – 1.5 recomandat

        self.face_mesh = create_face_mesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.left_corner_idx = 61
        self.right_corner_idx = 291
        self.lower_lip_center_idx = 14

        # Parametri pentru formă și întindere
        self.arc_power = 2.7        # Cât de sus se ridică colțurile vs centru
        self.stretch_ratio = 0.72   # Cât se întind în lateral
        self.lift_ratio = 0.85      # Cât se ridică efectiv colțurile

        self.debug = False  # Activează pentru desenare ROI și puncte

    def apply(self, frame):
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return frame

        landmarks = results.multi_face_landmarks[0].landmark

        # Coord pixeli
        p1 = np.array([landmarks[self.left_corner_idx].x * w, landmarks[self.left_corner_idx].y * h])
        p2 = np.array([landmarks[self.right_corner_idx].x * w, landmarks[self.right_corner_idx].y * h])
        p_mid = (p1 + p2) / 2
        mouth_width = np.linalg.norm(p2 - p1)

        # Detectează rotația capului folosind ochii și nasul
        left_eye = np.array([landmarks[33].x * w, landmarks[33].y * h])  # Colțul ochiului stâng
        right_eye = np.array([landmarks[263].x * w, landmarks[263].y * h])  # Colțul ochiului drept
        nose_tip = np.array([landmarks[1].x * w, landmarks[1].y * h])  # Vârful nasului
        
        # Calculează unghiul de rotație al capului bazat pe linia ochilor
        eye_vector = right_eye - left_eye
        head_rotation_angle = np.arctan2(eye_vector[1], eye_vector[0])  # Unghiul în radiani

        # ROI circular în jurul gurii
        roi_radius = int(mouth_width * 1.0)  # Raza cercului ROI
        
        cx, cy = p_mid
        x0 = int(np.clip(cx - roi_radius, 0, w-1))
        x1 = int(np.clip(cx + roi_radius, 0, w-1))
        y0 = int(np.clip(cy - roi_radius, 0, h-1))
        y1 = int(np.clip(cy + roi_radius, 0, h-1))

        # Hartă identitate
        map_x = np.tile(np.arange(w, dtype=np.float32), (h, 1))
        map_y = np.tile(np.arange(h, dtype=np.float32).reshape(-1, 1), (1, w))

        # Coordonate ROI
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)

        # Calculează distanța de la centrul gurii
        dx = xx - cx
        dy = yy - cy
        distance_from_center = np.sqrt(dx*dx + dy*dy)
        
        # Mască circulară - aplică efectul doar în interiorul cercului
        circular_mask = distance_from_center <= roi_radius
        
        # Coordonate normalizate pentru cerc
        u = dx / roi_radius  # Normalizat [-1, 1] pe orizontală
        v = dy / roi_radius  # Normalizat [-1, 1] pe verticală

        # Falloff circular smooth
        sigma = 0.8
        distance_normalized = distance_from_center / roi_radius
        weight = np.exp(-(distance_normalized * distance_normalized) / (sigma * sigma))
        
        # Aplică doar în interiorul cercului
        weight = weight * circular_mask

        # Arc zâmbet – colțurile mai sus decât centrul
        corner_arc = np.clip(np.abs(u), 0.0, 1.0) ** self.arc_power

        # Calculează deplasarea de bază
        base_lift = mouth_width * self.lift_ratio * self.smile_strength * corner_arc * weight
        base_stretch = mouth_width * self.stretch_ratio * self.smile_strength * np.sign(u) * corner_arc * weight

        # Rotește deplasarea în funcție de rotația capului
        cos_angle = np.cos(head_rotation_angle)
        sin_angle = np.sin(head_rotation_angle)
        
        # Aplicarea matricei de rotație pentru vectorii de deplasare
        # Lift devine o combinație de lift și stretch rotit
        # Stretch devine o combinație de stretch și lift rotit
        rotated_lift = base_lift * cos_angle - base_stretch * sin_angle
        rotated_stretch = base_lift * sin_angle + base_stretch * cos_angle

        # Aplică deplasarea rotită
        map_y[y0:y1, x0:x1] += rotated_lift
        map_x[y0:y1, x0:x1] -= rotated_stretch

        out = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

        if self.debug:
            # Desenează cercul ROI în loc de dreptunghi
            cv2.circle(out, tuple(p_mid.astype(int)), roi_radius, (0, 255, 0), 1)
            cv2.circle(out, tuple(p1.astype(int)), 2, (255, 0, 0), -1)
            cv2.circle(out, tuple(p2.astype(int)), 2, (0, 0, 255), -1)
            cv2.circle(out, tuple(p_mid.astype(int)), 2, (0, 255, 255), -1)

        return out
