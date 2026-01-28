# 🔌 Configurare pentru API-uri Reale

Acest fișier conține exemple de configurare pentru API-urile reale ale platformelor.

## ⚠️ IMPORTANT: Mock vs. Production

### Mock Server (Testare)
```python
CHATURBATE_URL = "http://127.0.0.1:5000/events/chaturbate"
STRIPCHAT_URL = "http://127.0.0.1:5000/events/stripchat"
CAMSODA_URL = "http://127.0.0.1:5000/events/camsoda"
```

### Production APIs (Real)
```python
# !! EXEMPLU - Înlocuiește cu API keys și endpoint-uri reale !!
CHATURBATE_URL = "https://eventsapi.chaturbate.com/events/YOUR_USERNAME/YOUR_API_TOKEN/"
STRIPCHAT_URL = "https://b2b.stripchat.com/api/vxcammodels/events?token=YOUR_TOKEN"
CAMSODA_URL = "https://api.camsoda.com/api/v1/events?api_key=YOUR_API_KEY"
```

---

## 🔑 Obținere API Keys

### Chaturbate Events API

1. **Autentificare**: Loghează-te pe Chaturbate
2. **App Settings**: Mergi la https://chaturbate.com/apps/
3. **Developer Apps**: Creează un nou app
4. **Events API**: Activează Events API și obține token-ul
5. **Endpoint Format**: 
   ```
   https://eventsapi.chaturbate.com/events/{username}/{token}/
   ```

**Documentație**: https://chaturbate.com/affiliates/api/

**Format evenimente primite**:
```json
{
  "events": [
    {
      "method": "tip",
      "object": {
        "amount": 100,
        "user": {
          "username": "tipper123"
        },
        "message": "great show!"
      }
    }
  ],
  "next_url": "https://eventsapi.chaturbate.com/events/{username}/{token}/"
}
```

---

### Stripchat Events API

1. **Model Account**: Creează cont de model pe Stripchat
2. **Developer Portal**: Mergi la developer settings
3. **API Access**: Request acces la Events API
4. **Token**: Obține token-ul de autentificare
5. **Webhook Setup**: Configurează webhook URL sau polling endpoint

**Documentație**: Contact Stripchat support for API access

**Format evenimente primite**:
```json
{
  "events": [
    {
      "type": "tip",
      "data": {
        "tokens": 100,
        "from": {
          "username": "tipper123",
          "userId": "12345"
        },
        "message": "love the show"
      }
    }
  ]
}
```

---

### Camsoda External API

1. **Broadcaster Account**: Loghează-te ca broadcaster
2. **Settings → Integrations**: Mergi la setări integrations
3. **API Keys**: Generează un API key
4. **External API**: Activează External API pentru tips
5. **Webhook**: Configurează webhook URL sau polling

**Documentație**: https://www.camsoda.com/api (broadcaster access only)

**Format evenimente primite**:
```json
{
  "events": [
    {
      "event_type": "tip",
      "tip_amount": 100,
      "tipper": {
        "name": "tipper123",
        "id": "user_12345"
      },
      "timestamp": 1706442890,
      "message": "awesome!"
    }
  ]
}
```

---

## 🚀 Template de Configurare Production

Creează un fișier `config_production.py`:

```python
"""
Production Configuration for AR Filter System
⚠️ NU UPLOADA ACEST FIȘIER PE GITHUB! Adaugă în .gitignore
"""

# ========================================
# CHATURBATE CONFIGURATION
# ========================================
CHATURBATE_ENABLED = True
CHATURBATE_USERNAME = "your_username_here"
CHATURBATE_TOKEN = "your_token_here"
CHATURBATE_URL = f"https://eventsapi.chaturbate.com/events/{CHATURBATE_USERNAME}/{CHATURBATE_TOKEN}/"

# ========================================
# STRIPCHAT CONFIGURATION
# ========================================
STRIPCHAT_ENABLED = True
STRIPCHAT_TOKEN = "your_token_here"
STRIPCHAT_URL = f"https://b2b.stripchat.com/api/events?token={STRIPCHAT_TOKEN}"

# ========================================
# CAMSODA CONFIGURATION
# ========================================
CAMSODA_ENABLED = True
CAMSODA_API_KEY = "your_api_key_here"
CAMSODA_URL = f"https://api.camsoda.com/v1/events?api_key={CAMSODA_API_KEY}"

# ========================================
# HELPER FUNCTION
# ========================================
def get_platform_urls():
    """Returns dict of enabled platform URLs"""
    return {
        'chaturbate': CHATURBATE_URL if CHATURBATE_ENABLED else None,
        'stripchat': STRIPCHAT_URL if STRIPCHAT_ENABLED else None,
        'camsoda': CAMSODA_URL if CAMSODA_ENABLED else None
    }
```

