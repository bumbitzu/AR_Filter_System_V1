import json
import os
import queue
import threading
import time
from dotenv import load_dotenv
from pynput.keyboard import Controller, Key, Listener

from core.ChaturbateListener import ChaturbateListener
from core.StripchatListener import StripchatListener
from core.CamsodaListener import CamsodaListener

# Import queue UI server
try:
    from queue_ui_server import add_to_queue, next_filter, run_server as run_ui_server
    UI_SERVER_AVAILABLE = True
except ImportError:
    UI_SERVER_AVAILABLE = False
    print("⚠️ Queue UI Server not available")


class KeySender:
    def __init__(self, hold_ms=50, delay_ms=80):
        self.controller = Controller()
        self.hold_seconds = max(0, hold_ms) / 1000.0
        self.delay_seconds = max(0, delay_ms) / 1000.0
        self.alias_map = {
            "ctrl": Key.ctrl,
            "control": Key.ctrl,
            "shift": Key.shift,
            "alt": Key.alt,
            "option": Key.alt,
            "cmd": Key.cmd,
            "win": Key.cmd,
            "super": Key.cmd,
            "enter": Key.enter,
            "return": Key.enter,
            "space": Key.space,
            "tab": Key.tab,
            "esc": Key.esc,
            "escape": Key.esc,
            "backspace": Key.backspace,
            "delete": Key.delete,
            "up": Key.up,
            "down": Key.down,
            "left": Key.left,
            "right": Key.right,
            "home": Key.home,
            "end": Key.end,
            "pageup": Key.page_up,
            "pagedown": Key.page_down,
        }

    def _resolve_key(self, token):
        token = token.strip()
        if token == "":
            return None
        if len(token) == 1:
            return token

        lowered = token.lower()
        if lowered in self.alias_map:
            return self.alias_map[lowered]

        if lowered.startswith("f") and lowered[1:].isdigit():
            fn_name = lowered
            if hasattr(Key, fn_name):
                return getattr(Key, fn_name)

        return None

    def _press_key(self, key):
        if key is None:
            return
        self.controller.press(key)
        if self.hold_seconds > 0:
            time.sleep(self.hold_seconds)
        self.controller.release(key)

    def _press_combo(self, keys):
        pressed = []
        for key in keys:
            if key is None:
                continue
            self.controller.press(key)
            pressed.append(key)
        if self.hold_seconds > 0:
            time.sleep(self.hold_seconds)
        for key in reversed(pressed):
            self.controller.release(key)

    def send_sequence(self, key_sequence):
        for entry in key_sequence:
            if isinstance(entry, str) and "+" in entry:
                parts = [self._resolve_key(part) for part in entry.split("+")]
                self._press_combo(parts)
            else:
                key = self._resolve_key(entry if isinstance(entry, str) else str(entry))
                self._press_key(key)
            if self.delay_seconds > 0:
                time.sleep(self.delay_seconds)


