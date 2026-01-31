# Ghid Dezvoltare - AR Filter System V1

## Cuprins

1. [Setup Environment Dezvoltare](#setup-environment-dezvoltare)
2. [Structura Cod](#structura-cod)
3. [Conventii Coding](#conventii-coding)
4. [Testing](#testing)
5. [Debugging](#debugging)
6. [Adaugare Features](#adaugare-features)
7. [Optimizari Performance](#optimizari-performance)
8. [Contributie Guidelines](#contributie-guidelines)
9. [API Reference](#api-reference)
10. [Advanced Topics](#advanced-topics)

---

## Setup Environment Dezvoltare

### Prerequisites

- Python 3.8+
- Git
- VS Code sau PyCharm (recomandat)
- Cunostinte Python intermediate
- Familiaritate cu threading, REST APIs

### Setup Initial

**1. Clone repository:**
```bash
git clone https://github.com/yourusername/AR_Filter_System_V1.git
cd AR_Filter_System_V1
```

**2. Creaza development branch:**
```bash
git checkout -b dev/feature-name
```

**3. Setup virtual environment:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac
```

**4. Instaleaza dependente + dev tools:**
```bash
pip install -r requirements.txt
pip install pytest pylint black mypy  # Dev dependencies
```

**5. Configure IDE:**

**VS Code - settings.json:**
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

**PyCharm:**
- Settings → Python Interpreter → Add venv
- Settings → Tools → Python Integrated Tools → Testing: pytest

### Environment Files

**Development setup:**
```bash
.env.dev        # Development config
.env.test       # Testing config
.env.production # Production config (nu commit in git!)
```

**.gitignore essentials:**
```
.env
.env.production
__pycache__/
*.pyc
venv/
recordings/
output/
.vscode/
.idea/
```

---

## Structura Cod

### File Organization

```
AR_Filter_System_V1/
├── main.py                    # Entry point, FilterAutomation class
├── queue_ui_server.py         # Flask server pentru UI
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
│
├── core/                      # Core modules
│   ├── __init__.py
│   ├── ChaturbateListener.py
│   ├── StripchatListener.py
│   ├── CamsodaListener.py
│   └── base_listener.py       # (optional) Abstract base class
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── mock_server.py
│   ├── test_key_sender.py
│   ├── test_listeners.py      # Unit tests listeners
│   ├── test_queue.py          # Unit tests queue logic
│   └── test_integration.py    # Integration tests
│
├── templates/                 # HTML templates
│   ├── queue.html
│   └── menu.html
│
├── static/                    # (optional) Static assets
│   ├── css/
│   ├── js/
│   └── images/
│
├── docs/                      # Documentation
│   ├── README.md
│   ├── ARHITECTURA.md
│   ├── API_INTEGRATION.md
│   ├── INSTALARE.md
│   ├── UTILIZARE.md
│   └── DEZVOLTARE.md (this file)
│
└── scripts/                   # Utility scripts
    ├── setup.bat
    ├── run.bat
    ├── switch_env.bat
    └── deploy.bat
```

### Module Responsibilities

**main.py:**
- `FilterAutomation` class - Core orchestration
- `KeySender` class - Keyboard simulation
- Configuration loading
- Main entry point

**core/listeners:**
- Platform-specific API polling
- Event normalization
- Error handling & retry logic
- Each listener = separate thread

**queue_ui_server.py:**
- Flask application
- SSE implementation
- Routes & endpoints
- UI state management

**tests/:**
- Unit tests per component
- Integration tests
- Mock server pentru testing

---

## Conventii Coding

### Python Style Guide

Urmeaza **PEP 8** cu adaptari:

**Naming:**
```python
# Classes: PascalCase
class FilterAutomation:
    pass

# Functions/methods: snake_case
def process_queue(self):
    pass

# Constants: UPPER_SNAKE_CASE
TIP_TO_KEYS = {...}
POLL_INTERVAL = 5

# Private: _leading_underscore
def _normalize_event(self):
    pass
```

**Imports:**
```python
# Standard library
import os
import time
from queue import Queue

# Third-party
import requests
from flask import Flask
from pynput import keyboard

# Local
from core.ChaturbateListener import ChaturbateListener
```

**Docstrings:**
```python
def add_to_queue(self, event_data):
    """
    Adauga filtru in coada bazat pe event data.
    
    Args:
        event_data (dict): Event normalizat cu keys: platform, amount, tipper, etc.
        
    Returns:
        bool: True daca adaugare reusita, False altfel
        
    Example:
        >>> automation.add_to_queue({
        ...     "platform": "chaturbate",
        ...     "amount": 100,
        ...     "tipper": "user123"
        ... })
        True
    """
    pass
```

**Comments (Romana fara diacritice):**
```python
# Proceseaza elementele din coada in ordine prioritate
# Mai intai tips mari, apoi tips mici
while not self.stop_event.is_set():
    # Asteapta element din coada
    item = self.filter_queue.get(timeout=1)
```

### Type Hints

**Foloseste type hints pentru clarity:**
```python
from typing import Dict, List, Optional, Callable

def normalize_event(self, event: Dict) -> Optional[Dict]:
    """Normalizeaza event la format uniform"""
    pass

def start_listeners(self, callbacks: List[Callable]) -> None:
    """Start all platform listeners"""
    pass
```

### Error Handling

**Specific exceptions:**
```python
# ❌ Bad
try:
    data = response.json()
except Exception as e:
    print(f"Error: {e}")

# ✅ Good
try:
    data = response.json()
except requests.Timeout:
    print("[platform] Timeout API. Reincercare...")
except requests.ConnectionError as e:
    print(f"[platform] Eroare conexiune: {e}")
except ValueError as e:
    print(f"[platform] Eroare parsing JSON: {e}")
```

**Logging consistent:**
```python
# Format: [context] Message
print(f"[{self.platform}] Listener pornit pe {self.url}")
print(f"[worker] Procesez element: {item}")
print(f"[ui] Client conectat la SSE stream")
```

---

## Testing

### Test Structure

**Unit Tests:**
```python
# tests/test_key_sender.py
import pytest
from main import KeySender

class TestKeySender:
    def setup_method(self):
        """Setup inainte de fiecare test"""
        self.sender = KeySender()
    
    def test_parse_keys_single(self):
        """Test parsing o singura tasta"""
        keys = self.sender._parse_keys("ctrl")
        assert len(keys) == 1
        assert keys[0].name == "ctrl"
    
    def test_parse_keys_combination(self):
        """Test parsing combinatie taste"""
        keys = self.sender._parse_keys("ctrl+1")
        assert len(keys) == 2
        assert keys[0].name == "ctrl"
        assert keys[1] == "1"
    
    def test_send_keys_invalid(self):
        """Test handling taste invalide"""
        with pytest.raises(ValueError):
            self.sender.send_keys("invalid+combo")
```

**Integration Tests:**
```python
# tests/test_integration.py
import pytest
from main import FilterAutomation
from tests.mock_server import start_mock_server

class TestIntegration:
    @pytest.fixture
    def automation(self):
        """Fixture pentru FilterAutomation instance"""
        return FilterAutomation()
    
    def test_end_to_end_tip_processing(self, automation):
        """Test full flow: tip → queue → keys"""
        # Setup mock event
        event = {
            "platform": "chaturbate",
            "amount": 100,
            "tipper": "test_user"
        }
        
        # Add to queue
        automation.add_to_queue(event)
        
        # Verify queue
        assert automation.filter_queue.qsize() == 1
        
        # Process
        automation.process_queue()  # Single iteration
        
        # Verify queue empty
        assert automation.filter_queue.qsize() == 0
```

### Running Tests

**Run all tests:**
```bash
pytest
```

**Run specific test file:**
```bash
pytest tests/test_key_sender.py
```

**Run with coverage:**
```bash
pytest --cov=. --cov-report=html
```

**Run with verbose:**
```bash
pytest -v -s
```

### Mock Server Testing

**Start mock server in test:**
```python
import threading
from tests.mock_server import create_app

@pytest.fixture(scope="session")
def mock_server():
    """Start mock server pentru testing"""
    app = create_app()
    thread = threading.Thread(target=lambda: app.run(port=5000))
    thread.daemon = True
    thread.start()
    time.sleep(1)  # Wait pentru server sa porneasca
    yield
    # Cleanup (server se opreste automat, daemon=True)
```

---

## Debugging

### Logging Levels

**Implementare logging proper:**
```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] [%(name)s] %(message)s'
)

logger = logging.getLogger(__name__)

# Usage
logger.debug("Debug info")
logger.info("Info message")
logger.warning("Warning")
logger.error("Error occurred")
```

**Environment-based logging:**
```python
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

if DEBUG:
    logger.debug(f"Raw API response: {response.text}")
    logger.debug(f"Parsed data: {data}")
```

### Debugging Techniques

**1. Print Debugging (Quick & Dirty):**
```python
def add_to_queue(self, event_data):
    print(f"DEBUG: event_data = {event_data}")
    print(f"DEBUG: queue size before = {self.filter_queue.qsize()}")
    
    # Logic
    self.filter_queue.put(item)
    
    print(f"DEBUG: queue size after = {self.filter_queue.qsize()}")
```

**2. VS Code Debugger:**
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Main",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/main.py",
      "console": "integratedTerminal",
      "env": {
        "DEBUG": "true"
      }
    }
  ]
}
```

**Set breakpoints** in VS Code → F5 pentru debug.

**3. pdb (Python Debugger):**
```python
import pdb

def problematic_function(data):
    pdb.set_trace()  # Execution stops here
    
    # Inspect variables
    # Commands: n (next), c (continue), p variable (print), q (quit)
    result = process(data)
    return result
```

**4. Thread Debugging:**
```python
import threading

def debug_threads():
    """Print all active threads"""
    for thread in threading.enumerate():
        print(f"Thread: {thread.name}, Alive: {thread.is_alive()}")

# Call periodic
debug_threads()
```

### Common Debug Scenarios

**Problem: Listener nu primeste evenimente**
```python
# In listener._poll()
print(f"DEBUG: Polling {self.url}")
print(f"DEBUG: Response status: {response.status_code}")
print(f"DEBUG: Response body: {response.text}")

# Check:
# - URL corect?
# - Headers corecte?
# - API key valid?
```

**Problem: Queue nu se proceseaza**
```python
# In process_queue()
print(f"DEBUG: Queue size: {self.filter_queue.qsize()}")
print(f"DEBUG: Stop event set: {self.stop_event.is_set()}")
print(f"DEBUG: Worker thread alive: {self.worker_thread.is_alive()}")
```

**Problem: Taste nu se trimit**
```python
# In KeySender.send_keys()
print(f"DEBUG: Sending keys: {key_combination}")
print(f"DEBUG: Parsed keys: {keys}")
print(f"DEBUG: Pressing key: {key}")
```

---

## Adaugare Features

### Feature 1: Nou Platform Listener

**Step 1: Creaza listener class**
```python
# core/NewPlatformListener.py
import requests
import time
from typing import Callable, Dict, Optional

class NewPlatformListener:
    """
    Listener pentru NewPlatform Events API.
    
    Poll la interval regulat si notifica prin callback la evenimente noi.
    """
    
    def __init__(self, url: str, callback: Callable, poll_interval: int = 5):
        """
        Args:
            url: API endpoint URL
            callback: Functie apelata la event nou
            poll_interval: Secunde intre polls
        """
        self.url = url
        self.callback = callback
        self.poll_interval = poll_interval
        self.platform = "newplatform"
        self.stop_event = False
    
    def start(self):
        """Porneste polling in thread separat"""
        import threading
        self.thread = threading.Thread(target=self._poll, daemon=True)
        self.thread.start()
        print(f"[{self.platform}] Listener pornit pe {self.url}")
    
    def _poll(self):
        """Polling loop infinit"""
        while not self.stop_event:
            try:
                response = requests.get(self.url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                events = data.get("events", [])
                
                for event in events:
                    normalized = self._normalize_event(event)
                    if normalized:
                        self.callback(normalized)
                
            except requests.Timeout:
                print(f"[{self.platform}] Timeout API. Reincercare...")
            except requests.RequestException as e:
                print(f"[{self.platform}] Eroare API: {e}")
            except Exception as e:
                print(f"[{self.platform}] Eroare neasteptata: {e}")
            
            time.sleep(self.poll_interval)
    
    def _normalize_event(self, event: Dict) -> Optional[Dict]:
        """
        Normalizeaza event la format uniform.
        
        Args:
            event: Raw event de la API
            
        Returns:
            Normalized event dict sau None
        """
        try:
            return {
                "platform": self.platform,
                "amount": event["tip_amount"],
                "tipper": event["user"]["username"],
                "message": event.get("message", ""),
                "timestamp": time.time()
            }
        except (KeyError, TypeError) as e:
            print(f"[{self.platform}] Eroare normalizare: {e}")
            return None
    
    def stop(self):
        """Opreste listener"""
        self.stop_event = True
```

**Step 2: Update .env**
```bash
# .env.test
NEWPLATFORM_ENABLED=true
NEWPLATFORM_EVENTS_URL=http://127.0.0.1:5000/events/newplatform
NEWPLATFORM_POLL_INTERVAL=5
```

**Step 3: Integrate in main.py**
```python
# In FilterAutomation.__init__()
from core.NewPlatformListener import NewPlatformListener

if os.getenv("NEWPLATFORM_ENABLED") == "true":
    url = os.getenv("NEWPLATFORM_EVENTS_URL")
    listener = NewPlatformListener(
        url=url,
        callback=self.add_to_queue,
        poll_interval=int(os.getenv("NEWPLATFORM_POLL_INTERVAL", 5))
    )
    self.listeners.append(listener)
```

**Step 4: Test**
```bash
# Adauga in mock_server.py
@app.route('/events/newplatform')
def newplatform_events():
    return jsonify({
        "events": [{
            "tip_amount": 50,
            "user": {"username": "test_user"},
            "message": "Test"
        }]
    })
```

### Feature 2: Database Logging

**Step 1: Install dependency**
```bash
pip install sqlalchemy
```

**Step 2: Create database module**
```python
# db.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class TipEvent(Base):
    """Model pentru tip events"""
    __tablename__ = 'tip_events'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String)
    amount = Column(Integer)
    tipper = Column(String)
    message = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Setup
engine = create_engine('sqlite:///tips.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def log_tip(event_data):
    """Log tip in database"""
    session = Session()
    tip = TipEvent(
        platform=event_data["platform"],
        amount=event_data["amount"],
        tipper=event_data["tipper"],
        message=event_data.get("message", "")
    )
    session.add(tip)
    session.commit()
    session.close()
```

**Step 3: Integrate logging**
```python
# In main.py, add_to_queue()
from db import log_tip

def add_to_queue(self, event_data):
    # ... existing logic
    
    # Log in database
    try:
        log_tip(event_data)
    except Exception as e:
        print(f"[db] Eroare logging: {e}")
```

### Feature 3: Web Dashboard

**Step 1: Extinde Flask app**
```python
# queue_ui_server.py

@app.route('/dashboard')
def dashboard():
    """Dashboard cu statistici"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def api_stats():
    """API endpoint pentru statistici"""
    # Query database pentru stats
    from db import Session, TipEvent
    session = Session()
    
    total_tips = session.query(TipEvent).count()
    total_amount = session.query(func.sum(TipEvent.amount)).scalar() or 0
    top_tippers = session.query(
        TipEvent.tipper,
        func.sum(TipEvent.amount).label('total')
    ).group_by(TipEvent.tipper).order_by(desc('total')).limit(10).all()
    
    session.close()
    
    return jsonify({
        "total_tips": total_tips,
        "total_amount": total_amount,
        "top_tippers": [
            {"username": t[0], "amount": t[1]}
            for t in top_tippers
        ]
    })
```

**Step 2: Create template**
```html
<!-- templates/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - AR Filter System</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Dashboard Statistici</h1>
    
    <div id="stats">
        <p>Total Tips: <span id="total-tips">0</span></p>
        <p>Total Amount: <span id="total-amount">0</span> tokens</p>
    </div>
    
    <canvas id="top-tippers-chart"></canvas>
    
    <script>
        fetch('/api/stats')
            .then(r => r.json())
            .then(data => {
                document.getElementById('total-tips').textContent = data.total_tips;
                document.getElementById('total-amount').textContent = data.total_amount;
                
                // Chart
                new Chart(document.getElementById('top-tippers-chart'), {
                    type: 'bar',
                    data: {
                        labels: data.top_tippers.map(t => t.username),
                        datasets: [{
                            label: 'Total Tokens',
                            data: data.top_tippers.map(t => t.amount)
                        }]
                    }
                });
            });
    </script>
</body>
</html>
```

---

## Optimizari Performance

### 1. Queue Processing

**Problem: Queue lag la multe evenimente**

**Solution: Multiple workers**
```python
# In FilterAutomation.__init__()
self.num_workers = int(os.getenv("NUM_WORKERS", 3))
self.workers = []

for i in range(self.num_workers):
    worker = threading.Thread(
        target=self.process_queue,
        name=f"Worker-{i}",
        daemon=True
    )
    worker.start()
    self.workers.append(worker)
```

**Trade-off**: Taste simultane pot cauza issues. Adauga locking:
```python
self.key_lock = threading.Lock()

def apply_filter(self, item):
    with self.key_lock:
        self.key_sender.send_keys(item["keys"])
```

### 2. API Polling Optimization

**Adaptive polling:**
```python
def _poll(self):
    consecutive_empty = 0
    base_interval = self.poll_interval
    
    while not self.stop_event:
        events = self._fetch_events()
        
        if events:
            consecutive_empty = 0
            interval = base_interval  # Normal speed
        else:
            consecutive_empty += 1
            # Slow down daca nu sunt evenimente
            interval = min(base_interval * (1 + consecutive_empty * 0.5), 30)
        
        time.sleep(interval)
```

### 3. Memory Management

**Problem: Queue creste infinit**

**Solution: Max queue size**
```python
from queue import Queue

self.filter_queue = Queue(maxsize=100)

def add_to_queue(self, event_data):
    try:
        self.filter_queue.put(item, block=False)
    except Full:
        print("[queue] ATENTIE: Coada plina! Eliminat cel mai vechi item.")
        self.filter_queue.get()  # Remove oldest
        self.filter_queue.put(item)
```

### 4. UI Performance

**Problem: SSE connections consume resurse**

**Solution: Connection pooling & cleanup**
```python
import weakref

active_connections = weakref.WeakSet()

@app.route('/stream')
def stream():
    def event_stream():
        active_connections.add(current_connection)
        try:
            while True:
                # Stream logic
                yield data
        finally:
            active_connections.discard(current_connection)
    
    return Response(event_stream(), mimetype='text/event-stream')

# Periodic cleanup
def cleanup_connections():
    print(f"Active SSE connections: {len(active_connections)}")
```

---

## Contributie Guidelines

### Workflow

**1. Create Issue:**
- Descrie problema sau feature
- Include use case
- Attach screenshots daca relevant

**2. Create Branch:**
```bash
git checkout -b fix/issue-123
# sau
git checkout -b feature/new-platform-support
```

**Naming:**
- `fix/` - Bug fixes
- `feature/` - New features
- `refactor/` - Code refactoring
- `docs/` - Documentation

**3. Implement Changes:**
- Urmeaza coding conventions
- Adauga tests
- Update documentation

**4. Test:**
```bash
pytest
pylint main.py core/
black .  # Format code
```

**5. Commit:**
```bash
git add .
git commit -m "Fix: Rezolva issue #123 - timeout handling in listeners"
```

**Commit messages:**
- `Fix: ...` - Bug fix
- `Feature: ...` - New feature
- `Refactor: ...` - Code improvement
- `Docs: ...` - Documentation
- `Test: ...` - Test updates

**6. Push & Pull Request:**
```bash
git push origin fix/issue-123
```

Create PR pe GitHub cu:
- Descriere clara
- Link la issue
- Screenshots (daca UI changes)
- Test results

### Code Review Checklist

**Inainte de submit PR:**
- [ ] Codul urmeaza PEP 8
- [ ] Toate tests pass
- [ ] Adaugat tests pentru new code
- [ ] Documentation updated
- [ ] No hardcoded values (use .env)
- [ ] Error handling implementat
- [ ] Logging adaugat
- [ ] No breaking changes (sau documentate)

---

## API Reference

### FilterAutomation

```python
class FilterAutomation:
    """
    Clasa principala pentru orchestrare sistem.
    """
    
    def __init__(self):
        """Initialize automation system"""
        
    def start(self) -> None:
        """Porneste toate componentele"""
        
    def stop(self) -> None:
        """Opreste graceful sistemul"""
        
    def add_to_queue(self, event_data: Dict) -> bool:
        """
        Adauga filtru in coada.
        
        Args:
            event_data: Dict cu keys: platform, amount, tipper, message, timestamp
            
        Returns:
            True daca adaugare reusita
        """
        
    def process_queue(self) -> None:
        """Worker loop pentru procesare coada"""
        
    def trigger_manual_filter(self, filter_id: int) -> None:
        """
        Trigger manual filtru prin hotkey.
        
        Args:
            filter_id: ID filtru (1-9)
        """
```

### KeySender

```python
class KeySender:
    """
    Simuleaza keyboard input folosind pynput.
    """
    
    def __init__(self, key_delay: float = 0.1):
        """
        Args:
            key_delay: Delay intre press si release (seconds)
        """
        
    def send_keys(self, key_combination: str) -> None:
        """
        Trimite combinatie taste.
        
        Args:
            key_combination: String gen "ctrl+1", "alt+f4"
            
        Raises:
            ValueError: Daca taste invalide
        """
        
    def _parse_keys(self, key_combination: str) -> List:
        """Parse string taste in Key objects"""
```

### Platform Listeners

```python
class ChaturbateListener:
    """Listener pentru Chaturbate Events API"""
    
    def __init__(self, url: str, callback: Callable, poll_interval: int = 5):
        """
        Args:
            url: API endpoint
            callback: Function apelata cu normalized event
            poll_interval: Secunde intre polls
        """
        
    def start(self) -> None:
        """Start polling thread"""
        
    def stop(self) -> None:
        """Stop polling"""
        
    def _poll(self) -> None:
        """Internal polling loop"""
        
    def _normalize_event(self, event: Dict) -> Optional[Dict]:
        """
        Normalizeaza event la format uniform.
        
        Returns:
            Dict cu keys: platform, amount, tipper, message, timestamp
        """
```

### Queue UI Server

```python
def create_app() -> Flask:
    """Create Flask application"""

@app.route('/queue')
def queue_page():
    """Pagina UI pentru vizualizare coada"""

@app.route('/stream')
def stream():
    """SSE endpoint pentru updates real-time"""

@app.route('/queue-data')
def queue_data():
    """JSON API cu stare curenta coada"""
```

---

## Advanced Topics

### Custom Event Filters

**Filtrare evenimente inainte de queue:**
```python
class FilterAutomation:
    def __init__(self):
        # ...
        self.event_filters = [
            self._filter_min_amount,
            self._filter_blacklist
        ]
    
    def _filter_min_amount(self, event: Dict) -> bool:
        """Accepta doar tips > 10 tokens"""
        return event["amount"] >= 10
    
    def _filter_blacklist(self, event: Dict) -> bool:
        """Blocheaza useri din blacklist"""
        blacklist = ["banned_user1", "banned_user2"]
        return event["tipper"] not in blacklist
    
    def add_to_queue(self, event_data):
        # Apply filters
        for filter_func in self.event_filters:
            if not filter_func(event_data):
                print(f"Event filtrat: {event_data}")
                return False
        
        # Continue cu logica normala
        # ...
```

### Plugin System

**Architecture pentru extensibility:**
```python
# plugins/base.py
from abc import ABC, abstractmethod

class FilterPlugin(ABC):
    """Base class pentru plugins"""
    
    @abstractmethod
    def on_tip_received(self, event: Dict) -> None:
        """Called cand tip nou e primit"""
        pass
    
    @abstractmethod
    def on_filter_applied(self, filter_id: int) -> None:
        """Called dupa ce filtru e aplicat"""
        pass

# plugins/discord_notifier.py
class DiscordNotifier(FilterPlugin):
    """Plugin pentru notificari Discord"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def on_tip_received(self, event: Dict):
        """Trimite notificare Discord"""
        import requests
        requests.post(self.webhook_url, json={
            "content": f"Tip primit: {event['amount']} tokens de la {event['tipper']}"
        })
    
    def on_filter_applied(self, filter_id: int):
        pass  # No action needed

# In main.py
class FilterAutomation:
    def __init__(self):
        # ...
        self.plugins = []
        self._load_plugins()
    
    def _load_plugins(self):
        """Load configured plugins"""
        if os.getenv("DISCORD_WEBHOOK_URL"):
            plugin = DiscordNotifier(os.getenv("DISCORD_WEBHOOK_URL"))
            self.plugins.append(plugin)
    
    def add_to_queue(self, event_data):
        # Notify plugins
        for plugin in self.plugins:
            plugin.on_tip_received(event_data)
        
        # Continue normal logic
```

### Distributed Queue (Redis)

**Scale beyond single machine:**
```python
# Requires: pip install redis
import redis
import json

class RedisQueue:
    """Redis-backed queue pentru distributed processing"""
    
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)
        self.queue_key = "ar_filter_queue"
    
    def put(self, item: Dict) -> None:
        """Add item to queue"""
        self.redis.rpush(self.queue_key, json.dumps(item))
    
    def get(self, timeout: int = 1) -> Optional[Dict]:
        """Get item from queue (blocking)"""
        result = self.redis.blpop(self.queue_key, timeout=timeout)
        if result:
            return json.loads(result[1])
        return None
    
    def qsize(self) -> int:
        """Get queue size"""
        return self.redis.llen(self.queue_key)

# In main.py
from redis_queue import RedisQueue

class FilterAutomation:
    def __init__(self):
        # Use Redis queue instead of Python Queue
        self.filter_queue = RedisQueue()
```

---

## Resources

### Documentation Links

- [Python Docs](https://docs.python.org/3/)
- [Flask Docs](https://flask.palletsprojects.com/)
- [pynput Docs](https://pynput.readthedocs.io/)
- [pytest Docs](https://docs.pytest.org/)

### Recommended Reading

- "Fluent Python" by Luciano Ramalho
- "Effective Python" by Brett Slatkin
- "Python Testing with pytest" by Brian Okken

### Tools

- **VS Code**: IDE recomandat
- **Black**: Code formatter
- **Pylint**: Linter
- **mypy**: Type checker
- **pytest**: Testing framework

---

## Concluzii

Acest ghid acopera fundamentele dezvoltarii pentru AR Filter System. Pentru intrebari suplimentare:

1. Check documentatia existenta
2. Review codul existent pentru patterns
3. Deschide GitHub Issue pentru clarificari

Happy coding! 🚀
