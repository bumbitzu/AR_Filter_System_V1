"""
Chaturbate Events API Listener
Proceseaza evenimente de tip din Chaturbate si normalizeaza datele
Comunica cu API-ul Chaturbate Events si extrage sumele de tokeni primite
"""
import time
import requests
import threading


class ChaturbateListener:
    """
    Listener pentru API-ul Chaturbate Events
    Asculta evenimente de tip si le trimite la process_tip pentru procesare
    Suporta doua formate de evenimente (user-provided si legacy)
    """
    def __init__(self, api_url, process_tip_callback):
        """
        Initializeaza listener-ul Chaturbate
        
        Args:
            api_url: URL-ul complet catre endpoint-ul Chaturbate Events API
            process_tip_callback: Functie callback process_tip(amount, username)
        """
        self.api_url = api_url
        self.process_tip = process_tip_callback
        self.running = False
        self.thread = None

    def start(self):
        """
        Porneste thread-ul de ascultare in background
        Thread-ul este daemon, deci se inchide automat cand se opreste programul
        """
        self.running = True
        self.thread = threading.Thread(target=self._fetch_events, daemon=True)
        self.thread.start()
        print(f"✅ Listener Chaturbate pornit pe {self.api_url}")

    def stop(self):
        """
        Opreste thread-ul de ascultare
        Asteapta maximum 2 secunde pentru inchidere
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _fetch_events(self):
        """
        Loop principal care interogeaza continuu API-ul Chaturbate
        Implementeaza exponential backoff pentru retry (5s -> 10s -> 20s -> max 60s)
        Suporta 2 formate de evenimente:
        - Format User-Provided: {"tip": {"tokens": 25}}
        - Format Legacy: {"method": "tip", "object": {"amount": 25}}
        """
        retry_delay = 5  # Delay initial pentru retry
        max_retry_delay = 60  # Maximum delay intre retry-uri
        
        while self.running:
            try:
                # Trimite request HTTP GET cu timeout de 5 secunde
                response = requests.get(self.api_url, timeout=5)
                response.raise_for_status()  # Arunca exceptie daca status != 200
                data = response.json()

                # Proceseaza toate evenimentele din raspuns
                for event in data.get('events', []):
                    # Format 1: User Provided / Official ("tip": {"tokens": 25})
                    if 'tip' in event:
                        amount = event.get('tip', {}).get('tokens', 0)
                        # Nu extragem username-ul la cererea userului
                        self.process_tip(amount, "Viewer")
                    
                    # Format 2: Old / Legacy ("method": "tip", "object": {"amount": 25})
                    elif event.get('method') == 'tip':
                        amount = event.get('object', {}).get('amount', 0)
                        self.process_tip(amount, "Viewer")
                
                # Resetam delay-ul la valoarea initiala dupa succes
                retry_delay = 5
                time.sleep(1)  # Polling interval de 1 secunda

            except requests.exceptions.Timeout:
                # Timeout dupa 5 secunde - API-ul nu raspunde
                print(f"⚠️ Timeout API Chaturbate. Reincercare in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)  # Dublez delay-ul
                
            except requests.exceptions.ConnectionError:
                # Eroare de conexiune - serverul nu e accesibil
                print(f"⚠️ Esec conexiune API Chaturbate. Reincercare in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except requests.exceptions.RequestException as e:
                # Alte erori HTTP (403, 404, 500, etc)
                print(f"⚠️ Eroare API Chaturbate: {str(e)}. Reincercare in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except Exception as e:
                # Orice alta eroare neasteptata (JSON parse, etc)
                print(f"❌ Eroare neasteptata Chaturbate: {str(e)}")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
