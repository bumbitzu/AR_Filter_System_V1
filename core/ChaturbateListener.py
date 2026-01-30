"""
Chaturbate Events API Listener
Procesează events din Chaturbate și normalizează datele pentru process_tip()
"""
import time
import requests
import threading


class ChaturbateListener:
    def __init__(self, api_url, process_tip_callback):
        """
        Args:
            api_url (str): URL-ul endpoint-ului Chaturbate Events API
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
        print(f"✅ Chaturbate listener started on {self.api_url}")

    def stop(self):
        """Oprește thread-ul de ascultare"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _fetch_events(self):
        """Thread principal care interoghează API-ul Chaturbate"""
        retry_delay = 5
        max_retry_delay = 60
        
        while self.running:
            try:
                response = requests.get(self.api_url, timeout=5)
                response.raise_for_status()
                data = response.json()

                # Procesare events
                for event in data.get('events', []):
                    # Format 1: User Provided / Official ("tip": {"tokens": 25})
                    if 'tip' in event:
                        amount = event.get('tip', {}).get('tokens', 0)
                        # User explicitly requested NOT to extract username
                        self.process_tip(amount, "Viewer")
                    
                    # Format 2: Old / Legacy ("method": "tip", "object": {"amount": 25})
                    elif event.get('method') == 'tip':
                        amount = event.get('object', {}).get('amount', 0)
                        self.process_tip(amount, "Viewer")
                
                # Reset retry delay dacă conexiunea a avut succes
                retry_delay = 5
                time.sleep(1)  # Polling interval

            except requests.exceptions.Timeout:
                print(f"⚠️ Chaturbate API timeout. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except requests.exceptions.ConnectionError:
                print(f"⚠️ Chaturbate API connection failed. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Chaturbate API error: {str(e)}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except Exception as e:
                print(f"❌ Chaturbate unexpected error: {str(e)}")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
