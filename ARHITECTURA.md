# Arhitectura Sistem - AR Filter System V1

## Cuprins

1. [Prezentare Generala](#prezentare-generala)
2. [Componente Principale](#componente-principale)
3. [Flow de Date](#flow-de-date)
4. [Design Patterns](#design-patterns)
5. [Threading Model](#threading-model)
6. [Queue Management](#queue-management)
7. [Event Processing](#event-processing)
8. [UI Architecture](#ui-architecture)
9. [Extensibilitate](#extensibilitate)

---

## Prezentare Generala

AR Filter System V1 este construit pe o arhitectura modulara, bazata pe evenimente, cu componente decuplate care comunica prin cozi si evenimente. Sistemul foloseste un model producer-consumer pentru gestionarea evenimentelor de tip si aplicarea filtrelor.

### Principii Arhitecturale

- **Separation of Concerns**: Fiecare modul are responsabilitate clara
- **Single Responsibility**: Clase cu scop bine definit
- **DRY (Don't Repeat Yourself)**: Cod reutilizabil si abstractizat
- **Loose Coupling**: Dependente minime intre componente
- **High Cohesion**: Functionalitati inrudite grupate impreuna

---

## Componente Principale

### 1. FilterAutomation (main.py)

**Responsabilitati:**
- Orchestrare generala sistem
- Gestionare coada filtre
- Procesare evenimente tip
- Coordonare listeners si workers

**Atribute Cheie:**
```python
filter_queue: Queue          # Coada principala filtre
listeners: List[Thread]      # Lista thread-uri listeners
worker_thread: Thread        # Thread worker procesare
keyboard_listener: Listener  # Global keyboard listener
```

**Metode Importante:**
- `start()`: Porneste toate componentele sistem
- `add_to_queue()`: Adauga element in coada
- `process_queue()`: Worker procesare coada
- `stop()`: Opreste graceful toate thread-urile

### 2. Platform Listeners (core/)

**Arhitectura Comuni:**
Toti listeners implementeaza acelasi pattern:

```python
class PlatformListener:
    def __init__(self, url, callback, poll_interval)
    def start(self)            # Thread infinit polling
    def _poll(self)            # Logica polling API
    def _normalize_event()     # Conversie la format uniform
```

#### ChaturbateListener
- Poll endpoint: `/events/{broadcaster}`
- Retry logic: Exponential backoff
- Suporta 2 formate evenimente (legacy si nou)

#### StripchatListener
- Poll endpoint: `/v1/events`
- Multi-format support
- Error handling robust

#### CamsodaListener
- Poll endpoint: External API
- Tipper extraction flexibila
- Timeout handling

### 3. KeySender (main.py)

**Responsabilitati:**
- Simulare keyboard input
- Presare combinatii taste
- Delay-uri configurabile

**Metode:**
```python
send_keys(key_combination)  # Trimite o combinatie de taste
_parse_keys()               # Parseaza string taste in obiecte Key
_press_key()                # Apasa o tasta
_release_key()              # Elibereaza o tasta
```

### 4. Queue UI Server (queue_ui_server.py)

**Responsabilitati:**
- Server Flask pentru UI web
- Server-Sent Events (SSE) pentru updates real-time
- API endpoints pentru date coada

**Endpoints:**
- `GET /queue`: Pagina UI vizualizare coada
- `GET /menu`: Overlay menu (optional)
- `GET /stream`: SSE stream pentru updates
- `GET /queue-data`: JSON cu stare coada

---

## Flow de Date

### 1. Event Flow (Tip Primit)

```
┌─────────────────────────────────────────────────────┐
│ 1. API Platform (Chaturbate/Stripchat/Camsoda)     │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP Response
                       ↓
┌─────────────────────────────────────────────────────┐
│ 2. Platform Listener                                │
│    - Poll API                                       │
│    - Parse response                                 │
│    - Extract tip data                               │
└──────────────────────┬──────────────────────────────┘
                       │ Normalized Event
                       ↓
┌─────────────────────────────────────────────────────┐
│ 3. Event Normalization                              │
│    {                                                │
│      "platform": "chaturbate",                      │
│      "amount": 100,                                 │
│      "tipper": "username",                          │
│      "message": "tip message",                      │
│      "timestamp": 1234567890                        │
│    }                                                │
└──────────────────────┬──────────────────────────────┘
                       │ Callback Invocation
                       ↓
┌─────────────────────────────────────────────────────┐
│ 4. FilterAutomation.add_to_queue()                  │
│    - Map amount → filter_id                         │
│    - Calculate priority                             │
│    - Add to queue                                   │
└──────────────────────┬──────────────────────────────┘
                       │ Queue.put()
                       ↓
┌─────────────────────────────────────────────────────┐
│ 5. Priority Queue                                   │
│    [(priority1, filter1), (priority2, filter2), ...]│
└──────────────────────┬──────────────────────────────┘
                       │ Queue.get() (FIFO)
                       ↓
┌─────────────────────────────────────────────────────┐
│ 6. Worker Thread (process_queue)                    │
│    - Get next item                                  │
│    - Log processing                                 │
│    - Invoke KeySender                               │
└──────────────────────┬──────────────────────────────┘
                       │ send_keys()
                       ↓
┌─────────────────────────────────────────────────────┐
│ 7. KeySender                                        │
│    - Parse key combination                          │
│    - Simulate keyboard input                        │
│    - Apply delays                                   │
└──────────────────────┬──────────────────────────────┘
                       │ pynput Controller
                       ↓
┌─────────────────────────────────────────────────────┐
│ 8. Operating System                                 │
│    - Process keyboard events                        │
│    - Forward to active application                  │
└─────────────────────────────────────────────────────┘
                       │
                       ↓
              [AR Filter Activated]
```

### 2. UI Update Flow

```
┌─────────────────┐
│ Queue Modified  │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────┐
│ broadcast_queue_update()    │
│ (in queue_ui_server.py)     │
└────────┬────────────────────┘
         │ SSE Message
         ↓
┌─────────────────────────────┐
│ EventSource (Browser)       │
│ - Receives message          │
│ - Parses JSON data          │
└────────┬────────────────────┘
         │ JavaScript Update
         ↓
┌─────────────────────────────┐
│ DOM Update (queue.html)     │
│ - Update queue list         │
│ - Update stats              │
│ - Animate changes           │
└─────────────────────────────┘
```

---

## Design Patterns

### 1. Producer-Consumer Pattern

**Implementare:**
- **Producers**: Platform Listeners (produce evenimente tip)
- **Queue**: Python Queue (thread-safe)
- **Consumer**: Worker Thread (consuma si proceseaza)

**Avantaje:**
- Decuplare producatori si consumatori
- Buffer pentru rate limiting
- Thread-safe operations

### 2. Observer Pattern

**Implementare:**
- **Subject**: Platform Listeners
- **Observers**: FilterAutomation (callback function)
- **Notification**: Callback invocation la event nou

### 3. Strategy Pattern

**Implementare:**
- **Context**: Event normalization
- **Strategies**: Fiecare listener are propria strategie de parsing
- **Flexibilitate**: Usor de adaugat platforme noi

### 4. Singleton Pattern (Implicit)

**Implementare:**
- `FilterAutomation` - o singura instanta per run
- `QueueUIServer` - un singur server Flask

---

## Threading Model

### Thread Structure

```
Main Thread
├── Listener Thread 1 (Chaturbate)
├── Listener Thread 2 (Stripchat)
├── Listener Thread 3 (Camsoda)
├── Worker Thread (Queue Processing)
├── Keyboard Listener Thread (pynput)
└── Flask Server Thread (UI)
    └── SSE Connection Threads (per client)
```

### Thread Safety

**Thread-Safe Components:**
- `Queue.Queue`: Built-in thread-safe queue
- Listeners: Independent, no shared state
- KeySender: Sequential operations, no race conditions

**Synchronization:**
- Queue foloseste internal locks
- Event flags pentru stop signals
- Graceful shutdown cu thread.join()

### Lifecycle Management

**Start Sequence:**
```python
1. Initialize FilterAutomation
2. Start Flask server (daemon thread)
3. Start platform listeners (daemon threads)
4. Start worker thread (daemon thread)
5. Start keyboard listener (pynput)
6. Enter main loop / wait for Ctrl+C
```

**Stop Sequence:**
```python
1. Catch KeyboardInterrupt
2. Set stop event flags
3. Stop keyboard listener
4. Join worker thread
5. Join listener threads
6. Cleanup resources
```

---

## Queue Management

### Queue Structure

```python
filter_queue = Queue()

# Element format
queue_item = (priority, filter_data)

# filter_data structure
{
    "filter_id": 1,
    "keys": "ctrl+1",
    "amount": 100,
    "tipper": "username",
    "platform": "chaturbate"
}
```

### Priority System

**Reguli:**
- Priority = Negative amount (mai mare = prioritate mai mare)
- FIFO pentru aceeasi prioritate
- No duplicate filtering (permite duplicate intentionat)

**Exemplu:**
```python
# Tip 500 tokens → priority = -500 (high)
# Tip 100 tokens → priority = -100 (low)
# Queue: [(-500, filter1), (-100, filter2)]
```

### Processing Strategy

```python
def process_queue(self):
    while not self.stop_event.is_set():
        try:
            priority, item = self.filter_queue.get(timeout=1)
            self.apply_filter(item)
            self.filter_queue.task_done()
        except Empty:
            continue
```

---

## Event Processing

### Event Normalization

**Format Uniform:**
```python
{
    "platform": str,      # "chaturbate" | "stripchat" | "camsoda"
    "amount": int,        # Suma tip in tokens
    "tipper": str,        # Username tipper
    "message": str,       # Mesaj tip (optional)
    "timestamp": float    # Unix timestamp
}
```

**Mapping Platform-Specific:**

**Chaturbate:**
```python
# Format 1 (legacy)
event["tip"]["tokens"] → amount
event["tip"]["from_username"] → tipper

# Format 2 (nou)
event["amount"] → amount
event["from_user"]["username"] → tipper
```

**Stripchat:**
```python
# Multi-format support
event["amount"] OR event["tip"]["amount"] → amount
event["user"]["username"] → tipper
```

**Camsoda:**
```python
event["amount"] → amount
event["tipper"]["username"] OR event["user"] → tipper
```

### Filter Mapping

**Configuration:**
```python
TIP_TO_KEYS = {
    10: "ctrl+1",    # 10 tokens → Filter 1
    20: "ctrl+2",    # 20 tokens → Filter 2
    50: "ctrl+3",    # 50 tokens → Filter 3
    # ... extensibil
}
```

**Mapping Logic:**
```python
def get_keys_for_amount(amount):
    return TIP_TO_KEYS.get(amount, None)
```

---

## UI Architecture

### Frontend (queue.html)

**Tehnologii:**
- HTML5
- CSS3 (responsive design)
- Vanilla JavaScript (no frameworks)
- EventSource API (SSE)

**Componente:**
```html
├── Header (titlu + stats)
├── Queue List (lista items)
│   ├── Queue Item 1
│   ├── Queue Item 2
│   └── ...
└── Footer (status)
```

**Real-Time Updates:**
```javascript
const eventSource = new EventSource('/stream');
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateQueueDisplay(data);
};
```

### Backend (queue_ui_server.py)

**Flask Routes:**
```python
@app.route('/queue')          # GET - UI page
@app.route('/stream')         # GET - SSE stream
@app.route('/queue-data')     # GET - JSON data
```

**SSE Implementation:**
```python
def event_stream():
    while True:
        with queue_lock:
            data = get_queue_snapshot()
        yield f"data: {json.dumps(data)}\n\n"
        time.sleep(1)
```

**Thread Safety:**
```python
queue_lock = threading.Lock()

# Access queue cu lock
with queue_lock:
    queue_data = list(automation.filter_queue.queue)
```

---

## Extensibilitate

### Adaugare Platform Noua

**Pasi:**

1. **Creaza Listener:**
```python
# core/NewPlatformListener.py
class NewPlatformListener:
    def __init__(self, url, callback, poll_interval=5):
        # Initialize
        
    def start(self):
        # Start polling thread
        
    def _poll(self):
        # Poll API logic
        
    def _normalize_event(self, raw_event):
        # Return normalized format
```

2. **Update Configuration:**
```python
# In .env
NEW_PLATFORM_ENABLED=true
NEW_PLATFORM_URL=https://api.newplatform.com/events
```

3. **Integrate in main.py:**
```python
from core.NewPlatformListener import NewPlatformListener

# In FilterAutomation.__init__()
if os.getenv("NEW_PLATFORM_ENABLED") == "true":
    listener = NewPlatformListener(
        url=os.getenv("NEW_PLATFORM_URL"),
        callback=self.add_to_queue
    )
    self.listeners.append(listener)
```

### Adaugare Filter Nou

**Pasi:**

1. **Update Mapping:**
```python
# In main.py
TIP_TO_KEYS = {
    # ... existing
    100: "ctrl+9",  # New filter
}
```

2. **Update Manual Triggers:**
```python
# In setup_manual_triggers()
keyboard.add_hotkey('ctrl+9', 
    lambda: self.trigger_manual_filter(9))
```

3. **Documentare:**
```markdown
# In UTILIZARE.md
- Ctrl+9: Filter special 100 tokens
```

### Customizare UI

**CSS Themes:**
```css
/* templates/queue.html - in <style> */
:root {
    --primary-color: #your-color;
    --background: #your-bg;
}
```

**Template Customization:**
```html
<!-- Modifica queue.html -->
<div class="custom-component">
    <!-- Your HTML -->
</div>
```

---

## Performanta

### Optimizari Implementate

1. **Polling Intervals:** Configurabile per platform
2. **Thread Pooling:** Reuse thread-uri pentru listeners
3. **Queue Buffering:** Absorbe spike-uri trafic
4. **Lazy Loading:** UI se incarca doar la access

### Scalabilitate

**Limitari Curente:**
- Single-instance design
- Local queue (non-distributed)
- In-memory state (no persistence)

**Potential Improvements:**
- Redis queue pentru distributed processing
- Database pentru persistence
- Load balancing pentru multiple instances

---

## Securitate

### Consideratii

1. **API Keys:** Stocate in .env (nu in git)
2. **Local Server:** UI accesibil doar localhost
3. **Input Validation:** Parsing defensiv evenimente
4. **Error Handling:** No stack traces expuse in production

### Best Practices

- Nu commit .env in repository
- Rotate API keys periodic
- Monitor loguri pentru activitate suspicioasa
- Test cu mock server inainte de production

---

## Diagrame

### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│                 AR Filter System                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────┐      ┌──────────────────┐      │
│  │ Platform       │      │ FilterAutomation │      │
│  │ Listeners      │─────▶│    (Core)        │      │
│  │ - Chaturbate   │      │  - Queue Mgmt    │      │
│  │ - Stripchat    │      │  - Processing    │      │
│  │ - Camsoda      │      │  - Coordination  │      │
│  └────────────────┘      └────────┬─────────┘      │
│                                   │                 │
│                          ┌────────┴────────┐        │
│                          │                 │        │
│                   ┌──────▼──────┐   ┌─────▼─────┐  │
│                   │  KeySender  │   │  Queue UI │  │
│                   │  (pynput)   │   │  (Flask)  │  │
│                   └─────────────┘   └───────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Sequence Diagram (Tip Processing)

```
Listener  FilterAuto  Queue  Worker  KeySender  OS
   │          │         │      │        │       │
   │─poll API─▶         │      │        │       │
   │◀─response─         │      │        │       │
   │          │         │      │        │       │
   │─callback─▶         │      │        │       │
   │          │─add─────▶      │        │       │
   │          │         │      │        │       │
   │          │         │─get──▶        │       │
   │          │         │      │        │       │
   │          │         │      │─send───▶       │
   │          │         │      │        │       │
   │          │         │      │        │─keys──▶
   │          │         │      │        │       │
   │          │         │      │◀─done──        │
   │          │         │◀─done─        │       │
```

---

## Concluzii

Arhitectura AR Filter System V1 este construita pentru:
- **Modularitate**: Componente independente, usor de intretinut
- **Scalabilitate**: Potential de extindere pentru noi platforme
- **Robustete**: Error handling si retry logic
- **Usability**: UI intuitive si automatizare completa

Sistemul urmeaza principii SOLID si design patterns standard, facandu-l usor de inteles si extins de dezvoltatori noi.
