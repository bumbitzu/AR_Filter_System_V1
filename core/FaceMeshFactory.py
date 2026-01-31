import os
import time
from dataclasses import dataclass
from typing import List, Optional

import requests
import cv2


_FACEMESH_CACHE = {}


# Lightweight compatibility objects so existing filters can keep using:
# results.multi_face_landmarks -> [face_landmarks]
# face_landmarks.landmark -> [lm]
# lm.x / lm.y / lm.z


@dataclass
class _Landmark:
    x: float
    y: float
    z: float = 0.0


@dataclass
class _FaceLandmarks:
    landmark: List[_Landmark]


@dataclass
class _FaceMeshResults:
    multi_face_landmarks: Optional[List[_FaceLandmarks]]


def _env_str(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return v.strip() if isinstance(v, str) and v.strip() else default


def _env_bool(name: str, default: str = "false") -> bool:
    v = _env_str(name, default)
    return v.lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    try:
        return int(str(v).strip())
    except Exception:
        return default


def _maybe_downscale_rgb(rgb_frame):
    """Downscale input frame for faster landmark inference.

    Landmarker outputs normalized coordinates, so downscaling does not break filters.

    Env:
      - FACEMESH_MAX_WIDTH (default 0 = disabled)
      - FACEMESH_MAX_HEIGHT (default 0 = disabled)
    """
    max_w = _env_int("FACEMESH_MAX_WIDTH", 0)
    max_h = _env_int("FACEMESH_MAX_HEIGHT", 0)

    if max_w <= 0 and max_h <= 0:
        return rgb_frame

    h, w = rgb_frame.shape[:2]
    if (max_w > 0 and w > max_w) or (max_h > 0 and h > max_h):
        if max_w <= 0:
            scale = max_h / float(h)
        elif max_h <= 0:
            scale = max_w / float(w)
        else:
            scale = min(max_w / float(w), max_h / float(h))

        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        return cv2.resize(rgb_frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

    return rgb_frame


def _ensure_face_landmarker_task(model_path: str) -> str:
    if os.path.exists(model_path):
        return model_path

    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # Official MediaPipe model bundles are hosted on Google Cloud Storage.
    # We try a small set of known URLs; if they change, user can download manually.
    urls = [
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task",
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float32/latest/face_landmarker.task",
    ]

    last_err = None
    for url in urls:
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            with open(model_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            return model_path
        except Exception as e:
            last_err = e

    raise RuntimeError(
        "Could not download MediaPipe FaceLandmarker model bundle. "
        f"Tried: {urls}. Last error: {last_err}. "
        f"Download it manually and place it at: {model_path}"
    )


class _SolutionsFaceMeshWrapper:
    def __init__(self, refine_landmarks: bool, min_detection_confidence: float, min_tracking_confidence: float):
        import mediapipe as mp

        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, rgb_frame):
        rgb_frame = _maybe_downscale_rgb(rgb_frame)
        return self._face_mesh.process(rgb_frame)


class _TasksFaceLandmarkerWrapper:
    def __init__(
        self,
        model_path: str,
        prefer_gpu: bool,
        num_faces: int,
        min_detection_confidence: float,
        min_tracking_confidence: float,
    ):
        import mediapipe as mp
        from mediapipe.tasks.python import vision
        from mediapipe.tasks.python.core import base_options as base_options_mod

        model_path = _ensure_face_landmarker_task(model_path)

        delegate = base_options_mod.BaseOptions.Delegate.GPU if prefer_gpu else base_options_mod.BaseOptions.Delegate.CPU
        base_options = base_options_mod.BaseOptions(model_asset_path=model_path, delegate=delegate)

        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_faces=num_faces,
            min_face_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )

        self._mp = mp
        self._vision = vision
        self._landmarker = vision.FaceLandmarker.create_from_options(options)

    def process(self, rgb_frame):
        rgb_frame = _maybe_downscale_rgb(rgb_frame)
        mp_image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb_frame)
        ts_ms = int(time.time() * 1000)
        result = self._landmarker.detect_for_video(mp_image, ts_ms)

        if not result.face_landmarks:
            return _FaceMeshResults(multi_face_landmarks=None)

        faces: List[_FaceLandmarks] = []
        for face in result.face_landmarks:
            faces.append(
                _FaceLandmarks(
                    landmark=[_Landmark(lm.x, lm.y, getattr(lm, "z", 0.0)) for lm in face]
                )
            )

        return _FaceMeshResults(multi_face_landmarks=faces)


def create_face_mesh(
    refine_landmarks: bool = True,
    min_detection_confidence: float = 0.5,
    min_tracking_confidence: float = 0.5,
):
    """Factory returning an object with .process(rgb_frame) and results.multi_face_landmarks.

    Control via env:
      - FACEMESH_BACKEND: tasks | solutions  (default: tasks)
      - FACEMESH_GPU: true/false (default: true)
      - FACEMESH_MODEL_PATH: path to face_landmarker.task (default: assets/models/face_landmarker.task)

    Notes:
      - On Windows, GPU delegate support depends on your drivers/runtime. If GPU init fails,
        we automatically fall back to CPU.
    """

    backend = _env_str("FACEMESH_BACKEND", "tasks").lower()
    prefer_gpu = _env_bool("FACEMESH_GPU", "true")
    model_path = _env_str("FACEMESH_MODEL_PATH", os.path.join("assets", "models", "face_landmarker.task"))

    cache_key = (backend, prefer_gpu, os.path.abspath(model_path))
    cached = _FACEMESH_CACHE.get(cache_key)
    if cached is not None:
        return cached

    if backend == "tasks":
        try:
            # MediaPipe Tasks FaceLandmarker always outputs 478 landmarks (FaceMesh-V2).
            # This matches existing filters that index landmarks like 10/234/454/468 etc.
            inst = _TasksFaceLandmarkerWrapper(
                model_path=model_path,
                prefer_gpu=prefer_gpu,
                num_faces=1,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
            )
            _FACEMESH_CACHE[cache_key] = inst
            return inst
        except Exception:
            # Fallback to CPU Tasks, then Solutions.
            try:
                inst = _TasksFaceLandmarkerWrapper(
                    model_path=model_path,
                    prefer_gpu=False,
                    num_faces=1,
                    min_detection_confidence=min_detection_confidence,
                    min_tracking_confidence=min_tracking_confidence,
                )
                # Cache under both keys so we don't retry GPU init every time.
                _FACEMESH_CACHE[(backend, False, os.path.abspath(model_path))] = inst
                _FACEMESH_CACHE[cache_key] = inst
                return inst
            except Exception:
                inst = _SolutionsFaceMeshWrapper(
                    refine_landmarks=refine_landmarks,
                    min_detection_confidence=min_detection_confidence,
                    min_tracking_confidence=min_tracking_confidence,
                )
                _FACEMESH_CACHE[("solutions", False, "")] = inst
                _FACEMESH_CACHE[cache_key] = inst
                return inst

    inst = _SolutionsFaceMeshWrapper(
        refine_landmarks=refine_landmarks,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )
    _FACEMESH_CACHE[("solutions", False, "")] = inst
    return inst