class TipKeyAutomation:
    def __init__(self, chaturbate_url=None, stripchat_url=None, camsoda_url=None, key_rules=None, hold_ms=50, delay_ms=80, filter_duration=10, filter_close_key=None, enable_ui_server=True, enable_manual_triggers=True):
        self.key_sender = KeySender(hold_ms=hold_ms, delay_ms=delay_ms)
        self.key_rules = key_rules or []
        self.filter_duration = filter_duration
        self.filter_close_key = filter_close_key  # Tastă pentru închiderea filtrului
        self.queue = queue.Queue()
        self.running = False
        self.worker_thread = None
        self.ui_server_thread = None
        self.keyboard_listener = None
        self.enable_ui_server = enable_ui_server and UI_SERVER_AVAILABLE
        self.enable_manual_triggers = enable_manual_triggers
        self.last_key_time = {}  # Track last trigger time for each key (cooldown)

        self.listeners = []
        if chaturbate_url:
            listener = ChaturbateListener(chaturbate_url, self.process_tip)
            listener.start()
            self.listeners.append(listener)
        if stripchat_url:
            listener = StripchatListener(stripchat_url, self.process_tip)
            listener.start()
            self.listeners.append(listener)
        if camsoda_url:
            listener = CamsodaListener(camsoda_url, self.process_tip)
            listener.start()
            self.listeners.append(listener)

        if not self.listeners:
            print("⚠️ No platform APIs configured. Waiting for tips is disabled.")

    def start(self):
        if self.running:
            return
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        print("🔧 [DEBUG] Worker thread started")
        
        # Start UI server if enabled
        if self.enable_ui_server:
            self.ui_server_thread = threading.Thread(target=self._start_ui_server, daemon=True)
            self.ui_server_thread.start()
            print("🎨 Queue UI Server starting on http://127.0.0.1:8080")
        
        # Start keyboard listener for manual triggers
        if self.enable_manual_triggers:
            self.keyboard_listener = Listener(on_press=self._on_key_press)
            self.keyboard_listener.start()
            print("⌨️  Manual trigger keys enabled (1, 2, 3, 4)")
    
    def _on_key_press(self, key):
        """Handle manual key presses for triggering filters"""
        try:
            key_map = {
                '1': 0,  # First rule index
                '2': 1,  # Second rule index
                '3': 2,  # Third rule index
                '4': 3,  # Fourth rule index
                '5': 4,  # Fifth rule index
                '6': 5,  # Sixth rule index
                '7': 6,  # Seventh rule index
                '8': 7,  # Eighth rule index
                '9': 8,  # Ninth rule index
                '0': 9,  # Tenth rule index
            }
            
            # Get the character from the key
            if hasattr(key, 'char') and key.char in key_map:
                current_time = time.time()
                # Cooldown of 0.5 seconds between triggers for the same key
                if key.char not in self.last_key_time or (current_time - self.last_key_time[key.char]) > 0.5:
                    self.last_key_time[key.char] = current_time
                    rule_index = key_map[key.char]
                    if rule_index < len(self.key_rules):
                        rule = self.key_rules[rule_index]
                        # Use the minimum value from the range as the amount
                        amount = rule['min']
                        print(f"🎹 Manual trigger: Key {key.char} → {rule['label']}")
                        self.process_tip(amount, "Manual")
        except Exception as e:
            pass  # Ignore errors from key handling
    
    def _start_ui_server(self):
        """Start the Flask UI server in a separate thread"""
        try:
            run_ui_server(host='127.0.0.1', port=8080)
        except Exception as e:
            print(f"⚠️ Failed to start UI server: {e}")

    def stop(self):
        self.running = False
        for listener in self.listeners:
            listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        try:
            self.queue.put_nowait(None)
        except Exception:
            pass
        if self.worker_thread:
            self.worker_thread.join(timeout=2)

    def _worker(self):
        print("🔧 [DEBUG] Worker thread running...")
        
        while self.running:
            item = self.queue.get()
            if item is None:
                break
            
            print(f"🔧 [DEBUG] Processing item from queue: {item['label']} with keys: {item['keys']}")
            print(f"⏳ Filtru activ: {item['label']} pentru {self.filter_duration} secunde...")
            
            # Trimite tastele pentru a activa filtrul
            self.key_sender.send_sequence(item["keys"])
            print(f"✅ Taste apăsate pentru activare: {item['keys']}")
            
            # Așteaptă durata filtrului
            time.sleep(self.filter_duration)
            
            # Închide filtrul la final
            if self.filter_close_key:
                close_keys = [self.filter_close_key] if isinstance(self.filter_close_key, str) else self.filter_close_key
                self.key_sender.send_sequence(close_keys)
                print(f"🔴 Taste apăsate pentru închidere: {close_keys}")
            else:
                # Dacă nu e definită tastă de închidere, apasă din nou tastele de activare
                self.key_sender.send_sequence(item["keys"])
                print(f"🔴 Taste apăsate pentru închidere: {item['keys']} (reapăsare)")
            
            # Move to next in UI queue after filter duration
            if self.enable_ui_server:
                next_filter()
            
            print(f"✅ Filtru {item['label']} finalizat. Trecem la următorul...\n")
            self.queue.task_done()

    def process_tip(self, amount, username="Viewer"):
        for rule in self.key_rules:
            if rule["min"] <= amount <= rule["max"]:
                item = {
                    "keys": rule["keys"],
                    "amount": amount,
                    "username": username,
                    "label": rule["label"],
                }
                
                # Add to UI queue
                if self.enable_ui_server:
                    add_to_queue(item['label'], item['username'], item['amount'])
                
                print(f"🔧 [DEBUG] Adding to queue: {item}")
                self.queue.put(item)
                print(f"✅ [TIP] {amount} tokens de la {username} -> Taste: {rule['label']}")
                return
        print(f"ℹ️ [TIP] {amount} tokens primite, dar nu există taste configurate pentru această sumă.")

    def run_forever(self):
        self.start()
        while True:
            time.sleep(1)


