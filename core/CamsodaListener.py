"""
Camsoda External API Listener
Procesează events din Camsoda și normalizează datele pentru process_tip()
"""
import time
import requests
import threading


class CamsodaListener:
    def __init__(self, api_url, process_tip_callback):
        """
        Args:
            api_url (str): URL-ul endpoint-ului Camsoda External API
            process_tip_callback (callable): Funcția centrală process_tip(amount, username)
        """
        self.api_url = api_url
        self.process_tip = process_tip_callback
        self.running = False
        self.thread = None

    def start(self):
        """Pornește thread-ul de ascultare"""
        self.running = True
        self.thread = threading.Thread(target=self._fetch_events, daemon=True)
        self.thread.start()
        print(f"✅ Camsoda listener started on {self.api_url}")

    def stop(self):
        """Oprește thread-ul de ascultare"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _fetch_events(self):
        """Thread principal care interoghează API-ul Camsoda"""
        retry_delay = 5
        max_retry_delay = 60
        
        while self.running:
            try:
                response = requests.get(self.api_url, timeout=5)
                response.raise_for_status()
                data = response.json()

                # Procesare events Camsoda
                # Format așteptat: {"events": [{"event_type": "tip", "tip_amount": 100, "tipper": {"name": "user123"}}]}
                for event in data.get('events', []):
                    event_type = event.get('event_type', event.get('type', event.get('method', '')))
                    
                    if event_type == 'tip':
                        # Normalizare date Camsoda (suportă multiple formate)
                        # Camsoda poate folosi: "tip_amount", "amount", "tokens"
                        amount = event.get('tip_amount', event.get('amount', event.get('tokens', 0)))
                        
                        # Username poate fi în diferite locații
                        # Camsoda folosește "tipper" sau "user"
                        tipper_obj = event.get('tipper', event.get('user', event.get('from', {})))
                        
                        # Extrage username/name
                        if isinstance(tipper_obj, dict):
                            username = tipper_obj.get('name', tipper_obj.get('username', 'Anonymous'))
                        elif isinstance(tipper_obj, str):
                            username = tipper_obj
                        else:
                            username = 'Anonymous'
                        
                        # Trimite către metoda centrală
                        self.process_tip(amount, username)
                
                # Reset retry delay dacă conexiunea a avut succes
                retry_delay = 5
                time.sleep(1)  # Polling interval

            except requests.exceptions.Timeout:
                print(f"⚠️ Camsoda API timeout. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except requests.exceptions.ConnectionError:
                print(f"⚠️ Camsoda API connection failed. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Camsoda API error: {str(e)}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except Exception as e:
                print(f"❌ Camsoda unexpected error: {str(e)}")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
