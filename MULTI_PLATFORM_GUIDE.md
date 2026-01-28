# AR Filter System - Multi-Platform Tipping Integration

## 📋 Prezentare Generală

Sistemul AR Filter suportă acum **3 platforme de streaming**:
- 🟠 **Chaturbate** (Events API)
- 🔵 **Stripchat** (Events API)
- 🟢 **Camsoda** (External API)

Fiecare platformă rulează pe propriul thread separat, permițând procesarea simultană a tips-urilor fără interferențe.

---

## 🏗️ Arhitectură

### Structura Modulelor

```
AR_Filter_System_V1/
├── main.py                          # Aplicația principală
├── core/
│   ├── OutputManager.py            # Manager pentru output video
│   ├── ChaturbateListener.py       # Listener pentru Chaturbate
│   ├── StripchatListener.py        # Listener pentru Stripchat
│   └── CamsodaListener.py          # Listener pentru Camsoda
├── filters/
│   ├── BigEyeFilter.py             # Filtru ochi mari
│   ├── FaceMask3DFilter.py         # Filtru mască 3D
│   └── RainSparkleFilter.py        # Filtru particule
└── tests/
    └── mock_server.py              # Server de testare pentru toate platformele
```

### Flow Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Chaturbate    │     │    Stripchat    │     │     Camsoda     │
│   Events API    │     │   Events API    │     │  External API   │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  process_tip(amount,    │
                    │     username)           │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Priority Queue        │
                    │   (deque)               │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Filter Activation     │
                    │   (Sparkles, Big Eyes,  │
                    │    Cyber Mask)          │
                    └─────────────────────────┘
```

---

## 🔧 Normalizarea Datelor

Fiecare platformă folosește formate JSON diferite. Listener-ele normalizează datele înainte de a le trimite la `process_tip()`.

### Chaturbate Format
```json
{
  "method": "tip",
  "object": {
    "amount": 100,
    "user": {
      "username": "user123"
    }
  }
}
```
**Normalizare**: `amount` → `amount`, `user.username` → `username`

### Stripchat Format
```json
{
  "type": "tip",
  "data": {
    "tokens": 100,
    "from": {
      "username": "user123"
    }
  }
}
```
**Normalizare**: `data.tokens` → `amount`, `data.from.username` → `username`

### Camsoda Format
```json
{
  "event_type": "tip",
  "tip_amount": 100,
  "tipper": {
    "name": "user123"
  }
}
```
**Normalizare**: `tip_amount` → `amount`, `tipper.name` → `username`

---

## 🚀 Utilizare

### 1. Pornire Mock Server

```bash
python tests/mock_server.py
```

Server-ul va porni pe `http://127.0.0.1:5000` și va afișa:
```
============================================================
🚀 AR Filter System - Mock API Server
============================================================

📡 Platforme disponibile:
   • Chaturbate: http://127.0.0.1:5000/events/chaturbate
   • Stripchat:  http://127.0.0.1:5000/events/stripchat
   • Camsoda:    http://127.0.0.1:5000/events/camsoda

🌐 Deschide http://127.0.0.1:5000 pentru documentație
============================================================
```

### 2. Configurare Aplicație Principală

Editează `main.py` pentru a activa/dezactiva platforme:

```python
if __name__ == "__main__":
    # Configurare URL-uri pentru fiecare platformă
    CHATURBATE_URL = "http://127.0.0.1:5000/events/chaturbate"
    STRIPCHAT_URL = "http://127.0.0.1:5000/events/stripchat"
    CAMSODA_URL = "http://127.0.0.1:5000/events/camsoda"
    
    # Pentru a dezactiva o platformă:
    # STRIPCHAT_URL = None
    
    app = CameraFiltersAutomation(
        chaturbate_url=CHATURBATE_URL,
        stripchat_url=STRIPCHAT_URL,
        camsoda_url=CAMSODA_URL,
        output_mode="window",  # sau "vcam" pentru virtual camera
        quality="1080p"
    )
    app.run()
```

### 3. Pornire Aplicație

```bash
python main.py
```

### 4. Testare Tips

#### Opțiune A: Browser (Recomandat)
Deschide `http://127.0.0.1:5000` în browser și click pe link-urile de test.

#### Opțiune B: cURL
```bash
# Chaturbate
curl http://127.0.0.1:5000/trigger/chaturbate/33/TestUser1

# Stripchat
curl http://127.0.0.1:5000/trigger/stripchat/99/StripUser2

# Camsoda
curl http://127.0.0.1:5000/trigger/camsoda/200/CamUser3
```

#### Opțiune C: Keyboard Shortcuts (fără server)
- Apasă `1` → 35 tokens (Sparkles - closest to 33)
- Apasă `2` → 105 tokens (Big Eyes - closest to 99)
- Apasă `3` → 500 tokens (Cyber Mask - closest to 200)

---

## 🎯 Mapare Filtre

