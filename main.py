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
from collections import deque

try:
    os.dup2(old_stderr_fd, sys.stderr.fileno())
    os.close(null_fd)
except Exception:
    pass

class CameraFiltersAutomation:
    def __init__(self, output_mode="window", chaturbate_url=None, stripchat_url=None, camsoda_url=None, quality="1080p"):
        if quality == "4K":
            self.width, self.height, self.fps = 3840, 2160, 30
        else:  # Default 1080p
            self.width, self.height, self.fps = 1920, 1080, 60

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
        self.fixed_tips = {
            33:  ('Sparkles', RainSparkleFilter(), 10),
            50:  ('Rabbit Ears', RabbitEarsFilter(), 15),
            99:  ('Big Eyes', BigEyeFilter(), 20),
            200: ('Cyber Mask', FaceMask3D(), 30)
        }

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

    def process_tip(self, amount, username="Viewer"):
        """Activates filters ONLY for specific tip amounts."""
        if amount in self.fixed_tips:
            name, instance, duration = self.fixed_tips[amount]
            # Add to the sequence
            self.queue.append({
                "name": name,
                "user": username,
                "duration": duration,
                "instance": instance
            })
            print(f"Added {name} to queue for {username}")

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

    def draw_queue_box(self, frame):
        h, w, _ = frame.shape
        box_w, box_h = 320, 115
        x1, y1 = w - box_w - 20, h - box_h - 20
        x2, y2 = w - 20, h - 20

        # 1. Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), 1)

        if self.current_filter:
            rem = int(self.filter_end_time - time.time())

            # 2. Main Title (Active Filter)
            filter_text = f"{self.current_filter['name']} - {rem}s"
            cv2.putText(frame, filter_text, (x1 + 15, y1 + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 51, 255), 2)

            # 3. Queue Counter (Top Right of the box)
            # Count includes everything in the queue deque
            queue_count = len(self.queue)
            count_text = f"({queue_count} in queue)"
            cv2.putText(frame, count_text, (x1 + 175, y1 + 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

            # 4. Separator Line
            cv2.line(frame, (x1 + 15, y1 + 45), (x2 - 15, y1 + 45), (80, 80, 80), 1)

            # 5. Up Next List
            y_offset = y1 + 65
            cv2.putText(frame, "UP NEXT:", (x1 + 15, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

            # Display only the next 2, but the counter above shows the total
            for i, item in enumerate(list(self.queue)[:2]):
                y_offset += 18
                user_display = (item['user'][:10] + '..') if len(item['user']) > 10 else item['user']
                queue_text = f"{i + 1}. {user_display} ({item['name']})"
                cv2.putText(frame, queue_text, (x1 + 15, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (220, 220, 220), 1)
        else:
            cv2.putText(frame, "Waiting for tips...", (x1 + 15, y1 + 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 120), 1)



    def run(self):
        window_name = "AR_STREAM_WINDOW"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        print("--- APP RUNNING ---")

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)

            self.update_queue()

            if self.current_filter:
                frame = self.current_filter["instance"].apply(frame)

            self.draw_queue_box(frame)

            # Manual Testing Keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('1'):
                self.process_tip(35)  # Test Tier 1
            elif key == ord('2'):
                self.process_tip(105)  # Test Tier 2
            elif key == ord('3'):
                self.process_tip(500)  # Test Tier 3

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

