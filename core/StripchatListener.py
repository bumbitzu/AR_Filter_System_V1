"""
Stripchat Events API Listener
Proceseaza evenimente de tip din Stripchat si normalizeaza datele
Comunica cu API-ul Stripchat Events si extrage sumele de tokeni primite
"""
import time
import requests
import threading


class StripchatListener:
    """
    Listener pentru API-ul Stripchat Events
    Asculta evenimente de tip si le trimite la process_tip pentru procesare
    Suporta multiple formate de evenimente pentru compatibilitate
    """
    def __init__(self, api_url, process_tip_callback):
        """
        Initializeaza listener-ul Stripchat
        
        Args:
            api_url: URL-ul complet catre endpoint-ul Stripchat Events API
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
        print(f"✅ Listener Stripchat pornit pe {self.api_url}")

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
        Loop principal care interogeaza continuu API-ul Stripchat
        Implementeaza exponential backoff pentru retry (5s -> 10s -> 20s -> max 60s)
        Format asteptat: {"events": [{"type": "tip", "data": {"tokens": 100, "from": {"username": "user"}}}]}
        Suporta si formate alternative pentru compatibilitate (method, object, amount)
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
                    # Verifica daca e eveniment de tip (suporta "type" sau "method")
                    if event.get('type') == 'tip' or event.get('method') == 'tip':
                        # Normalizeaza datele (suporta "data" sau "object")
                        event_data = event.get('data', event.get('object', {}))
                        
                        # Stripchat foloseste "tokens" in loc de "amount"
                        amount = event_data.get('tokens', event_data.get('amount', 0))
                        
                        # Username poate fi in diferite locatii (from.username, user.name, etc)
                        user_obj = event_data.get('from', event_data.get('user', {}))
                        username = user_obj.get('username', user_obj.get('name', 'Anonymous'))
                        
                        # Trimite catre metoda centrala de procesare
                        self.process_tip(amount, username)
                
                # Resetam delay-ul la valoarea initiala dupa succes
                retry_delay = 5
                time.sleep(1)  # Polling interval de 1 secunda

            except requests.exceptions.Timeout:
                # Timeout dupa 5 secunde - API-ul nu raspunde
                print(f"⚠️ Stripchat API timeout. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)  # Dublez delay-ul
                
            except requests.exceptions.ConnectionError:
                # Eroare de conexiune - serverul nu e accesibil
                print(f"⚠️ Stripchat API connection failed. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except requests.exceptions.RequestException as e:
                # Alte erori HTTP (403, 404, 500, etc)
                print(f"⚠️ Stripchat API error: {str(e)}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except Exception as e:
                # Orice alta eroare neasteptata (JSON parse, etc)
                print(f"❌ Eroare neasteptata Stripchat: {str(e)}")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
