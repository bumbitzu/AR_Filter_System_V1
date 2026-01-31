import json
import os
import queue
import threading
import time
from dotenv import load_dotenv
from pynput.keyboard import Controller, Key

from core.ChaturbateListener import ChaturbateListener
from core.StripchatListener import StripchatListener
from core.CamsodaListener import CamsodaListener


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
    def __init__(self, chaturbate_url=None, stripchat_url=None, camsoda_url=None, key_rules=None, hold_ms=50, delay_ms=80):
        self.key_sender = KeySender(hold_ms=hold_ms, delay_ms=delay_ms)
        self.key_rules = key_rules or []
        self.queue = queue.Queue()
        self.running = False
        self.worker_thread = None

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

    def stop(self):
        self.running = False
        for listener in self.listeners:
            listener.stop()
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
            self.key_sender.send_sequence(item["keys"])
            print(f"🔧 [DEBUG] Keys sent: {item['keys']}")
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


def load_key_rules_from_env():
    default_rules = [
        {"min": 119, "max": 128, "keys": ["ctrl+1"], "label": "Ctrl+Key 1"},
        {"min": 129, "max": 138, "keys": ["ctrl+2"], "label": "Ctrl+Key 2"},
    ]

    raw = os.getenv("TIP_KEY_MAP", "").strip()
    if not raw:
        return default_rules

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        print("⚠️ TIP_KEY_MAP nu este JSON valid. Se folosesc regulile implicite.")
        return default_rules

    rules = []
    for entry in parsed:
        try:
            min_t = int(entry.get("min"))
            max_t = int(entry.get("max"))
            keys = entry.get("keys")
            label = entry.get("label") or "+".join(keys) if isinstance(keys, list) else str(keys)
            if not isinstance(keys, list) or not keys:
                raise ValueError("keys trebuie să fie listă nenulă")
            rules.append({"min": min_t, "max": max_t, "keys": keys, "label": label})
        except Exception:
            print("⚠️ Regula TIP_KEY_MAP invalidă, a fost ignorată.")
    return rules or default_rules


def load_config_from_env():
    load_dotenv()

    return {
        "environment": os.getenv("ENVIRONMENT", "test"),
        "chaturbate_url": os.getenv("CHATURBATE_URL") if _str_to_bool(os.getenv("CHATURBATE_ENABLED", "true")) else None,
        "stripchat_url": os.getenv("STRIPCHAT_URL") if _str_to_bool(os.getenv("STRIPCHAT_ENABLED", "true")) else None,
        "camsoda_url": os.getenv("CAMSODA_URL") if _str_to_bool(os.getenv("CAMSODA_ENABLED", "true")) else None,
        "hold_ms": int(os.getenv("KEYPRESS_HOLD_MS", "50")),
        "delay_ms": int(os.getenv("KEYPRESS_DELAY_MS", "80")),
    }


if __name__ == "__main__":
    config = load_config_from_env()
    key_rules = load_key_rules_from_env()

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
    print("=" * 60 + "\n")

    app = TipKeyAutomation(
        chaturbate_url=config["chaturbate_url"],
        stripchat_url=config["stripchat_url"],
        camsoda_url=config["camsoda_url"],
        key_rules=key_rules,
        hold_ms=config["hold_ms"],
        delay_ms=config["delay_ms"],
    )

    try:
        app.run_forever()
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user.")
    finally:
        app.stop()
