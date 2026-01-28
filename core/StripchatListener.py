"""
Stripchat Events API Listener
Procesează events din Stripchat și normalizează datele pentru process_tip()
"""
import time
import requests
import threading


class StripchatListener:
    def __init__(self, api_url, process_tip_callback):
        """
        Args:
            api_url (str): URL-ul endpoint-ului Stripchat Events API
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
        print(f"✅ Stripchat listener started on {self.api_url}")

    def stop(self):
        """Oprește thread-ul de ascultare"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _fetch_events(self):
        """Thread principal care interoghează API-ul Stripchat"""
        retry_delay = 5
        max_retry_delay = 60
        
        while self.running:
            try:
                response = requests.get(self.api_url, timeout=5)
                response.raise_for_status()
                data = response.json()

                # Procesare events Stripchat
                # Format așteptat: {"events": [{"type": "tip", "data": {"tokens": 100, "from": {"username": "user123"}}}]}
                for event in data.get('events', []):
                    if event.get('type') == 'tip' or event.get('method') == 'tip':
                        # Normalizare date Stripchat (suportă ambele formate)
                        event_data = event.get('data', event.get('object', {}))
                        
                        # Stripchat folosește "tokens" in loc de "amount"
                        amount = event_data.get('tokens', event_data.get('amount', 0))
                        
                        # Username poate fi în diferite locații
                        user_obj = event_data.get('from', event_data.get('user', {}))
                        username = user_obj.get('username', user_obj.get('name', 'Anonymous'))
                        
                        # Trimite către metoda centrală
                        self.process_tip(amount, username)
                
                # Reset retry delay dacă conexiunea a avut succes
                retry_delay = 5
                time.sleep(1)  # Polling interval

            except requests.exceptions.Timeout:
                print(f"⚠️ Stripchat API timeout. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except requests.exceptions.ConnectionError:
                print(f"⚠️ Stripchat API connection failed. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Stripchat API error: {str(e)}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except Exception as e:
                print(f"❌ Stripchat unexpected error: {str(e)}")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
