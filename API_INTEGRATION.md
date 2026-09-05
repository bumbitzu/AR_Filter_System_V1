# API Integration - AR Filter System V1

## Cuprins

1. [Prezentare Generala](#prezentare-generala)
2. [Chaturbate API](#chaturbate-api)
3. [Stripchat API](#stripchat-api)
4. [Camsoda API](#camsoda-api)
5. [Event Normalization](#event-normalization)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Mock Server](#mock-server)
9. [Best Practices](#best-practices)

---

## Prezentare Generala

AR Filter System se integreaza cu trei platforme principale de streaming live:
- **Chaturbate** - Events API
- **Stripchat** - Events API
- **Camsoda** - External API

Fiecare platform are propriul format de date si protocol de comunicare. Sistemul normalizeaza aceste diferente intr-un format uniform pentru procesare consistenta.

### Arhitectura Integration

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Chaturbate  │     │  Stripchat   │     │   Camsoda    │
│     API      │     │     API      │     │     API      │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │ HTTP               │ HTTP               │ HTTP
       │ Polling            │ Polling            │ Polling
       ↓                    ↓                    ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Chaturbate   │     │  Stripchat   │     │   Camsoda    │
│  Listener    │     │   Listener   │     │   Listener   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ↓
                   ┌─────────────────┐
                   │ Event            │
                   │ Normalization    │
                   └────────┬─────────┘
                            ↓
                   ┌─────────────────┐
                   │ Uniform Format   │
                   │  {               │
                   │   platform,      │
                   │   amount,        │
                   │   tipper,        │
                   │   message,       │
                   │   timestamp      │
                   │  }               │
                   └─────────────────┘
```

---

## Chaturbate API

### Overview

Chaturbate Events API permite broadcasterilor sa primeasca evenimente in timp real despre tips, follows, si alte actiuni.

### Configuration

**Environment Variables:**
```bash
# .env sau .env.production
CHATURBATE_ENABLED=true
CHATURBATE_EVENTS_URL=https://events.example.com/events/{broadcaster}
CHATURBATE_POLL_INTERVAL=5
```

### API Endpoint

```
GET https://events.example.com/events/{broadcaster}
```

**Headers:**
```http
X-Api-Key: your_api_key_here
Content-Type: application/json
```

### Response Formats

Chaturbate suporta doua formate de raspuns:

#### Format 1 (Legacy)

```json
{
  "events": [
    {
      "method": "tip",
      "tip": {
        "tokens": 100,
        "from_username": "tipper123",
        "message": "Great show!",
        "is_anon": false
      }
    }
  ]
}
```

#### Format 2 (Nou)

```json
{
  "events": [
    {
      "method": "tip",
      "object": {
        "amount": 100,
        "from_user": {
          "username": "tipper123",
          "is_mod": false
        },
        "message": "Great show!"
      }
    }
  ]
}
```

### Normalization Logic

```python
def _normalize_event(self, event):
    """Normalizeaza evenimentul Chaturbate la format uniform"""
    
    # Detectare format
    if "tip" in event:
        # Format 1 (legacy)
        tip_data = event["tip"]
        amount = tip_data.get("tokens", 0)
        tipper = tip_data.get("from_username", "Anonymous")
        message = tip_data.get("message", "")
    else:
        # Format 2 (nou)
        obj = event.get("object", {})
        amount = obj.get("amount", 0)
        from_user = obj.get("from_user", {})
        tipper = from_user.get("username", "Anonymous")
        message = obj.get("message", "")
    
    return {
        "platform": "chaturbate",
        "amount": amount,
        "tipper": tipper,
        "message": message,
        "timestamp": time.time()
    }
```

### Error Scenarios

**Timeout:**
```python
except requests.Timeout:
    # Exponential backoff
    delay = min(self.base_delay * (2 ** self.retry_count), 60)
    print(f"Timeout API Chaturbate. Reincercare in {delay}s...")
    time.sleep(delay)
```

**Connection Error:**
```python
except requests.ConnectionError as e:
    print(f"Eroare conexiune API Chaturbate: {e}")
    time.sleep(10)
```

**HTTP Errors:**
```python
except requests.HTTPError as e:
    if response.status_code == 401:
        print("Eroare autentificare Chaturbate. Verifica API key.")
    elif response.status_code == 429:
        print("Rate limit Chaturbate. Asteptare...")
        time.sleep(30)
```

### Retry Strategy

**Exponential Backoff:**
```python
base_delay = 5          # Initial delay
max_retry = 5           # Max retries
retry_count = 0

delay = min(base_delay * (2 ** retry_count), 60)
# Delays: 5s, 10s, 20s, 40s, 60s (max)
```

---

## Stripchat API

### Overview

Stripchat Events API ofera evenimente real-time pentru tips si interactiuni.

### Configuration

**Environment Variables:**
```bash
STRIPCHAT_ENABLED=true
STRIPCHAT_EVENTS_URL=https://api.stripchat.com/v1/events
STRIPCHAT_POLL_INTERVAL=5
```

### API Endpoint

```
GET https://api.stripchat.com/v1/events
```

**Headers:**
```http
Authorization: Bearer your_token_here
Content-Type: application/json
```

### Response Formats

Stripchat suporta multiple formate:

#### Format Standard

```json
{
  "events": [
    {
      "type": "tip",
      "amount": 50,
      "user": {
        "username": "user456",
        "is_premium": true
      },
      "message": "Nice!"
    }
  ]
}
```

#### Format Alternativ

```json
{
  "events": [
    {
      "type": "tip",
      "tip": {
        "amount": 50,
        "message": "Nice!"
      },
      "user": {
        "username": "user456"
      }
    }
  ]
}
```

### Normalization Logic

```python
def _normalize_event(self, event):
    """Normalizeaza evenimentul Stripchat la format uniform"""
    
    # Extract amount (multiple locations posibile)
    amount = event.get("amount")
    if amount is None:
        tip_obj = event.get("tip", {})
        amount = tip_obj.get("amount", 0)
    
    # Extract user
    user_obj = event.get("user", {})
    tipper = user_obj.get("username", "Anonymous")
    
    # Extract message
    message = event.get("message", "")
    if not message:
        tip_obj = event.get("tip", {})
        message = tip_obj.get("message", "")
    
    return {
        "platform": "stripchat",
        "amount": amount,
        "tipper": tipper,
        "message": message,
        "timestamp": time.time()
    }
```

### Error Handling

**API Errors:**
```python
try:
    response.raise_for_status()
except requests.HTTPError as e:
    if response.status_code == 401:
        print("Token Stripchat invalid sau expirat")
    elif response.status_code == 403:
        print("Acces interzis Stripchat")
    else:
        print(f"Eroare API Stripchat: {e}")
```

**Network Errors:**
```python
except requests.ConnectionError:
    print("Esec conexiune API Stripchat. Reincercare...")
    time.sleep(10)
```

---

## Camsoda API

### Overview

Camsoda External API ofera acces la evenimente pentru broadcasteri.

### Configuration

**Environment Variables:**
```bash
CAMSODA_ENABLED=true
CAMSODA_EVENTS_URL=https://api.camsoda.com/external/events
CAMSODA_POLL_INTERVAL=5
```

### API Endpoint

```
GET https://api.camsoda.com/external/events
```

**Query Parameters:**
```
?broadcaster=your_username
&api_key=your_api_key
```

### Response Format

```json
{
  "success": true,
  "events": [
    {
      "type": "tip",
      "amount": 25,
      "tipper": {
        "username": "fan789"
      },
      "timestamp": 1234567890
    }
  ]
}
```

#### Format Alternativ

```json
{
  "success": true,
  "events": [
    {
      "type": "tip",
      "amount": 25,
      "user": "fan789",
      "timestamp": 1234567890
    }
  ]
}
```

### Normalization Logic

```python
def _normalize_event(self, event):
    """Normalizeaza evenimentul Camsoda la format uniform"""
    
    amount = event.get("amount", 0)
    
    # Tipper poate fi in mai multe locuri
    tipper = "Anonymous"
    if "tipper" in event:
        tipper_obj = event["tipper"]
        if isinstance(tipper_obj, dict):
            tipper = tipper_obj.get("username", "Anonymous")
        else:
            tipper = str(tipper_obj)
    elif "user" in event:
        tipper = event["user"]
    
    message = event.get("message", "")
    
    return {
        "platform": "camsoda",
        "amount": amount,
        "tipper": tipper,
        "message": message,
        "timestamp": event.get("timestamp", time.time())
    }
```

### Error Handling

**Timeout Handling:**
```python
except requests.Timeout:
    print("Timeout API Camsoda. Reincercare...")
    time.sleep(5)
```

**Response Validation:**
```python
if not data.get("success"):
    print("API Camsoda raspuns esuat")
    return

events = data.get("events", [])
if not events:
    return  # No events, continue polling
```

---

## Event Normalization

### Uniform Format

Toate platformele sunt normalizate la acest format:

```python
{
    "platform": str,      # "chaturbate" | "stripchat" | "camsoda"
    "amount": int,        # Suma tip in tokens
    "tipper": str,        # Username tipper (sau "Anonymous")
    "message": str,       # Mesaj tip (optional, default "")
    "timestamp": float    # Unix timestamp
}
```

### Benefits

1. **Consistent Processing**: Logica aplicatie nu depinde de platform
2. **Easy Testing**: Mock data uniform
3. **Extensibility**: Usor de adaugat platforme noi
4. **Type Safety**: Format predictibil pentru debugging

### Implementation Pattern

```python
class PlatformListener:
    def _normalize_event(self, event):
        """Implementat de fiecare subclasa"""
        raise NotImplementedError
    
    def _poll(self):
        # Poll API
        events = self._fetch_events()
        
        # Normalize si callback
        for event in events:
            normalized = self._normalize_event(event)
            self.callback(normalized)
```

---

## Error Handling

### Hierarchy of Errors

```
Exception
├── RequestException
│   ├── Timeout
│   ├── ConnectionError
│   ├── HTTPError
│   │   ├── 401 Unauthorized
│   │   ├── 403 Forbidden
│   │   ├── 429 Too Many Requests
│   │   └── 500 Server Error
│   └── SSLError
└── ValueError (parsing errors)
```

### Error Recovery Strategies

**1. Timeout → Exponential Backoff**
```python
retry_count = 0
max_retries = 5

while retry_count < max_retries:
    try:
        response = requests.get(url, timeout=10)
        break
    except Timeout:
        delay = min(5 * (2 ** retry_count), 60)
        time.sleep(delay)
        retry_count += 1
```

**2. Connection Error → Fixed Delay**
```python
except ConnectionError:
    print("Conexiune esuata. Reincercare in 10s...")
    time.sleep(10)
```

**3. Rate Limit → Respectare Headers**
```python
if response.status_code == 429:
    retry_after = response.headers.get("Retry-After", 30)
    time.sleep(int(retry_after))
```

**4. Authentication Error → Stop si Alert**
```python
if response.status_code == 401:
    print("EROARE CRITICA: Autentificare esuata!")
    print("Verifica API keys in .env")
    return  # Stop acest listener
```

### Logging Best Practices

```python
# Log structure
print(f"[{platform}] [{timestamp}] {message}")

# Examples
print("[chaturbate] [12:34:56] Listener pornit")
print("[stripchat] [12:35:01] Primit tip: 100 tokens de la user123")
print("[camsoda] [12:35:10] Eroare API: Timeout")
```

---

## Rate Limiting

### Platform Limits

**Chaturbate:**
- Rate limit: ~120 requests/minute
- Burst: Da (permite spike-uri temporare)
- Headers: `X-RateLimit-Remaining`

**Stripchat:**
- Rate limit: ~100 requests/minute
- Burst: Nu (strict enforcement)
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

**Camsoda:**
- Rate limit: ~60 requests/minute
- Burst: Da
- Headers: None (implicit)

### Implementation Strategy

**Poll Interval Configuration:**
```python
# .env configuration
CHATURBATE_POLL_INTERVAL=5  # 12 req/min → safe
STRIPCHAT_POLL_INTERVAL=5   # 12 req/min → safe
CAMSODA_POLL_INTERVAL=10    # 6 req/min → very safe
```

**Adaptive Polling:**
```python
def _poll(self):
    base_interval = self.poll_interval
    
    while not self.stop_event.is_set():
        start_time = time.time()
        
        try:
            self._fetch_and_process()
            interval = base_interval
        except RateLimitError:
            interval = base_interval * 2  # Backoff
        
        elapsed = time.time() - start_time
        sleep_time = max(0, interval - elapsed)
        time.sleep(sleep_time)
```

### Monitoring Rate Limits

```python
def _check_rate_limit(self, response):
    """Verifica headers rate limit"""
    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining and int(remaining) < 10:
        print(f"[WARNING] Rate limit aproape atins: {remaining} ramase")
```

---

## Mock Server

### Overview

Mock Server (`tests/mock_server.py`) simuleaza API-urile platformelor pentru testare fara credentials reale.

### Endpoints

```python
# Chaturbate mock
GET /events/chaturbate

# Stripchat mock
GET /events/stripchat

# Camsoda mock
GET /events/camsoda
```

### Usage

**Start Server:**
```bash
python tests\mock_server.py
```

**Configure Application:**
```bash
# .env.test
CHATURBATE_ENABLED=true
CHATURBATE_EVENTS_URL=http://127.0.0.1:5000/events/chaturbate
```

### Mock Response Examples

**Chaturbate Mock:**
```json
{
  "events": [
    {
      "method": "tip",
      "object": {
        "amount": 100,
        "from_user": {"username": "test_user"},
        "message": "Test tip"
      }
    }
  ]
}
```

**Random Events:**
Mock server genereaza evenimente random cu:
- Amounts: [10, 20, 50, 100, 200]
- Users: [user1, user2, user3, fan123, supporter]
- Messages: Fraze predefinite

### Benefits

- ✅ Testare fara API keys
- ✅ Predictable behavior
- ✅ No rate limits
- ✅ Instant feedback
- ✅ Development offline

---

## Best Practices

### 1. Configuration Management

**Use Environment Variables:**
```python
# ❌ Bad - hardcoded
url = "https://api.platform.com/events"

# ✅ Good - configurable
url = os.getenv("PLATFORM_EVENTS_URL")
```

**Separate Environments:**
```
.env.test        # Mock URLs
.env.production  # Real URLs
```

### 2. Error Handling

**Always Catch Specific Exceptions:**
```python
# ❌ Bad
except Exception as e:
    print(f"Error: {e}")

# ✅ Good
except requests.Timeout:
    # Handle timeout
except requests.ConnectionError:
    # Handle connection
except requests.HTTPError as e:
    # Handle HTTP errors
```

**Log Errors with Context:**
```python
print(f"[{platform}] Eroare la {timestamp}: {error_details}")
```

### 3. Polling Strategy

**Respect Rate Limits:**
```python
# Configure conservative intervals
poll_interval = max(5, required_interval)
```

**Use Timeout:**
```python
response = requests.get(url, timeout=10)
# Prevents hanging forever
```

**Graceful Shutdown:**
```python
while not self.stop_event.is_set():
    # Polling logic
    time.sleep(poll_interval)
```

### 4. Data Validation

**Validate Before Normalization:**
```python
def _normalize_event(self, event):
    # Check required fields
    if "amount" not in event and "tip" not in event:
        print("Event invalid: lipseste amount")
        return None
    
    # Proceed with normalization
```

**Type Checking:**
```python
amount = event.get("amount", 0)
if not isinstance(amount, (int, float)):
    print(f"Amount invalid: {amount}")
    return None
```

### 5. Testing

**Test Each Platform:**
```python
# Test normalization
def test_chaturbate_normalization():
    listener = ChaturbateListener(...)
    event = {"tip": {"tokens": 100, "from_username": "test"}}
    normalized = listener._normalize_event(event)
    assert normalized["amount"] == 100
    assert normalized["platform"] == "chaturbate"
```

**Mock API Responses:**
```python
@patch('requests.get')
def test_polling(mock_get):
    mock_get.return_value.json.return_value = {
        "events": [mock_event]
    }
    # Test logic
```

### 6. Monitoring

**Log Key Events:**
```python
print(f"[{platform}] Listener pornit pe {url}")
print(f"[{platform}] Primit tip: {amount} tokens de la {tipper}")
print(f"[{platform}] Eroare: {error}")
```

**Track Metrics:**
```python
# Count events processed
self.events_processed += 1
print(f"Total evenimente procesate: {self.events_processed}")
```

---

## Troubleshooting

### Common Issues

**1. No Events Received**
- Verifica API URL este corect
- Confirma API keys sunt valide
- Check network connectivity
- Verifica platform este enabled in .env

**2. Authentication Errors**
- Regenereaza API keys pe platform
- Verifica format headers (Bearer vs API-Key)
- Check expiration date pentru tokens

**3. Rate Limit Exceeded**
- Creste poll_interval in .env
- Implementeaza exponential backoff
- Monitor rate limit headers

**4. Parsing Errors**
- Log raw response pentru debugging
- Check API documentation pentru format changes
- Update normalization logic

**5. Connection Timeouts**
- Verifica internet connection
- Creste timeout value
- Check firewall/proxy settings

### Debug Mode

**Enable Verbose Logging:**
```python
# In listener
DEBUG = os.getenv("DEBUG", "false") == "true"

if DEBUG:
    print(f"Raw response: {response.text}")
    print(f"Parsed data: {data}")
```

**Test Individual Components:**
```bash
# Test doar un listener
python -c "from core.ChaturbateListener import ChaturbateListener; ..."
```

---

## Appendix

### API Documentation Links

- **Chaturbate**: Contact support for API access
- **Stripchat**: Check broadcaster dashboard
- **Camsoda**: External API documentation

### Rate Limit Calculator

```python
def calculate_safe_interval(rate_limit_per_minute):
    """
    Calculeaza interval sigur pentru polling
    
    rate_limit_per_minute: Max requests per minute
    Returns: Interval in seconds
    """
    return (60 / rate_limit_per_minute) * 1.5  # 50% safety margin

# Examples
chaturbate_interval = calculate_safe_interval(120)  # → 0.75s
stripchat_interval = calculate_safe_interval(100)   # → 0.9s
camsoda_interval = calculate_safe_interval(60)      # → 1.5s
```

### Event Schema Validation

```python
NORMALIZED_EVENT_SCHEMA = {
    "platform": str,
    "amount": (int, float),
    "tipper": str,
    "message": str,
    "timestamp": float
}

def validate_normalized_event(event):
    for field, expected_type in NORMALIZED_EVENT_SCHEMA.items():
        if field not in event:
            raise ValueError(f"Lipseste field: {field}")
        if not isinstance(event[field], expected_type):
            raise TypeError(f"Type gresit pentru {field}")
    return True
```

---

## Concluzii

Integrarile API sunt核心 al sistemului. Implementarea robusta cu:
- Error handling comprehensiv
- Retry strategies
- Rate limiting respect
- Event normalization

Asigura functionare stabila si fiabila in production.
