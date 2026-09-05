"""
AR Filter System - Aplicatie Principala
Sistem automat de activare filtre AR bazat pe tips de la platforme de streaming
"""

# Importuri standard Python
import json
import os
import queue
import threading
import time

# Importuri biblioteci externe
from dotenv import load_dotenv  # Pentru incarcarea variabilelor de mediu din .env
from pynput.keyboard import Controller, Key, Listener  # Pentru simularea apasarii tastelor

# Importuri module proprii - listenere pentru fiecare platforma
from core.ChaturbateListener import ChaturbateListener
from core.StripchatListener import StripchatListener
from core.CamsodaListener import CamsodaListener

# Incercam sa importam serverul UI pentru coada de filtre
try:
    from queue_ui_server import add_to_queue, next_filter, run_server as run_ui_server
    UI_SERVER_AVAILABLE = True
except ImportError:
    UI_SERVER_AVAILABLE = False
    print("⚠️ Serverul Queue UI nu este disponibil")


class KeySender:
    """
    Clasa pentru trimiterea secventelor de taste catre sistem
    Simuleaza apasarea tastelor pentru activarea filtrelor in Snap Camera
    """
    
    def __init__(self, hold_ms=50, delay_ms=80):
        """
        Initializeaza controller-ul de tastatura
        
        Args:
            hold_ms: Timp de tinere a tastei apasat (milisecunde)
            delay_ms: Pauza intre apasari consecutive (milisecunde)
        """
        self.controller = Controller()  # Controller pynput pentru simularea tastelor
        self.hold_seconds = max(0, hold_ms) / 1000.0  # Converteste ms in secunde
        self.delay_seconds = max(0, delay_ms) / 1000.0
        
        # Dictionar pentru maparea alias-urilor de taste la obiecte Key
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
        """
        Converteste un string (ex: 'ctrl', 'f1') intr-un obiect Key
        
        Args:
            token: String reprezentand o tasta (ex: 'ctrl', 'shift', '1', 'f2')
            
        Returns:
            Obiect Key corespunzator sau caracterul daca e o singura litera
        """
        token = token.strip()
        if token == "":
            return None
        if len(token) == 1:  # Daca e o singura litera/cifra, returneaza direct
            return token

        lowered = token.lower()
        if lowered in self.alias_map:  # Cauta in dictionar de aliasuri
            return self.alias_map[lowered]

        # Verifica daca e tasta functie (F1-F12)
        if lowered.startswith("f") and lowered[1:].isdigit():
            fn_name = lowered
            if hasattr(Key, fn_name):
                return getattr(Key, fn_name)

        return None

    def _press_key(self, key):
        """
        Apasa si elibereaza o singura tasta
        
        Args:
            key: Obiect Key sau caracter de apasat
        """
        if key is None:
            return
        self.controller.press(key)  # Apasa tasta
        if self.hold_seconds > 0:
            time.sleep(self.hold_seconds)  # Tine apasata
        self.controller.release(key)  # Elibereaza tasta

    def _press_combo(self, keys):
        """
        Apasa o combinatie de taste (ex: Ctrl+Shift+A)
        Apasa tastele in ordine, apoi le elibereaza in ordine inversa
        
        Args:
            keys: Lista de obiecte Key de apasat simultan
        """
        pressed = []
        # Apasa toate tastele in ordine
        for key in keys:
            if key is None:
                continue
            self.controller.press(key)
            pressed.append(key)
        if self.hold_seconds > 0:
            time.sleep(self.hold_seconds)
        # Elibereaza tastele in ordine inversa
        for key in reversed(pressed):
            self.controller.release(key)

    def send_sequence(self, key_sequence):
        """
        Trimite o secventa completa de taste
        Suporta atat taste simple cat si combinatii (ex: ['ctrl+shift+a', '1', 'f2'])
        
        Args:
            key_sequence: Lista de stringuri reprezentand taste sau combinatii
        """
        for entry in key_sequence:
            # Daca contine '+', e o combinatie de taste (ex: 'ctrl+shift+a')
            if isinstance(entry, str) and "+" in entry:
                parts = [self._resolve_key(part) for part in entry.split("+")]
                self._press_combo(parts)
            else:
                # Tasta simpla
                key = self._resolve_key(entry if isinstance(entry, str) else str(entry))
                self._press_key(key)
            # Pauza intre taste
            if self.delay_seconds > 0:
                time.sleep(self.delay_seconds)