def _str_to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes", "on") if value is not None else False


def load_key_rules():
    """Load key rules configuration (hardcoded for now)"""
    return [
        {"min": 119, "max": 128, "keys": ["shift+q"], "label": "Cartoon Style"},
        {"min": 129, "max": 138, "keys": ["shift+w"], "label": "Neon Devil"},
        {"min": 139, "max": 148, "keys": ["shift+e"], "label": "Shock ML"},
        {"min": 149, "max": 158, "keys": ["shift+r"], "label": "Crying ML"},
        {"min": 159, "max": 168, "keys": ["shift+t"], "label": "Kisses"},
        {"min": 169, "max": 178, "keys": ["shift+y"], "label": "Pinocchio"},
        {"min": 179, "max": 189, "keys": ["shift+u"], "label": "Ski Mask"},
        {"min": 190, "max": 198, "keys": ["shift+i"], "label": "Cowboy"},
        {"min": 199, "max": 209, "keys": ["shift+o"], "label": "Big Cheeks"},
        {"min": 210, "max": 219, "keys": ["shift+p"], "label": "Lips Morph"},
    ]


def load_config_from_env():
    load_dotenv()
    
    # Parse filter close key - poate fi None, o tastă singură sau combinație
    filter_close_key_raw = os.getenv("FILTER_CLOSE_KEY", "").strip()
    filter_close_key = filter_close_key_raw if filter_close_key_raw else None

    return {
        "environment": os.getenv("ENVIRONMENT", "test"),
        "chaturbate_url": os.getenv("CHATURBATE_URL") if _str_to_bool(os.getenv("CHATURBATE_ENABLED", "true")) else None,
        "stripchat_url": os.getenv("STRIPCHAT_URL") if _str_to_bool(os.getenv("STRIPCHAT_ENABLED", "true")) else None,
        "camsoda_url": os.getenv("CAMSODA_URL") if _str_to_bool(os.getenv("CAMSODA_ENABLED", "true")) else None,
        "hold_ms": int(os.getenv("KEYPRESS_HOLD_MS", "50")),
        "delay_ms": int(os.getenv("KEYPRESS_DELAY_MS", "80")),
        "filter_duration": int(os.getenv("FILTER_DURATION_SECONDS", "10")),
        "filter_close_key": filter_close_key,
    }
    


if __name__ == "__main__":
    config = load_config_from_env()
    key_rules = load_key_rules()

    print("=" * 60)
    print(f"🚀 TIP → KEYS AUTOMATION - {config['environment'].upper()} MODE")
    print("=" * 60)
    print("\n📡 Platforme configurate:")
    if config["chaturbate_url"]:
        print(f"   ✅ Chaturbate: {config['chaturbate_url']}")
    else:
        print("   ❌ Chaturbate: Disabled")

    if config["stripchat_url"]:
        print(f"   ✅ Stripchat: {config['stripchat_url']}")
    else:
        print("   ❌ Stripchat: Disabled")

    if config["camsoda_url"]:
        print(f"   ✅ Camsoda: {config['camsoda_url']}")
    else:
        print("   ❌ Camsoda: Disabled")

    print("\n⌨️  Key settings:")
    print(f"   Hold: {config['hold_ms']}ms")
    print(f"   Delay: {config['delay_ms']}ms")
    print(f"   Filter duration: {config['filter_duration']}s")
    print(f"   Filter close key: {config['filter_close_key'] or 'Repress activation keys'}")
    print("=" * 60 + "\n")

    app = TipKeyAutomation(
        chaturbate_url=config["chaturbate_url"],
        stripchat_url=config["stripchat_url"],
        camsoda_url=config["camsoda_url"],
        key_rules=key_rules,
        hold_ms=config["hold_ms"],
        delay_ms=config["delay_ms"],
        filter_duration=config["filter_duration"],
        filter_close_key=config["filter_close_key"],
    )

    try:
        app.run_forever()
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user.")
    finally:
        app.stop()