### Folosire în `main.py`:

```python
# La începutul main.py, adaugă:
try:
    from config_production import get_platform_urls
    urls = get_platform_urls()
    CHATURBATE_URL = urls['chaturbate']
    STRIPCHAT_URL = urls['stripchat']
    CAMSODA_URL = urls['camsoda']
    print("✅ Using production configuration")
except ImportError:
    # Fallback to mock server
    CHATURBATE_URL = "http://127.0.0.1:5000/events/chaturbate"
    STRIPCHAT_URL = "http://127.0.0.1:5000/events/stripchat"
    CAMSODA_URL = "http://127.0.0.1:5000/events/camsoda"
    print("⚠️ Using mock server configuration")
```

---

## 🔒 Security Best Practices

### 1. **Environment Variables**
În loc de hardcoding tokens, folosește variabile de mediu:

```python
import os

CHATURBATE_URL = os.environ.get('CHATURBATE_API_URL')
STRIPCHAT_URL = os.environ.get('STRIPCHAT_API_URL')
CAMSODA_URL = os.environ.get('CAMSODA_API_URL')
```

Apoi creează `.env`:
```bash
CHATURBATE_API_URL=https://eventsapi.chaturbate.com/events/user/token/
STRIPCHAT_API_URL=https://b2b.stripchat.com/api/events?token=xxx
CAMSODA_API_URL=https://api.camsoda.com/v1/events?api_key=xxx
```

Instalează `python-dotenv`:
```bash
pip install python-dotenv
```

Încarcă în `main.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. **.gitignore Configuration**
Adaugă în `.gitignore`:
```
config_production.py
.env
*.secret
*.key
```

### 3. **API Key Rotation**
- Schimbă API keys regular (lunar/trimestrial)
- Nu partaja keys-urile cu nimeni
- Monitorizează usage-ul API-urilor pentru activitate suspectă

---

## 🧪 Testing Production APIs

### Step 1: Test cu cURL
```bash
# Chaturbate
curl "https://eventsapi.chaturbate.com/events/YOUR_USER/YOUR_TOKEN/"

# Verifică că primești răspuns valid JSON
```

### Step 2: Test cu Python
```python
import requests

url = "https://eventsapi.chaturbate.com/events/YOUR_USER/YOUR_TOKEN/"
response = requests.get(url)
print(response.status_code)  # Should be 200
print(response.json())       # Should show events structure
```

### Step 3: Integrare în Sistem
```python
# În main.py:
CHATURBATE_URL = "https://eventsapi.chaturbate.com/events/YOUR_USER/YOUR_TOKEN/"
# ... celelalte URL-uri

app = CameraFiltersAutomation(
    chaturbate_url=CHATURBATE_URL,
    stripchat_url=STRIPCHAT_URL,
    camsoda_url=CAMSODA_URL,
    output_mode="vcam",
    quality="1080p"
)
app.run()
```

---

## 🔄 Webhook Alternative (Advanced)

În loc de polling, unele platforme suportă webhooks. Exemplu Flask webhook receiver:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook/chaturbate', methods=['POST'])
def chaturbate_webhook():
    data = request.json
    # Process tip event
    amount = data['object']['amount']
    username = data['object']['user']['username']
    
    # Trigger filter
    camera_app.process_tip(amount, username)
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=8080)
```

**Avantaje**:
- Latență mai mică (push vs pull)
- Reduce numărul de API requests
- Real-time processing

**Dezavantaje**:
- Necesită server public cu IP static
- Mai complexă configurarea
- Necesită SSL certificate pentru HTTPS

---

## 📞 Support

Pentru issues cu API-urile reale:
- **Chaturbate**: support@chaturbate.com
- **Stripchat**: Contact prin model support portal
- **Camsoda**: broadcaster-support@camsoda.com

Pentru issues cu acest sistem:
- Consultă `MULTI_PLATFORM_GUIDE.md`
- Verifică `IMPLEMENTATION_SUMMARY.md`

---

## ⚠️ Rate Limits

Fii atent la rate limits ale fiecărei platforme:

| Platform   | Rate Limit (estimate) | Polling Interval Recomandat |
|------------|----------------------|----------------------------|
| Chaturbate | 60 req/min           | 1-2 secunde                |
| Stripchat  | 30 req/min           | 2-3 secunde                |
| Camsoda    | 120 req/min          | 1 secunde                  |

**Nota**: În listener-ele curente, polling interval este 1s. Ajustează dacă primești rate limit errors.

Pentru a modifica polling interval, editează `_fetch_events()` în fiecare listener:
```python
# În loc de:
time.sleep(1)

# Folosește:
time.sleep(2)  # 2 secunde
```

---

**Ultimă actualizare**: 2026-01-28  
**Status**: Production Ready  
**Versiune**: 1.0.0