class TipKeyAutomation:
    """
    Clasa principala pentru automatizarea filtrelor pe baza de tips
    Asculta evenimente de la platforme (Chaturbate, Stripchat, Camsoda)
    si activeaza filtre prin simulare de taste
    """
    def __init__(self, chaturbate_url=None, stripchat_url=None, camsoda_url=None, key_rules=None, hold_ms=50, delay_ms=80, filter_duration=10, filter_close_key=None, enable_ui_server=True, enable_manual_triggers=True):
        """
        Initializeaza sistemul de automatizare
        
        Args:
            chaturbate_url: URL pentru API Chaturbate Events
            stripchat_url: URL pentru API Stripchat Events
            camsoda_url: URL pentru API Camsoda External
            key_rules: Lista de reguli pentru maparea sumelor la taste
            hold_ms: Durata apasarii tastei in milisecunde
            delay_ms: Pauza intre taste in milisecunde
            filter_duration: Durata filtrului activ in secunde
            filter_close_key: Tasta pentru inchiderea filtrului
            enable_ui_server: Porneste serverul web pentru UI
            enable_manual_triggers: Activeaza ascultarea tastelor 1-9
        """
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

        # Lista cu toti listenerii activi pentru platforme
        self.listeners = []
        
        # Porneste listener pentru Chaturbate daca e configurat
        if chaturbate_url:
            listener = ChaturbateListener(chaturbate_url, self.process_tip)
            listener.start()
            self.listeners.append(listener)
        
        # Porneste listener pentru Stripchat daca e configurat
        if stripchat_url:
            listener = StripchatListener(stripchat_url, self.process_tip)
            listener.start()
            self.listeners.append(listener)
        
        # Porneste listener pentru Camsoda daca e configurat
        if camsoda_url:
            listener = CamsodaListener(camsoda_url, self.process_tip)
            listener.start()
            self.listeners.append(listener)

        # Avertizare daca nu e configurata nicio platforma
        if not self.listeners:
            print("⚠️ Nicio platforma configurata. Asteptarea de tips este dezactivata.")

    def start(self):
        """
        Porneste toate componentele sistemului:
        - Thread worker pentru procesarea cozii de filtre
        - Server web pentru interfata grafica (optional)
        - Listener pentru trigger-uri manuale cu tastele 1-9 (optional)
        """
        if self.running:
            return
        self.running = True
        
        # Porneste thread-ul worker pentru coada de filtre
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        print("🔧 [DEBUG] Thread worker pornit")
        
        # Porneste serverul web pentru UI daca e activat
        if self.enable_ui_server:
            self.ui_server_thread = threading.Thread(target=self._start_ui_server, daemon=True)
            self.ui_server_thread.start()
            print("🎨 Serverul Queue UI porneste pe http://127.0.0.1:8080")
        
        # Porneste listener-ul de taste pentru trigger manual daca e activat
        if self.enable_manual_triggers:
            self.keyboard_listener = Listener(on_press=self._on_key_press)
            self.keyboard_listener.start()
            print("⌨️  Taste pentru trigger manual activate (1-9, 0)")
    
    def _on_key_press(self, key):
        """
        Handler pentru apasarea manuala a tastelor 1-9
        Activeaza filtrele corespunzatoare direct din tastatura
        Include cooldown de 0.5 secunde intre trigger-uri
        """
        try:
            # Mapare taste 1-9,0 la indecsi de reguli 0-9
            key_map = {
                '1': 0,  # Prima regula (Cartoon Style)
                '2': 1,  # A doua regula (Neon Devil)
                '3': 2,  # A treia regula (Shock ML)
                '4': 3,  # A patra regula (Crying ML)
                '5': 4,  # A cincea regula (Kisses)
                '6': 5,  # A sasea regula (Pinocchio)
                '7': 6,  # A saptea regula (Ski Mask)
                '8': 7,  # A opta regula (Cowboy)
                '9': 8,  # A noua regula (Big Cheeks)
                '0': 9,  # A zecea regula (Lips Morph)
            }
            
            # Extrage caracterul din obiectul key
            if hasattr(key, 'char') and key.char in key_map:
                current_time = time.time()
                # Cooldown de 0.5 secunde intre trigger-uri pentru aceeasi tasta
                if key.char not in self.last_key_time or (current_time - self.last_key_time[key.char]) > 0.5:
                    self.last_key_time[key.char] = current_time
                    rule_index = key_map[key.char]
                    # Verifica daca exista regula la acest index
                    if rule_index < len(self.key_rules):
                        rule = self.key_rules[rule_index]
                        # Foloseste valoarea minima din range ca suma
                        amount = rule['min']
                        print(f"🎹 Trigger manual: Tasta {key.char} → {rule['label']}")
                        self.process_tip(amount, "Manual")
        except Exception as e:
            pass  # Ignora erorile din gestionarea tastelor
    
    def _start_ui_server(self):
        """
        Porneste serverul Flask pentru interfata web
        Ruleaza in thread separat pentru a nu bloca executia principala
        """
        try:
            run_ui_server(host='127.0.0.1', port=8080)
        except Exception as e:
            print(f"⚠️ Eroare la pornirea serverului UI: {e}")

    def stop(self):
        """
        Opreste toate componentele sistemului:
        - Toti listenerii de platforme
        - Listener-ul de tastatura
        - Thread-ul worker (prin semnalizare cu None in coada)
        """
        self.running = False
        
        # Opreste toti listenerii de platforme
        for listener in self.listeners:
            listener.stop()
        
        # Opreste listener-ul de tastatura
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Trimite semnal de stop la worker thread
        try:
            self.queue.put_nowait(None)
        except Exception:
            pass
        
        # Asteapta ca worker thread sa se termine (timeout 2 secunde)
        if self.worker_thread:
            self.worker_thread.join(timeout=2)

    def _worker(self):
        print("🔧 [DEBUG] Thread worker ruleaza...")
        
        while self.running:
            item = self.queue.get()
            if item is None:
                break
            
            print(f"🔧 [DEBUG] Procesez element din coada: {item['label']} cu tastele: {item['keys']}")
            print(f"⏳ Filtru activ: {item['label']} pentru {self.filter_duration} secunde...")
            
            # Trimite tastele pentru a activa filtrul
            self.key_sender.send_sequence(item["keys"])
            print(f"✅ Taste apasate pentru activare: {item['keys']}")
            
            # Așteaptă durata filtrului
            time.sleep(self.filter_duration)
            
            # Închide filtrul la final
            if self.filter_close_key:
                close_keys = [self.filter_close_key] if isinstance(self.filter_close_key, str) else self.filter_close_key
                self.key_sender.send_sequence(close_keys)
                print(f"🔴 Taste apasate pentru inchidere: {close_keys}")
            else:
                # Dacă nu e definită tastă de închidere, apasă din nou tastele de activare
                self.key_sender.send_sequence(item["keys"])
                print(f"🔴 Taste apasate pentru inchidere: {item['keys']} (reapasare)")
            
            # Move to next in UI queue after filter duration
            if self.enable_ui_server:
                next_filter()
            
            print(f"✅ Filtru {item['label']} finalizat. Trecem la urmatorul...\n")
            self.queue.task_done()

    def process_tip(self, amount, username="Viewer"):
        """
        Proceseaza un tip si adauga filtrul corespunzator in coada
        Cauta in regulile configurate si gaseste filtrul potrivit pentru suma
        
        Args:
            amount: Suma de tokeni primita
            username: Numele utilizatorului care a dat tip-ul
        """
        # Parcurge toate regulile si gaseste prima care se potriveste cu suma
        for rule in self.key_rules:
            if rule["min"] <= amount <= rule["max"]:
                # Creeaza obiectul pentru coada
                item = {
                    "keys": rule["keys"],
                    "amount": amount,
                    "username": username,
                    "label": rule["label"],
                }
                
                # Adauga in coada UI pentru afisare
                if self.enable_ui_server:
                    add_to_queue(item['label'], item['username'], item['amount'])
                
                print(f"🔧 [DEBUG] Adaug in coada: {item}")
                self.queue.put(item)
                print(f"✅ [TIP] {amount} tokeni de la {username} -> Taste: {rule['label']}")
                return
        
        # Daca nu s-a gasit nicio regula pentru suma asta
        print(f"ℹ️ [TIP] {amount} tokeni primiti, dar nu exista taste configurate pentru aceasta suma.")

    def run_forever(self):
        """
        Porneste sistemul si il mentine activ la infinit
        Loop care tine aplicatia vie pana la Ctrl+C
        """
        self.start()
        while True:
            time.sleep(1)