| **Tokens** | **Filtru**     | **Durată** |
|-----------|---------------|-----------|
| 33        | Sparkles      | 10s       |
| 99        | Big Eyes      | 20s       |
| 200       | Cyber Mask    | 30s       |

---

## 🔐 Gestionarea Erorilor

Fiecare listener implementează:

### 1. **Exponential Backoff**
Dacă un API nu răspunde, sistemul crește treptat delay-ul între încercări:
- Încercare 1: 5s delay
- Încercare 2: 10s delay
- Încercare 3: 20s delay
- ...
- Max delay: 60s

### 2. **Error Types Handled**
- `Timeout`: API-ul nu răspunde în 5 secunde
- `ConnectionError`: Server-ul este offline
- `RequestException`: Erori HTTP generale
- `Exception`: Orice alte erori neașteptate

### 3. **Independent Operation**
Dacă Chaturbate este offline, Stripchat și Camsoda continuă să funcționeze normal.

**Exemplu de log când un API este offline:**
```
✅ Chaturbate listener started on http://127.0.0.1:5000/events/chaturbate
✅ Stripchat listener started on http://127.0.0.1:5000/events/stripchat
✅ Camsoda listener started on http://127.0.0.1:5000/events/camsoda
⚠️ Stripchat API connection failed. Retrying in 5s...
⚠️ Stripchat API connection failed. Retrying in 10s...
```

---

## 🧪 Testing Mock Server

### Endpoint-uri Disponibile

#### Chaturbate
- **Trigger**: `GET /trigger/chaturbate/<amount>/<username>`
- **Events**: `GET /events/chaturbate`

#### Stripchat
- **Trigger**: `GET /trigger/stripchat/<amount>/<username>`
- **Events**: `GET /events/stripchat`

#### Camsoda
- **Trigger**: `GET /trigger/camsoda/<amount>/<username>`
- **Events**: `GET /events/camsoda`

### Exemple de Requests

```python
import requests

# Simulează tip Chaturbate
requests.get('http://127.0.0.1:5000/trigger/chaturbate/99/Alice')

# Simulează tip Stripchat
requests.get('http://127.0.0.1:5000/trigger/stripchat/200/Bob')

# Simulează tip Camsoda
requests.get('http://127.0.0.1:5000/trigger/camsoda/33/Charlie')
```

---

## 📝 Modificări față de Versiunea Anterioară

### Înainte (Single-Threaded, Chaturbate Only)
```python
def __init__(self, api_url=None):
    if self.api_url:
        threading.Thread(target=self.fetch_events, daemon=True).start()

def fetch_events(self):
    # Polling logic pentru Chaturbate
    ...
```

### După (Multi-Threaded, 3 Platforme)
```python
def __init__(self, chaturbate_url=None, stripchat_url=None, camsoda_url=None):
    self.listeners = []
    
    if chaturbate_url:
        listener = ChaturbateListener(chaturbate_url, self.process_tip)
        listener.start()
        self.listeners.append(listener)
    
    # Similar pentru Stripchat și Camsoda
    ...
```

**Beneficii**:
- ✅ Separarea preocupărilor (separation of concerns)
- ✅ Gestionare independentă a erorilor
- ✅ Scalabilitate - ușor de adăugat noi platforme
- ✅ Thread-safe processing
- ✅ Exponential backoff pentru fiecare platformă

---

## 🔮 Extindere Viitoare

Pentru a adăuga o platformă nouă (ex: MyFreeCams):

1. **Crează listener nou**: `core/MyFreeCamsListener.py`
```python
class MyFreeCamsListener:
    def __init__(self, api_url, process_tip_callback):
        # Similar cu alte listeners
        ...
    
    def _fetch_events(self):
        # Normalizează formatul MyFreeCams
        ...
```

2. **Adaugă în main.py**:
```python
from core.MyFreeCamsListener import MyFreeCamsListener

# În __init__:
if myfreecams_url:
    listener = MyFreeCamsListener(myfreecams_url, self.process_tip)
    listener.start()
    self.listeners.append(listener)
```

3. **Adaugă în mock_server.py**:
```python
@app.route('/trigger/myfreecams/<int:amount>/<string:user>')
def trigger_myfreecams(amount, user):
    # Simulare tips
    ...
```

---

## 📞 Support & Debug

### Verificare Status Listeners

Adaugă acest cod în `main.py` pentru debugging:

```python
def get_active_platforms(self):
    active = []
    for listener in self.listeners:
        if listener.running:
            active.append(listener.__class__.__name__)
    return active

# Folosire:
print(f"Active platforms: {app.get_active_platforms()}")
```

### Log Level Adjustment

Pentru mai multe detalii de debugging, modifică listener-ele:

```python
# În _fetch_events() adaugă:
print(f"[DEBUG] Received data: {data}")
```

---

## 📄 Licență

Acest sistem este parte din AR Camera System proiect. Toate drepturile rezervate.
