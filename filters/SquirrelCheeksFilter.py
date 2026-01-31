import cv2
import mediapipe as mp
import numpy as np

from core.FaceMeshFactory import create_face_mesh


class SquirrelCheeksFilter:
    """
    Squirrel Cheeks (optimized)
    - No full-frame meshgrid/remap
    - Warps ONLY small ROIs around each cheek
    - Smooth falloff, clean borders
    - Optional temporal smoothing (anti-jitter)
    """

    def __init__(self):
        self.face_mesh = create_face_mesh(
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        # Landmarks (MediaPipe FaceMesh)
        self.left_mouth_corner = 61
        self.right_mouth_corner = 291
        self.left_cheekbone = 127
        self.right_cheekbone = 356
        self.left_jaw_mid = 172
        self.right_jaw_mid = 397
        self.nose_tip = 1

        # Effect tuning
        self.strength = 1.10          # overall intensity (0.7..1.6)
        self.radius_scale = 1.20      # cheek ROI size (0.9..1.6)
        self.x_boost = 1.35           # bulge more sideways
        self.y_boost = 1.10           # bulge less vertical

        # Smoothing (anti-jitter)
        self.smooth = True
        self.smooth_alpha = 0.65      # higher = smoother, more laggy (0.4..0.8)
        self._prev_left = None        # (cx, cy, rx, ry)
        self._prev_right = None

    @staticmethod
    def _smoothstep(x):
        return x * x * (3.0 - 2.0 * x)

    def _get_pts(self, frame):
        h, w = frame.shape[:2]
        res = self.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not res.multi_face_landmarks:
            return None

        lm = res.multi_face_landmarks[0].landmark
        pts = np.array([(int(p.x * w), int(p.y * h)) for p in lm], dtype=np.int32)
        return pts

    def _cheek_params(self, pts):
        # key points
        lmL = pts[self.left_mouth_corner]
        lmR = pts[self.right_mouth_corner]
        cbL = pts[self.left_cheekbone]
        cbR = pts[self.right_cheekbone]
        jwL = pts[self.left_jaw_mid]
        jwR = pts[self.right_jaw_mid]
        nose = pts[self.nose_tip]

        # centers (weighted blend: mouth/jaw/cheekbone + stabilize with nose)
        left_c = (lmL * 0.35 + jwL * 0.45 + cbL * 0.20).astype(np.float32)
        right_c = (lmR * 0.35 + jwR * 0.45 + cbR * 0.20).astype(np.float32)

        # slight pull towards nose so it doesn't drift outward too much
        left_c = (left_c * 0.92 + nose * 0.08).astype(np.float32)
        right_c = (right_c * 0.92 + nose * 0.08).astype(np.float32)

        # radius from face width
        face_w = np.linalg.norm(jwR - jwL)
        base = face_w * 0.22 * self.radius_scale

        # ellipse radii (more wide than tall for cheeks)
        rx = max(18.0, base * 1.25)
        ry = max(18.0, base * 1.00)

        return left_c, right_c, rx, ry

    def _ema(self, prev, curr):
        # prev/curr: (cx,cy,rx,ry) float
        a = self.smooth_alpha
        return (
            prev[0] * a + curr[0] * (1 - a),
            prev[1] * a + curr[1] * (1 - a),
            prev[2] * a + curr[2] * (1 - a),
            prev[3] * a + curr[3] * (1 - a),
        )

    def _bulge_roi(self, frame, center, rx, ry):
        """
        Bulge inside an ellipse ROI using inverse mapping (correct for cv2.remap).
        """
        h, w = frame.shape[:2]
        cx, cy = float(center[0]), float(center[1])

        # ROI bounds (a bit larger than ellipse, to keep edges clean)
        roi_mul = 1.35
        rx_roi = int(rx * roi_mul)
        ry_roi = int(ry * roi_mul)

        x0 = max(int(cx) - rx_roi, 0)
        y0 = max(int(cy) - ry_roi, 0)
        x1 = min(int(cx) + rx_roi, w)
        y1 = min(int(cy) + ry_roi, h)

        roi = frame[y0:y1, x0:x1]
        if roi.size == 0:
            return frame

        hh, ww = roi.shape[:2]
        yy, xx = np.mgrid[0:hh, 0:ww]

        X = xx.astype(np.float32) + x0
        Y = yy.astype(np.float32) + y0

        # normalized ellipse coords
        dx = (X - cx) / max(rx, 1.0)
        dy = (Y - cy) / max(ry, 1.0)
        dist = dx * dx + dy * dy

        mask = dist < 1.0
        if not np.any(mask):
            return frame

        # smooth falloff (strong center, zero at edge)
        fall = np.clip(1.0 - dist, 0.0, 1.0)
        fall = self._smoothstep(fall) * self.strength

        # anisotropic bulge
        scale_x = 1.0 + fall * self.x_boost
        scale_y = 1.0 + fall * self.y_boost

        # IMPORTANT: inverse mapping for remap (sample closer to center => bulge)
        src_X = cx + (X - cx) / scale_x
        src_Y = cy + (Y - cy) / scale_y

        map_x = np.clip(src_X - x0, 0, ww - 1).astype(np.float32)
        map_y = np.clip(src_Y - y0, 0, hh - 1).astype(np.float32)

        warped = cv2.remap(
            roi,
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101
        )

        out = frame.copy()
        out_roi = out[y0:y1, x0:x1]
        out_roi[mask] = warped[mask]
        return out

    def apply(self, frame):
        pts = self._get_pts(frame)
        if pts is None:
            return frame

        left_c, right_c, rx, ry = self._cheek_params(pts)

        # optional smoothing
        left_pack = (left_c[0], left_c[1], rx, ry)
        right_pack = (right_c[0], right_c[1], rx, ry)

        if self.smooth:
            if self._prev_left is None:
                self._prev_left = left_pack
                self._prev_right = right_pack
            else:
                self._prev_left = self._ema(self._prev_left, left_pack)
                self._prev_right = self._ema(self._prev_right, right_pack)

            lx, ly, lrx, lry = self._prev_left
            rx_, ry_, rrx, rry = self._prev_right
            left_c = np.array([lx, ly], dtype=np.float32)
            right_c = np.array([rx_, ry_], dtype=np.float32)
            rx, ry = float(lrx), float(lry)
            rrx, rry = float(rrx), float(rry)
        else:
            rrx, rry = rx, ry

        out = self._bulge_roi(frame, left_c, rx, ry)
        out = self._bulge_roi(out, right_c, rrx, rry)
        return out