def _str_to_bool(value):
    """
    Converteste un string sau valoare la boolean
    Recunoaste: "true", "1", "yes", "on" ca True (case-insensitive)
    
    Args:
        value: Valoarea de convertit (string, bool sau None)
    
    Returns:
        bool: True sau False
    """
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes", "on") if value is not None else False


def load_key_rules():
    """
    Incarca regulile de mapare intre sume de tokeni si filtre
    Returneaza lista cu 10 filtre, fiecare cu:
    - min/max: Range de tokeni
    - keys: Combinatie de taste pentru activare
    - label: Numele filtrului pentru afisare
    """
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
    """
    Incarca configuratia din fisierul .env
    Citeste URL-urile platformelor, setarile de taste si durata filtrelor
    
    Returns:
        dict: Dictionar cu toate setarile aplicatiei
    """
    load_dotenv()
    
    # Parse tasta de inchidere filtru - poate fi None, o tasta singura sau combinatie
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
    """
    Punct de intrare in aplicatie
    Incarca configuratia, afiseaza setarile si porneste sistemul
    """
    # Incarca configuratia din .env si regulile de taste
    config = load_config_from_env()
    key_rules = load_key_rules()

    # Afiseaza header-ul cu modul de functionare
    print("=" * 60)
    print(f"🚀 TIP → TASTE AUTOMATIZATE - MOD {config['environment'].upper()}")
    print("=" * 60)
    
    # Afiseaza platformele configurate
    print("\n📡 Platforme configurate:")
    if config["chaturbate_url"]:
        print(f"   ✅ Chaturbate: {config['chaturbate_url']}")
    else:
        print("   ❌ Chaturbate: Dezactivat")

    if config["stripchat_url"]:
        print(f"   ✅ Stripchat: {config['stripchat_url']}")
    else:
        print("   ❌ Stripchat: Dezactivat")

    if config["camsoda_url"]:
        print(f"   ✅ Camsoda: {config['camsoda_url']}")
    else:
        print("   ❌ Camsoda: Dezactivat")

    # Afiseaza setarile de taste
    print("\n⌨️  Setari taste:")
    print(f"   Hold: {config['hold_ms']}ms")
    print(f"   Delay: {config['delay_ms']}ms")
    print(f"   Durata filtru: {config['filter_duration']}s")
    print(f"   Tasta inchidere filtru: {config['filter_close_key'] or 'Reapasa tastele de activare'}")
    print("=" * 60 + "\n")

    # Creeaza instanta aplicatiei cu configuratia incarcata
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

    # Porneste aplicatia si tine-o activa
    try:
        app.run_forever()
    except KeyboardInterrupt:
        print("\n🛑 Aplicatie oprita de utilizator.")
    finally:
        app.stop()
