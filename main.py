import os
import sys

os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["OPENCV_LOG_LEVEL"] = "OFF"

try:
    null_fd = os.open(os.devnull, os.O_WRONLY)
    old_stderr_fd = os.dup(sys.stderr.fileno())
    os.dup2(null_fd, sys.stderr.fileno())
except Exception:
    pass

import cv2
import time
import threading
import requests
from dotenv import load_dotenv
from core.OutputManager import OutputManager
from core.ChaturbateListener import ChaturbateListener
from core.StripchatListener import StripchatListener
from core.CamsodaListener import CamsodaListener
from filters.FaceMask3DFilter import FaceMask3D
from filters.BigEyeFilter import BigEyeFilter
from filters.RainSparkleFilter import RainSparkleFilter
from filters.RabbitEarsFilter import RabbitEarsFilter
from filters.AlienFaceFilter import AlienFaceFilter
from filters.SquirrelCheeksFilter import SquirrelCheeksFilter
from filters.BigMouthFilter import BigMouthFilter
from filters.PinocchioFilter import PinocchioFilter
from filters.SharpChinFilter import SharpChinFilter
from filters.GiantForeheadFilter import GiantForeheadFilter
from filters.CubeHeadFilter import CubeHeadFilter
from collections import deque





try:
    os.dup2(old_stderr_fd, sys.stderr.fileno())
    os.close(null_fd)
except Exception:
    pass

