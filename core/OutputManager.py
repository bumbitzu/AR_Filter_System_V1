import cv2

try:
    import pyvirtualcam
    PYVIRTUALCAM_AVAILABLE = True
except ImportError:
    PYVIRTUALCAM_AVAILABLE = False

class OutputManager:
    def __init__(self, mode="window", quality="1080p"):
        self.mode = mode
        self.vcam = None
        if quality == "4K":
            self.width, self.height, self.fps = 3840, 2160, 30
        elif quality == "720p":
            self.width, self.height, self.fps = 1280, 720, 60
        else:  # Default 1080p
            self.width, self.height, self.fps = 1920, 1080, 60

        if self.mode == "vcam":
            if not PYVIRTUALCAM_AVAILABLE:
                print("Error: pyvirtualcam not installed. Falling back to Window mode.")
                self.mode = "window"
            else:
                try:
                    # Initialize the virtual camera
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
            # Virtual camera expects RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.vcam.send(frame_rgb)
            self.vcam.sleep_until_next_frame()

            # Optional: Still show a local preview window so you can see yourself
            cv2.imshow("Preview (Hidden from OBS)", frame)
        else:
            # Standard Window mode
            cv2.imshow("AR_STREAM_WINDOW", frame)

    def stop(self):
        if self.vcam:
            self.vcam.close()
        cv2.destroyAllWindows()
