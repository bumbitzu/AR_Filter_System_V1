"""
Camsoda External API Listener
Proceseaza evenimente de tip din Camsoda si normalizeaza datele
Comunica cu API-ul Camsoda External si extrage sumele de tokeni primite
"""
import time
import requests
import threading


class CamsodaListener:
    """
    Listener pentru API-ul Camsoda External
    Asculta evenimente de tip si le trimite la process_tip pentru procesare
    Suporta multiple formate de evenimente pentru compatibilitate
    """
    def __init__(self, api_url, process_tip_callback):
        """
        Initializeaza listener-ul Camsoda
        
        Args:
            api_url: URL-ul complet catre endpoint-ul Camsoda External API
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
        print(f"✅ Listener Camsoda pornit pe {self.api_url}")

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
        Loop principal care interogeaza continuu API-ul Camsoda
        Implementeaza exponential backoff pentru retry (5s -> 10s -> 20s -> max 60s)
        Format asteptat: {"events": [{"event_type": "tip", "tip_amount": 100, "tipper": {"name": "user"}}]}
        Suporta si formate alternative pentru compatibilitate (type, method, amount, tokens)
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
                    # Cauta tipul evenimentului in multiple locatii (event_type, type, method)
                    event_type = event.get('event_type', event.get('type', event.get('method', '')))
                    
                    if event_type == 'tip':
                        # Normalizeaza suma (Camsoda poate folosi: tip_amount, amount, tokens)
                        amount = event.get('tip_amount', event.get('amount', event.get('tokens', 0)))
                        
                        # Extrage obiectul cu informatii despre tipper
                        # Camsoda foloseste "tipper" sau "user"
                        tipper_obj = event.get('tipper', event.get('user', event.get('from', {})))
                        
                        # Extrage username-ul din obiectul tipper
                        if isinstance(tipper_obj, dict):
                            # Daca e dictionar, cauta "name" sau "username"
                            username = tipper_obj.get('name', tipper_obj.get('username', 'Anonymous'))
                        elif isinstance(tipper_obj, str):
                            # Daca e string direct, foloseste-l
                            username = tipper_obj
                        else:
                            # Fallback daca nu gasim username
                            username = 'Anonymous'
                        
                        # Trimite catre metoda centrala de procesare
                        self.process_tip(amount, username)
                
                # Resetam delay-ul la valoarea initiala dupa succes
                retry_delay = 5
                time.sleep(1)  # Polling interval de 1 secunda

            except requests.exceptions.Timeout:
                # Timeout dupa 5 secunde - API-ul nu raspunde
                print(f"⚠️ Timeout API Camsoda. Reincercare in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)  # Dublez delay-ul
                
            except requests.exceptions.ConnectionError:
                # Eroare de conexiune - serverul nu e accesibil
                print(f"⚠️ Esec conexiune API Camsoda. Reincercare in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except requests.exceptions.RequestException as e:
                # Alte erori HTTP (403, 404, 500, etc)
                print(f"⚠️ Eroare API Camsoda: {str(e)}. Reincercare in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except Exception as e:
                # Orice alta eroare neasteptata (JSON parse, etc)
                print(f"❌ Eroare neasteptata Camsoda: {str(e)}")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