class CameraFiltersAutomation:
    def __init__(self, output_mode="window", chaturbate_url=None, stripchat_url=None, camsoda_url=None, quality="2K"):
        if quality == "4K":
            self.width, self.height, self.fps = 3840, 2160, 30
        elif quality == "2K":
            self.width, self.height, self.fps = 2560, 1440, 60
        elif quality == "1080p":
            self.width, self.height, self.fps = 1920, 1080, 60
        elif quality == "720p":
            self.width, self.height, self.fps = 1280, 720, 60
        else:  # Default 2K
            self.width, self.height, self.fps = 2560, 1440, 60

        selected_index = self.select_camera()
        self.cap = cv2.VideoCapture(selected_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.output = OutputManager(mode=output_mode, quality=quality)

        self.queue = deque()  # Stores: {"name": "Sparkle", "user": "UserA", "duration": 30, "instance": obj}
        self.current_filter = None
        self.filter_end_time = 0

        # Define Tiers: (Min_Tokens, Max_Tokens, Filter_Key, Duration)
        # Modifică în __init__
        self.fixed_tips = [
            # (Min, Max, Nume, Instanță, Durată)
            (119, 128, 'Squirrel Cheeks', SquirrelCheeksFilter(), 10),
            (129, 138, 'Alien Face', AlienFaceFilter(), 10),
            (139, 148, 'Big Mouth', BigMouthFilter(), 10),
            (149, 158, 'Pinocchio', PinocchioFilter(), 10),
            (159, 168, 'Sharp Chin', SharpChinFilter(), 10),
            (169, 178, 'Giant Forehead', GiantForeheadFilter(), 10),
            (179, 188, 'Cube Head', CubeHeadFilter(), 10),
        ]

            # 189:  ('Big Eyes', BigEyeFilter(), 20),
            # 199:  ('Rabbit Ears', RabbitEarsFilter(), 15),
            # 209: ('Cyber Mask', FaceMask3D(), 30)

        





        # Initialize platform listeners
        self.listeners = []
        
        # Start Chaturbate listener
        if chaturbate_url:
            chaturbate_listener = ChaturbateListener(chaturbate_url, self.process_tip)
            chaturbate_listener.start()
            self.listeners.append(chaturbate_listener)
        
        # Start Stripchat listener
        if stripchat_url:
            stripchat_listener = StripchatListener(stripchat_url, self.process_tip)
            stripchat_listener.start()
            self.listeners.append(stripchat_listener)
        
        # Start Camsoda listener
        if camsoda_url:
            camsoda_listener = CamsodaListener(camsoda_url, self.process_tip)
            camsoda_listener.start()
            self.listeners.append(camsoda_listener)
        
        if not self.listeners:
            print("⚠️ No platform APIs configured. Use keyboard shortcuts for testing.")
        
        # # Load static menu overlay (one-time initialization for performance)
        # menu_path = os.path.join("assets", "menu_overlay.png")
        # self.menu_image = cv2.imread(menu_path, cv2.IMREAD_UNCHANGED)  # Load with alpha channel
        # if self.menu_image is None:
        #     print(f"⚠️ Warning: Could not load menu overlay from '{menu_path}'. Menu will not be displayed.")
        # else:
        #     h, w = self.menu_image.shape[:2] # Get height and width
        #     channels = self.menu_image.shape[2] if len(self.menu_image.shape) > 2 else 1 # Get number of channels
        #     print(f"✅ Menu overlay loaded: {w}x{h}px, {channels} channels from '{menu_path}'")
        #     
        #     # Resize menu if it's too large to fit in the frame
        #     max_menu_height = int(self.height * 0.4)  # Max 25% of frame height
        #     max_menu_width = int(self.width * 0.20)   # Max 20% of frame width
        #     
        #     if h > max_menu_height or w > max_menu_width:
        #         # Calculate scaling factor to fit within limits
        #         scale_h = max_menu_height / h
        #         scale_w = max_menu_width / w
        #         scale = min(scale_h, scale_w)
        #         
        #         new_w = int(w * scale)
        #         new_h = int(h * scale)
        #         
        #         self.menu_image = cv2.resize(self.menu_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        #         print(f"   Resized to: {new_w}x{new_h}px to fit frame ({self.width}x{self.height})")
        
        # Set menu_image to None when commented out
        self.menu_image = None

    def select_camera(self):
        """Finds camera names on both Windows and macOS."""
        import os
        import sys
        import subprocess

        os.environ["OPENCV_LOG_LEVEL"] = "OFF"
        camera_list = {}

        # --- WINDOWS LOGIC ---
        if sys.platform == 'win32':
            try:
                from pygrabber.dshow_graph import FilterGraph
                devices = FilterGraph().get_input_devices()
                for i, name in enumerate(devices):
                    camera_list[i] = name
            except Exception: pass

        # --- MACOS LOGIC ---
        elif sys.platform == 'darwin':
            try:
                cmd = ["system_profiler", "SPCameraDataType"]
                output = subprocess.check_output(cmd).decode('utf-8')
                names = [line.strip().replace("Model ID: ", "") for line in output.split("\n") if "Model ID" in line or "Name" in line]
                for i, name in enumerate(names[:5]):
                    camera_list[i] = name.split(":")[-1].strip()
            except Exception: pass

        # --- FALLBACK (Linux) ---
        if not camera_list:
            print("🔍 Scanning hardware ports...")
            for i in range(5):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    camera_list[i] = f"Camera Device {i}"
                    cap.release()

        print("\n" + "—"*45)
        print("🎥 AVAILABLE VIDEO DEVICES")
        print("—"*45)

        if not camera_list:
            print("⚠️ No cameras detected! Defaulting to index 0.")
            return 0

        for idx, name in camera_list.items():
            print(f"   [{idx}] -> {name}")
        print("—"*45)

        while True:
            choice = input(f"👉 Select Camera Index {list(camera_list.keys())}: ").strip()
            if choice == "": return list(camera_list.keys())[0]
            try:
                val = int(choice)
                if val in camera_list:
                    print(f"✅ Selected: {camera_list[val]}")
                    return val
            except: pass
            print("Invalid selection.")
    #
    def process_tip(self, amount, username="Viewer"):
        """Activates filters based on token ranges."""
        # Iterăm prin lista de configurări
        for min_t, max_t, name, instance, duration in self.fixed_tips:
            if min_t <= amount <= max_t:
                self.queue.append({
                    "name": name,
                    "user": username,
                    "duration": duration,
                    "instance": instance
                })
                print(f"✅ [TIP] {amount} tokens de la {username} -> Activat: {name}")
                return  # Oprim căutarea după ce am găsit range-ul corect

        print(f"ℹ️ [TIP] {amount} tokens primite, dar nu există filtru configurat pentru această sumă.")

    def draw_rounded_rect_with_glow(self, frame, x1, y1, x2, y2, corner_radius, bg_color, border_color, glow_thickness=8):
        """
        Draws a rounded rectangle with glassmorphism glow effect.
        
        Args:
            frame: The frame to draw on
            x1, y1: Top-left coordinates
            x2, y2: Bottom-right coordinates
            corner_radius: Radius for rounded corners
            bg_color: Background color (B, G, R)
            border_color: Border/glow color (B, G, R) - Neon Magenta or Cyber Cyan
            glow_thickness: Thickness of the glow effect
        """
        # Create overlay for semi-transparent background
        overlay = frame.copy()
        
        # Draw rounded background using circles at corners and rectangles
        # Top-left corner
        cv2.circle(overlay, (x1 + corner_radius, y1 + corner_radius), corner_radius, bg_color, -1, cv2.LINE_AA)
        # Top-right corner
        cv2.circle(overlay, (x2 - corner_radius, y1 + corner_radius), corner_radius, bg_color, -1, cv2.LINE_AA)
        # Bottom-left corner
        cv2.circle(overlay, (x1 + corner_radius, y2 - corner_radius), corner_radius, bg_color, -1, cv2.LINE_AA)
        # Bottom-right corner
        cv2.circle(overlay, (x2 - corner_radius, y2 - corner_radius), corner_radius, bg_color, -1, cv2.LINE_AA)
        
        # Fill rectangles
        cv2.rectangle(overlay, (x1 + corner_radius, y1), (x2 - corner_radius, y2), bg_color, -1)
        cv2.rectangle(overlay, (x1, y1 + corner_radius), (x2, y2 - corner_radius), bg_color, -1)
        
        # Blend overlay with frame for transparency
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Draw glow border (thicker, semi-transparent)
        glow_color = (border_color[0] // 2, border_color[1] // 2, border_color[2] // 2)
        self._draw_rounded_border(frame, x1, y1, x2, y2, corner_radius, glow_color, glow_thickness, alpha=0.4)
        
        # Draw bright neon border (thin, bright)
        self._draw_rounded_border(frame, x1, y1, x2, y2, corner_radius, border_color, 2, alpha=1.0)
    
    def _draw_rounded_border(self, frame, x1, y1, x2, y2, corner_radius, color, thickness, alpha=1.0):
        """Helper to draw rounded border with specified thickness and alpha."""
        if alpha < 1.0:
            overlay = frame.copy()
            self._draw_rounded_border_solid(overlay, x1, y1, x2, y2, corner_radius, color, thickness)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        else:
            self._draw_rounded_border_solid(frame, x1, y1, x2, y2, corner_radius, color, thickness)
    
    def _draw_rounded_border_solid(self, frame, x1, y1, x2, y2, corner_radius, color, thickness):
        """Draws the actual rounded border lines."""
        # Top line
        cv2.line(frame, (x1 + corner_radius, y1), (x2 - corner_radius, y1), color, thickness, cv2.LINE_AA)
        # Bottom line
        cv2.line(frame, (x1 + corner_radius, y2), (x2 - corner_radius, y2), color, thickness, cv2.LINE_AA)
        # Left line
        cv2.line(frame, (x1, y1 + corner_radius), (x1, y2 - corner_radius), color, thickness, cv2.LINE_AA)
        # Right line
        cv2.line(frame, (x2, y1 + corner_radius), (x2, y2 - corner_radius), color, thickness, cv2.LINE_AA)
        
        # Corner arcs
        cv2.ellipse(frame, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(frame, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(frame, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(frame, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, color, thickness, cv2.LINE_AA)

    def draw_pill_background(self, frame, text, x, y, font_scale, font_thickness, bg_color):
        """Draws a pill-shaped background for highlighted text (e.g., token amounts)."""
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
        padding_x, padding_y = 12, 6
        
        # Create overlay for pill
        overlay = frame.copy()
        pill_x1 = x - padding_x
        pill_y1 = y - text_size[1] - padding_y
        pill_x2 = x + text_size[0] + padding_x
        pill_y2 = y + padding_y
        
        # Draw rounded pill
        pill_radius = (pill_y2 - pill_y1) // 2
        cv2.circle(overlay, (pill_x1 + pill_radius, pill_y1 + pill_radius), pill_radius, bg_color, -1, cv2.LINE_AA)
        cv2.circle(overlay, (pill_x2 - pill_radius, pill_y1 + pill_radius), pill_radius, bg_color, -1, cv2.LINE_AA)
        cv2.rectangle(overlay, (pill_x1 + pill_radius, pill_y1), (pill_x2 - pill_radius, pill_y2), bg_color, -1)
        
        # Blend pill with frame
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        return x, y

    def update_queue(self):
        """Manages the transition between filters in the sequence."""
        now = time.time()

        # If nothing is running, grab the next item from queue
        if self.current_filter is None and self.queue:
            self.current_filter = self.queue.popleft()
            self.filter_end_time = now + self.current_filter["duration"]

        # If something is running and time is up
        elif self.current_filter and now > self.filter_end_time:
            self.current_filter = None  # Clear it to trigger next one

    def overlay_image_alpha(self, img, overlay, pos):
        """
        Efficiently overlay a transparent PNG image onto the frame using alpha blending.
        
        Args:
            img: Background image (frame from video)
            overlay: Foreground image with alpha channel (BGRA format)
            pos: Tuple (x, y) for top-left position of overlay
        
        Performance: Uses proper alpha blending for semi-transparent pixels.
        """
        if overlay is None:
            return  # Skip if overlay image not loaded
        
        x, y = pos
        h, w = overlay.shape[:2]
        
        # Boundary check - ensure overlay fits within frame
        if x < 0 or y < 0 or x + w > img.shape[1] or y + h > img.shape[0]:
            return  # Skip if overlay would go out of bounds
        
        # Extract the region of interest (ROI) from the background
        roi = img[y:y+h, x:x+w]
        
        # Check if overlay has alpha channel
        if len(overlay.shape) == 3 and overlay.shape[2] == 4:
            # BGRA image with alpha channel
            overlay_bgr = overlay[:, :, :3].astype(float)  # Color channels (BGR)
            alpha_mask = overlay[:, :, 3].astype(float) / 255.0  # Normalize alpha to 0-1
            
            # Expand alpha mask to 3 channels for broadcasting
            alpha_3ch = cv2.merge([alpha_mask, alpha_mask, alpha_mask])
            
            # Blend: result = overlay * alpha + background * (1 - alpha)
            blended = (overlay_bgr * alpha_3ch + roi.astype(float) * (1.0 - alpha_3ch)).astype('uint8')
            
            # Place the blended result back into the original image
            img[y:y+h, x:x+w] = blended
        elif len(overlay.shape) == 3 and overlay.shape[2] == 3:
            # BGR image without alpha channel - direct copy
            img[y:y+h, x:x+w] = overlay
        else:
            # Grayscale or other format - skip
            pass


    def draw_queue_box(self, frame):
        """Draws the queue box on the right side with glassmorphism and progress bar."""
        h, w, _ = frame.shape
        box_w, box_h = 350, 170
        x1, y1 = w - box_w - 20, h - box_h - 20
        x2, y2 = w - 20, h - 20
        corner_radius = 20
        
        # Neon colors (BGR format)
        NEON_MAGENTA = (255, 0, 255)
        CYBER_CYAN = (255, 255, 0)
        PURE_WHITE = (255, 255, 255)
        DARK_BG = (20, 15, 10)
        
        # Enhanced blur effect for glassmorphism
        roi = frame[y1:y2, x1:x2].copy()
        roi_blurred = cv2.GaussianBlur(roi, (21, 21), 0)
        frame[y1:y2, x1:x2] = roi_blurred
        
        # Draw rounded rectangle with glow
        self.draw_rounded_rect_with_glow(frame, x1, y1, x2, y2, corner_radius, DARK_BG, CYBER_CYAN, glow_thickness=8)
        
        if self.current_filter:
            remaining = max(0, int(self.filter_end_time - time.time()))
            total_duration = self.current_filter['duration']
            elapsed = total_duration - remaining
            progress = min(1.0, elapsed / total_duration) if total_duration > 0 else 0
            
            # Pulsing LIVE indicator
            pulse = abs((time.time() * 2) % 2 - 1)  # Creates a 0->1->0 pulse
            live_alpha = 0.5 + (pulse * 0.5)  # Varies between 0.5 and 1.0
            live_size = int(8 + pulse * 3)  # Varies between 8 and 11
            
            # Draw LIVE indicator
            live_x = x1 + 20
            live_y = y1 + 28
            
            # Draw pulsing circle
            live_overlay = frame.copy()
            cv2.circle(live_overlay, (live_x, live_y), live_size, (0, 0, 255), -1, cv2.LINE_AA)
            cv2.addWeighted(live_overlay, live_alpha, frame, 1 - live_alpha, 0, frame)
            
            # LIVE text
            cv2.putText(frame, "LIVE", (live_x + 15, live_y + 6), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
            
            # Filter name
            filter_text = self.current_filter['name']
            cv2.putText(frame, filter_text, (live_x + 70, live_y + 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, PURE_WHITE, 2, cv2.LINE_AA)
            
            # Progress bar
            bar_x1 = x1 + 20
            bar_y = y1 + 50
            bar_w = box_w - 40
            bar_h = 12
            bar_corner = 6
            
            # Background bar (empty)
            bg_overlay = frame.copy()
            cv2.rectangle(bg_overlay, (bar_x1, bar_y), (bar_x1 + bar_w, bar_y + bar_h), (60, 60, 60), -1)
            cv2.addWeighted(bg_overlay, 0.5, frame, 0.5, 0, frame)
            
            # Progress fill (colored)
            fill_w = int(bar_w * (1 - progress))  # Shrinks as time elapses
            if fill_w > 0:
                # Gradient from cyan to magenta
                progress_overlay = frame.copy()
                
                # Create gradient effect
                for i in range(fill_w):
                    ratio = i / fill_w if fill_w > 0 else 0
                    # Interpolate between CYBER_CYAN and NEON_MAGENTA
                    color = tuple(int(CYBER_CYAN[j] * (1 - ratio) + NEON_MAGENTA[j] * ratio) for j in range(3))
                    cv2.line(progress_overlay, (bar_x1 + i, bar_y), (bar_x1 + i, bar_y + bar_h), color, 1)
                
                cv2.addWeighted(progress_overlay, 0.9, frame, 0.1, 0, frame)
            
            # Time remaining text
            time_text = f"{remaining}s"
            cv2.putText(frame, time_text, (bar_x1 + bar_w - 35, bar_y + bar_h + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, PURE_WHITE, 2, cv2.LINE_AA)
            
            # Queue counter
            queue_count = len(self.queue)
            count_text = f"{queue_count} in queue"
            cv2.putText(frame, count_text, (bar_x1, bar_y + bar_h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)
            
            # Separator line
            sep_y = bar_y + bar_h + 30
            cv2.line(frame, (x1 + 20, sep_y), (x2 - 20, sep_y), (100, 100, 100), 1, cv2.LINE_AA)
            
            # Up Next list
            next_y = sep_y + 20
            cv2.putText(frame, "UP NEXT:", (x1 + 20, next_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, CYBER_CYAN, 1, cv2.LINE_AA)
            
            # Display next 2 items
            for i, item in enumerate(list(self.queue)[:3]):
                next_y += 15
                queue_text = f"{item['name']}"
                cv2.putText(frame, queue_text, (x1 + 25, next_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, cv2.LINE_AA)
        else:
            # No active filter - waiting state
            waiting_y = y1 + 65
            cv2.putText(frame, "Tip now to unlock the fun", (x1 + 20, waiting_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 2, cv2.LINE_AA)



    def run(self):
        window_name = "AR_STREAM_WINDOW"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        print("--- APP RUNNING ---")
        
        first_frame = True  # Flag to resize menu on first frame

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            
            # On first frame, ensure menu fits actual frame dimensions
            if first_frame and self.menu_image is not None:
                actual_h, actual_w = frame.shape[:2]
                menu_h, menu_w = self.menu_image.shape[:2]
                
                # Check if menu needs resizing for actual frame
                max_menu_h = int(actual_h * 0.8)  # Max 80% of actual height
                max_menu_w = int(actual_w * 0.35)  # Max 35% of actual width
                
                if menu_h > max_menu_h or menu_w > max_menu_w:
                    scale_h = max_menu_h / menu_h
                    scale_w = max_menu_w / menu_w
                    scale = min(scale_h, scale_w)
                    
                    new_w = int(menu_w * scale)
                    new_h = int(menu_h * scale)
                    
                    self.menu_image = cv2.resize(self.menu_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
                
                first_frame = False
            
            # Apply static menu overlay at top-left position (20, 20)
            self.overlay_image_alpha(frame, self.menu_image, (20, 20))

            self.update_queue()

            if self.current_filter:
                frame = self.current_filter["instance"].apply(frame)

            self.draw_queue_box(frame)

            # Manual Testing Keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('x'):
                break
            elif key == ord('1'):
                self.process_tip(120)   # Squirrel Cheeks 
            elif key == ord('2'):
                self.process_tip(130)   # Alien Face
            elif key == ord('3'):
                self.process_tip(140)   # Big Mouth
            elif key == ord('4'):
                self.process_tip(150)   # Pinocchio
            elif key == ord('5'):
                self.process_tip(160)   # Sharp Chin
            elif key == ord('6'):
                self.process_tip(170)   # Giant Forehead
            elif key == ord('7'):
                self.process_tip(180)   # Cube Head
            elif key == ord('8'):
                self.process_tip(190)   # Melted Face
            elif key == ord('9'):
                self.process_tip(200)   # Snail Eyes
            elif key == ord('0'):
                self.process_tip(210)   # Permanent Smile
            elif key == ord('q'):
                self.process_tip(220)   # Big Eyes
            elif key == ord('w'):
                self.process_tip(230)   # Rabbit Ears
            elif key == ord('e'):
                self.process_tip(240)   # Cyber Mask





            self.output.display(frame)

        self.output.stop()
        self.cap.release()


def load_config_from_env():
    """
    Încarcă configurația din fișierul .env
    Returns: dict cu configurația aplicației
    """
    # Încarcă .env file
    load_dotenv()
    
    # Helper function pentru boolean values
    def str_to_bool(value):
        if isinstance(value, bool):
            return value
        return value.lower() in ('true', '1', 'yes', 'on') if value else False
    
    # Citește environment variables
    environment = os.getenv('ENVIRONMENT', 'test')
    
    config = {
        'environment': environment,
        'chaturbate_url': os.getenv('CHATURBATE_URL') if str_to_bool(os.getenv('CHATURBATE_ENABLED', 'true')) else None,
        'stripchat_url': os.getenv('STRIPCHAT_URL') if str_to_bool(os.getenv('STRIPCHAT_ENABLED', 'true')) else None,
        'camsoda_url': os.getenv('CAMSODA_URL') if str_to_bool(os.getenv('CAMSODA_ENABLED', 'true')) else None,
        'output_mode': os.getenv('OUTPUT_MODE', 'window'),
        'quality': os.getenv('QUALITY', '1080p'),
        'camera_index': int(os.getenv('CAMERA_INDEX', '0')),
        'debug_mode': str_to_bool(os.getenv('DEBUG_MODE', 'false')),
        'verbose_logging': str_to_bool(os.getenv('VERBOSE_LOGGING', 'false'))
    }
    
    return config


if __name__ == "__main__":
    # Încarcă configurația din .env
    config = load_config_from_env()
    
    # Afișează informații despre configurație
    print("=" * 60)
    print(f"🚀 AR FILTER SYSTEM - {config['environment'].upper()} MODE")
    print("=" * 60)
    print(f"\n📡 Platforme configurate:")
    if config['chaturbate_url']:
        print(f"   ✅ Chaturbate: {config['chaturbate_url']}")
    else:
        print(f"   ❌ Chaturbate: Disabled")
    
    if config['stripchat_url']:
        print(f"   ✅ Stripchat: {config['stripchat_url']}")
    else:
        print(f"   ❌ Stripchat: Disabled")
    
    if config['camsoda_url']:
        print(f"   ✅ Camsoda: {config['camsoda_url']}")
    else:
        print(f"   ❌ Camsoda: Disabled")
    
    print(f"\n⚙️  Settings:")
    print(f"   Output Mode: {config['output_mode']}")
    print(f"   Quality: {config['quality']}")
    print(f"   Debug Mode: {'On' if config['debug_mode'] else 'Off'}")
    print("=" * 60 + "\n")
    
    # Inițializează aplicația cu configurația din .env
    app = CameraFiltersAutomation(
        chaturbate_url=config['chaturbate_url'],
        stripchat_url=config['stripchat_url'],
        camsoda_url=config['camsoda_url'],
        output_mode=config['output_mode'],
        quality=config['quality']
    )
    app.run()

