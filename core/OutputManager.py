import cv2

try:
    import pyvirtualcam
    PYVIRTUALCAM_AVAILABLE = True
except ImportError:
    PYVIRTUALCAM_AVAILABLE = False

class OutputManager:
    def __init__(self, mode="window", quality="1080p", fps=None, use_opencl=False):
        self.mode = mode
        self.vcam = None
        self._vcam_fmt = None
        self._last_frame = None
        self._show_local_preview = True
        try:
            import os
            self._show_local_preview = os.getenv("VCAM_LOCAL_PREVIEW", "true").strip().lower() in ("1", "true", "yes", "on")
        except Exception:
            pass
        if use_opencl:
            try:
                cv2.ocl.setUseOpenCL(True)
            except Exception:
                pass
        try:
            cv2.setUseOptimized(True)
        except Exception:
            pass

        if quality == "4K":
            self.width, self.height, default_fps = 3840, 2160, 30
        elif quality == "2K":
            self.width, self.height, default_fps = 2560, 1440, 25
        elif quality == "1080p":
            self.width, self.height, default_fps = 1920, 1080, 25
        elif quality == "720p":
            self.width, self.height, default_fps = 1280, 720, 25
        else:  # Default 1080p
            self.width, self.height, default_fps = 1920, 1080, 25

        self.fps = int(fps) if fps else default_fps

        if self.mode == "vcam":
            if not PYVIRTUALCAM_AVAILABLE:
                print("Error: pyvirtualcam not installed. Falling back to Window mode.")
                self.mode = "window"
            else:
                try:
                    # Prefer BGR to avoid per-frame cvtColor cost (smoother on CPU-bound systems)
                    try:
                        self._vcam_fmt = pyvirtualcam.PixelFormat.BGR
                        self.vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps, fmt=self._vcam_fmt)
                    except Exception:
                        self._vcam_fmt = None
                        self.vcam = pyvirtualcam.Camera(width=self.width, height=self.height, fps=self.fps)
                    print(f"Using Virtual Camera: {self.vcam.device}")
                except Exception as e:
                    print(f"Vcam failed to start: {e}. Falling back to Window mode.")
                    self.mode = "window"

        if self.mode == "window":
            cv2.namedWindow("AR_STREAM_WINDOW", cv2.WINDOW_NORMAL)
            print("Using Window Capture mode. Target 'AR_STREAM_WINDOW' in OBS.")

    def display(self, frame):
        if self.mode == "vcam":
            # If processing is slower than target FPS, pyvirtualcam pacing can look jittery.
            # Keep the last frame and always send something each tick.
            if self._last_frame is None:
                self._last_frame = frame

            out = frame if frame is not None else self._last_frame
            if out is None:
                return

            if self._vcam_fmt is None:
                # Virtual camera expects RGB
                out = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)

            self.vcam.send(out)
            self._last_frame = frame
            self.vcam.sleep_until_next_frame()

            # Optional: local preview window (can add overhead)
            if self._show_local_preview and frame is not None:
                cv2.imshow("Preview (Hidden from OBS)", frame)
        else:
            # Standard Window mode
            cv2.imshow("AR_STREAM_WINDOW", frame)

    def stop(self):
        if self.vcam:
            self.vcam.close()
        cv2.destroyAllWindows()
