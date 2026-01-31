import math
import time

import cv2
import mediapipe as mp
import numpy as np

from core.FaceMeshFactory import create_face_mesh


class FaceMask3D:
    def __init__(self):
        self.face_mesh = create_face_mesh(refine_landmarks=True)
        self.trail_canvas = None
        self.connections = mp.solutions.face_mesh.FACEMESH_TESSELATION

    def apply(self, frame):
        h, w, _ = frame.shape
        if self.trail_canvas is None:
            self.trail_canvas = np.zeros_like(frame)

        # 1. Faster fade to keep it clean (0.65)
        self.trail_canvas = cv2.addWeighted(self.trail_canvas, 0.65, self.trail_canvas, 0, 0)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        # Use time to drive the color shift
        t = time.time() * 2  # Adjust the '2' to speed up or slow down the cycle

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for connection in self.connections:
                    p1_idx, p2_idx = connection
                    p1 = face_landmarks.landmark[p1_idx]
                    p2 = face_landmarks.landmark[p2_idx]

                    pt1 = (int(p1.x * w), int(p1.y * h))
                    pt2 = (int(p2.x * w), int(p2.y * h))

                    # 2. THE GRADIENT MATH
                    # We create a shifting hue based on time and the vertical (y) position
                    # This makes the color "flow" down your face
                    hue_shift = (p1.y * 3.14) + t

                    # Generate dynamic RGB colors using sine waves
                    r = int((math.sin(hue_shift) * 127 + 128) * 0.6)  # Dimmed for slimness
                    g = int((math.sin(hue_shift + 2) * 127 + 128) * 0.6)
                    b = int((math.sin(hue_shift + 4) * 127 + 128) * 0.6)

                    cv2.line(self.trail_canvas, pt1, pt2, (b, g, r), 1, cv2.LINE_AA)

        # 3. Layering with lower opacity for face visibility
        glow = cv2.GaussianBlur(self.trail_canvas, (5, 5), 0)

        # Additive blend: 0.5 intensity for glow, 0.4 for sharp lines
        combined = cv2.addWeighted(frame, 1.0, glow, 0.5, 0)
        result = cv2.addWeighted(combined, 1.0, self.trail_canvas, 0.4, 0)

        return result
