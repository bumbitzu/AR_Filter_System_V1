# Ghid Utilizare - AR Filter System V1

## Cuprins

1. [Introducere](#introducere)
2. [Pornire Sistem](#pornire-sistem)
3. [Moduri de Operare](#moduri-de-operare)
4. [Interfata Web](#interfata-web)
5. [Trigger Manual Filtre](#trigger-manual-filtre)
6. [Gestionare Coada](#gestionare-coada)
7. [Monitorizare si Loguri](#monitorizare-si-loguri)
8. [Oprire Sistem](#oprire-sistem)
9. [Scenarii Uzuale](#scenarii-uzuale)
10. [Troubleshooting Utilizare](#troubleshooting-utilizare)

---

## Introducere

AR Filter System automatizeaza aplicarea filtrelor AR bazat pe tipuri primite pe platformele de streaming. Sistemul:
- ✅ Asculta evenimente tip de la Chaturbate, Stripchat, Camsoda
- ✅ Aplica automat filtre corespunzatoare sumei primite
- ✅ Gestioneaza coada cu prioritati
- ✅ Ofera control manual prin taste

### Flow Utilizare Tipic

```
1. Pornesti sistemul (run.bat sau python main.py)
2. Deschizi UI web pentru monitorizare (optional)
3. Primesti tip pe platforma
4. Sistemul detecteaza tip
5. Adauga filtru in coada
6. Aplica automat filtrul prin taste
7. Continua cu urmatorul din coada
```

---

## Pornire Sistem

### Metoda 1: Folosind run.bat (Recomandat)

**1. Deschide run.bat:**
```powershell
# Dublu-click pe run.bat
# SAU din terminal
.\run.bat
```

**2. Selecteaza optiune pornire:**
```
============================================================
         AR FILTER SYSTEM - PANOU DE CONTROL
============================================================

   [1] Porneste Programul
   [2] Opreste Programul
   [3] Reporneste Programul
   [4] Vizualizeaza Loguri
   [5] Deschide Queue UI
   [6] Verifica Status
   [7] Verifica Environment
   [Q] Iesire

============================================================
Alege optiunea (1-7 sau Q):
```

**3. Apasa [1] pentru pornire.**

**Output:**
```
Pornesc AR Filter System...
Program pornit cu succes!

IMPORTANT: Pastreaza fereastra Python deschisa pentru ca tastele sa functioneze!

Apasa orice tasta pentru a reveni la meniu...
```

**4. O noua fereastra Python se va deschide cu log-uri live.**

### Metoda 2: Direct cu Python

**Pentru utilizatori avansati:**

```powershell
# Activeaza environment (daca folosesti venv)
.\venv\Scripts\Activate.ps1

# Porneste aplicatia
python main.py
```

**Output:**
```
╔══════════════════════════════════════════════════════╗
║  AR FILTER SYSTEM - PORNIRE                          ║
╚══════════════════════════════════════════════════════╝

[chaturbate] Listener Chaturbate pornit pe http://...
[stripchat] Listener Stripchat pornit pe http://...
[camsoda] Listener Camsoda pornit pe http://...

Thread worker pornit pentru procesare coada
Taste manuale activate: Ctrl+1, Ctrl+2, ... Ctrl+9

Serverul Queue UI porneste pe http://127.0.0.1:8080
  -> Acceseaza: http://127.0.0.1:8080/queue

Program activ. Apasa Ctrl+C pentru oprire.
```

**IMPORTANT**: Lasa fereastra deschisa! Daca o inchizi, tastele nu mai functioneaza.

---

## Moduri de Operare

### TEST Mode (Mock Server)

**Cand folosesti:**
- Pentru testare fara API credentials
- Pentru demo si prezentari
- Pentru dezvoltare si debugging

**Setup:**

**1. Activeaza TEST mode:**
```powershell
switch_env.bat
# Selecteaza [1] - TEST MODE
```

**2. Porneste Mock Server:**
```powershell
# Intr-un terminal separat
python tests\mock_server.py
```

**Output:**
```
=========================================
   MOCK SERVER - AR FILTER SYSTEM
=========================================
Endpoints disponibile:
  • Chaturbate: http://127.0.0.1:5000/events/chaturbate
  • Stripchat:  http://127.0.0.1:5000/events/stripchat
  • Camsoda:    http://127.0.0.1:5000/events/camsoda

Mock server pornit pe http://127.0.0.1:5000

Genereaza evenimente random la fiecare 10 secunde.
Apasa Ctrl+C pentru oprire.
```

**3. Porneste aplicatia principala** (in alt terminal):
```powershell
python main.py
```

**Comportament:**
- Mock server genereaza tips random (10, 20, 50, 100, 200 tokens)
- Sistemul proceseaza aceste tips ca si cum ar fi reale
- Perfect pentru testare si invatare

### PRODUCTION Mode (API-uri Reale)

**Cand folosesti:**
- Pentru streaming live real
- Dupa ce ai testat in TEST mode
- Cand ai API credentials valide

**Setup:**

**1. Configureaza API keys:**
```powershell
notepad .env.production
```

**Editeaza cu credentials reale:**
```bash
CHATURBATE_ENABLED=true
CHATURBATE_EVENTS_URL=https://events.chaturbate.com/events/your_username
CHATURBATE_API_KEY=your_real_api_key

STRIPCHAT_ENABLED=true
STRIPCHAT_EVENTS_URL=https://api.stripchat.com/v1/events
STRIPCHAT_TOKEN=your_real_token

CAMSODA_ENABLED=true
CAMSODA_EVENTS_URL=https://api.camsoda.com/external/events
CAMSODA_API_KEY=your_real_api_key
```

**2. Activeaza PRODUCTION mode:**
```powershell
switch_env.bat
# Selecteaza [2] - PRODUCTION MODE
# Confirma cu 'y'
```

**3. Porneste aplicatia:**
```powershell
python main.py
```

**Comportament:**
- Conecteaza la API-uri reale ale platformelor
- Proceseaza tips reale de la vieweri
- Toate filtrele sunt aplicate live

---

## Interfata Web

### Accesare Queue UI

**1. Asigura-te ca aplicatia ruleaza.**

**2. Deschide browser:**
```
http://127.0.0.1:8080/queue
```

**SAU foloseste run.bat:**
```powershell
run.bat
# Selecteaza [5] - Deschide Queue UI
```

### Componente UI

**Header:**
```
╔═══════════════════════════════════════╗
║   AR FILTER SYSTEM - COADA FILTRE     ║
╚═══════════════════════════════════════╝
```

**Stats Section:**
```
Statistici Coada:
  • Total items: 5
  • In procesare: 1
  • In asteptare: 4
```

**Queue List:**
```
┌───────────────────────────────────────┐
│ #1 - Filter 3 (50 tokens)             │
│   Tipper: user123                     │
│   Platform: chaturbate                │
│   Status: ⏳ In procesare              │
└───────────────────────────────────────┘

┌───────────────────────────────────────┐
│ #2 - Filter 5 (200 tokens)            │
│   Tipper: supporter99                 │
│   Platform: stripchat                 │
│   Status: ⏸️ In asteptare              │
└───────────────────────────────────────┘
```

**Footer:**
```
[Last Update: 12:34:56] [Auto-refresh: ON]
```

### Features UI

- **Real-Time Updates**: Se actualizeaza automat via SSE
- **Color Coding**: Verde (procesare), Galben (asteptare), Gri (completat)
- **Responsive**: Functioneaza pe telefon/tableta
- **Live Stats**: Contoare actualizate in timp real

### Menu Overlay (Optional)

```
http://127.0.0.1:8080/menu
```

Afiseaza meniu simplu cu filtre disponibile - util pentru overlay in OBS.

---

## Trigger Manual Filtre

### Combinatii Taste

Poti activa manual filtre prin combinatii de taste:

```
Ctrl+1  →  Filtru #1 (10 tokens)
Ctrl+2  →  Filtru #2 (20 tokens)
Ctrl+3  →  Filtru #3 (50 tokens)
Ctrl+4  →  Filtru #4 (100 tokens)
Ctrl+5  →  Filtru #5 (200 tokens)
Ctrl+6  →  Filtru #6 (500 tokens)
Ctrl+7  →  Filtru #7 (1000 tokens)
Ctrl+8  →  Filtru #8 (Custom)
Ctrl+9  →  Filtru #9 (Custom)
```

### Cum Functioneaza

**1. Apasa combinatia:**
```
Ctrl+3  (tine apasat Ctrl, apoi apasa 3)
```

**2. Sistemul adauga in coada:**
```
[manual] Taste apasate pentru activare: Ctrl+3
[manual] Adaugat in coada: Filter 3 (50 tokens)
```

**3. Filtrul este procesat:**
```
Procesez element din coada: Filter 3
Aplic tastele: ctrl+3
```

### Scenarii Folosire Manual

**Demo pentru vieweri:**
```
Ctrl+1  # Filtru simplu
Ctrl+3  # Filtru mediu
Ctrl+7  # Filtru premium
```

**Testare filtre:**
```
Ctrl+1, Ctrl+2, Ctrl+3...  # Test fiecare filtru
```

**Activare urgenta:**
```
Ctrl+5  # Filtru special pe cerere
```

---

## Gestionare Coada

### Logica Coada

**Priority Queue:**
- Suma mai mare = prioritate mai mare
- 200 tokens procesat inaintea 50 tokens
- FIFO pentru aceeasi prioritate

**Exemplu:**
```
Queue: [100 tokens, 50 tokens, 200 tokens]
        ↓ Sortare automata
Queue: [200 tokens, 100 tokens, 50 tokens]
        ↓ Procesare
Proceseaza: 200 → 100 → 50
```

### Configurare Mapping

**Editare mapping tip → filtru:**

```python
# In main.py
TIP_TO_KEYS = {
    10: "ctrl+1",     # 10 tokens → Filter 1
    20: "ctrl+2",     # 20 tokens → Filter 2
    50: "ctrl+3",     # 50 tokens → Filter 3
    100: "ctrl+4",    # 100 tokens → Filter 4
    200: "ctrl+5",    # 200 tokens → Filter 5
    500: "ctrl+6",    # 500 tokens → Filter 6
    1000: "ctrl+7",   # 1000 tokens → Filter 7
}
```

**Adaugare mapping nou:**
```python
TIP_TO_KEYS = {
    # ... existing
    150: "ctrl+8",    # 150 tokens → Filter 8 custom
}
```

**Restart aplicatia pentru a aplica modificarile.**

### Queue Size si Performance

**Configurare:**
```python
# In main.py, class FilterAutomation
self.filter_queue = Queue(maxsize=100)  # Max 100 items
```

**Recommended sizes:**
- **Mic stream**: maxsize=50
- **Mediu stream**: maxsize=100 (default)
- **Mare stream**: maxsize=200+

**Monitoring:**
```python
queue_size = self.filter_queue.qsize()
print(f"Coada: {queue_size} items")
```

---

## Monitorizare si Loguri

### Log Levels

**Console Logs:**
- `[platform]` - Evenimente platform-specific
- `[worker]` - Procesare coada
- `[manual]` - Trigger-uri manuale
- `[ui]` - Evenimente UI server

**Exemplu log output:**
```
[chaturbate] Primit tip: 100 tokens de la user123
[worker] Procesez element din coada: Filter 4
[worker] Aplic tastele: ctrl+4
[manual] Taste apasate pentru activare: Ctrl+5
[ui] Client conectat la stream
```

### Vizualizare Loguri

**Metoda 1: Live in terminal**
- Logurile apar in fereastra Python in timp real

**Metoda 2: Folosind run.bat**
```powershell
run.bat
# Selecteaza [4] - Vizualizeaza Loguri
```

**Redirectare loguri in fisier:**
```powershell
python main.py > output\app.log 2>&1
```

**Tail loguri (PowerShell):**
```powershell
Get-Content output\app.log -Wait -Tail 20
```

### Status Checking

**Verificare status aplicatie:**
```powershell
run.bat
# Selecteaza [6] - Verifica Status
```

**Output:**
```
=== STATUS PROGRAM ===
Program: RULEAZA
PID: 12345
Timp rulare: 01:23:45
```

**Verificare environment:**
```powershell
run.bat
# Selecteaza [7] - Verifica Environment
```

**Output:**
```
=== VERIFICARE MEDIU ===
Fisier configurare gasit: .env
Environment Type: test

Continut .env:
-----------------------------------------------------------
ENVIRONMENT=test
CHATURBATE_ENABLED=true
...
-----------------------------------------------------------
```

---

## Oprire Sistem

### Metoda 1: Ctrl+C (Graceful)

**In fereastra Python:**
```
Apasa Ctrl+C
```

**Output:**
```
^C
Oprire aplicatie...
Opresc keyboard listener...
Opresc worker thread...
Opresc listeners...
Cleanup complet.
La revedere!
```

### Metoda 2: run.bat

```powershell
run.bat
# Selecteaza [2] - Opreste Programul
```

**Output:**
```
Opresc programul...
Program oprit cu succes!
```

### Metoda 3: Kill Process

**Daca aplicatia nu raspunde:**
```powershell
# Gaseste PID
Get-Process python

# Kill process
Stop-Process -Name python -Force
```

**SAU foloseste Task Manager:**
- Ctrl+Shift+Esc
- Gaseste `python.exe`
- End Task

### Restart Application

**Quick restart:**
```powershell
run.bat
# Selecteaza [3] - Reporneste Programul
```

**Efectueaza:**
1. Opreste procesul existent
2. Asteapta 2 secunde
3. Porneste nou proces

---

## Scenarii Uzuale

### Scenario 1: Primul Streaming cu Sistemul

**Pasi:**

1. **Pregatire (30 min inainte de stream):**
   ```powershell
   # Verifica environment
   switch_env.bat → [3] Verifica environment
   
   # Start in TEST mode pentru verificare
   switch_env.bat → [1] TEST MODE
   python tests\mock_server.py
   ```

2. **Testare (15 min inainte):**
   ```powershell
   # Porneste aplicatia
   python main.py
   
   # Testeaza fiecare filtru manual
   Ctrl+1, Ctrl+2, ..., Ctrl+9
   
   # Verifica UI
   Browser: http://127.0.0.1:8080/queue
   ```

3. **Switch la PRODUCTION (5 min inainte):**
   ```powershell
   # Opreste TEST
   Ctrl+C (in fiecare terminal)
   
   # Activeaza PRODUCTION
   switch_env.bat → [2] PRODUCTION MODE
   
   # Porneste aplicatia
   python main.py
   ```

4. **During Stream:**
   - Monitoreaza logurile
   - Check UI periodic
   - Trigger manual daca e necesar

5. **Dupa Stream:**
   ```powershell
   # Opreste graceful
   Ctrl+C
   ```

### Scenario 2: Debug - Filtre Nu Se Aplica

**Diagnostic:**

1. **Verifica fereastra Python e deschisa:**
   ```
   Cauza: Keyboard listener inactiv
   Solutie: Pastreaza fereastra deschisa
   ```

2. **Verifica taste corecte:**
   ```powershell
   # Check mapping in main.py
   TIP_TO_KEYS = {...}
   ```

3. **Test manual:**
   ```
   Ctrl+1  # Ar trebui sa se logheze
   ```

4. **Verifica pynput:**
   ```powershell
   pip show pynput
   # Reinstall daca e necesar
   pip install --force-reinstall pynput
   ```

5. **Check Admin Rights:**
   ```
   Unele aplicatii necesita Admin
   Click dreapta run.bat → Run as Administrator
   ```

### Scenario 3: Setup pentru Multiple Platforme

**Exemplu: Streamezi simultan pe 2 platforme**

**Configurare:**
```bash
# .env.production
CHATURBATE_ENABLED=true
CHATURBATE_EVENTS_URL=https://...

STRIPCHAT_ENABLED=true
STRIPCHAT_EVENTS_URL=https://...

CAMSODA_ENABLED=false  # Nu folosesti
```

**Pornire:**
```powershell
switch_env.bat → [2] PRODUCTION
python main.py
```

**Rezultat:**
- Asculta Chaturbate + Stripchat
- Proceseaza tips de pe ambele platforme
- O singura coada unified

### Scenario 4: Demo pentru Vieweri

**Setup rapid demo:**

1. **Activeaza TEST mode:**
   ```powershell
   switch_env.bat → [1] TEST MODE
   python tests\mock_server.py
   ```

2. **Porneste aplicatia:**
   ```powershell
   python main.py
   ```

3. **Arata UI pe stream (OBS):**
   - Browser source: `http://127.0.0.1:8080/queue`
   - Transparent background available

4. **Trigger manual filtre pentru demo:**
   ```
   "La 10 tokens → Filter 1" → Ctrl+1
   "La 50 tokens → Filter 3" → Ctrl+3
   "La 200 tokens → Filter 5" → Ctrl+5
   ```

5. **Mock server genereaza tips automat** - arata procesare live

### Scenario 5: Customizare Mapping Filtre

**Task: Adauga filtru special la 75 tokens**

**1. Editeaza main.py:**
```python
TIP_TO_KEYS = {
    10: "ctrl+1",
    20: "ctrl+2",
    50: "ctrl+3",
    75: "ctrl+8",     # NOU - filtru custom
    100: "ctrl+4",
    # ... rest
}
```

**2. Configureaza taste in AR app:**
- Ctrl+8 → Filter special

**3. Restart aplicatia:**
```powershell
run.bat → [3] Reporneste
```

**4. Test:**
```
Ctrl+8  # Verifica filtru se activeaza corect
```

---

## Troubleshooting Utilizare

### Problema: Aplicatia nu porneste

**Check 1: Python ruleaza?**
```powershell
Get-Process python
```

**Check 2: Port ocupat?**
```powershell
netstat -ano | findstr :8080
# Daca e ocupat, opreste procesul
```

**Check 3: .env exista?**
```powershell
Test-Path .env
# Daca nu exista
Copy-Item .env.test .env
```

### Problema: Nu primesc evenimente

**TEST Mode:**
- Mock server ruleaza? → python tests\mock_server.py
- URL corect in .env? → http://127.0.0.1:5000/...

**PRODUCTION Mode:**
- API keys valide? → Verifica in .env.production
- Internet connection? → ping api.platform.com
- Rate limit? → Check loguri pentru "429" errors

### Problema: Queue UI nu se incarca

**Check 1: Server ruleaza?**
```
Verifica in loguri: "Serverul Queue UI porneste pe..."
```

**Check 2: Port corect?**
```
Browser: http://127.0.0.1:8080/queue
NU: localhost (foloseste IP)
```

**Check 3: Firewall?**
```powershell
# Adauga exceptie
netsh advfirewall firewall add rule name="Flask" dir=in action=allow protocol=TCP localport=8080
```

### Problema: Taste manuale nu functioneaza

**Fix 1: Pastreaza fereastra Python deschisa**
```
Fereastra Python = Keyboard listener activ
Inchis fereastra = Taste inactive
```

**Fix 2: Run as Administrator**
```
Click dreapta run.bat → Run as Administrator
```

**Fix 3: Check aplicatie target**
```
Focus aplicatia AR unde vrei sa trimiti tastele
```

### Problema: Filtre se aplica incet

**Posibile cauze:**

1. **Coada mare:**
   ```python
   # Creste workers (in main.py)
   # Adauga multiple worker threads
   ```

2. **Delay mari:**
   ```python
   # In KeySender.__init__
   self.key_delay = 0.05  # Reduce delay
   ```

3. **Sistem supraincărcat:**
   - Inchide aplicatii nefolosite
   - Check CPU usage

### Problema: Duplicate events

**Normal behavior:**
- Sistemul permite duplicate intentionat
- Daca primesti 2 tips de 100, ambele se proceseaza

**Daca vrei filtering:**
```python
# In main.py, add_to_queue
# Implementeaza duplicate detection logic
```

---

## Tips & Tricks

### Tip 1: Hotkeys pentru Productivitate

**Setup global hotkeys (optional):**
```python
# In main.py
keyboard.add_hotkey('f9', lambda: self.toggle_pause())
keyboard.add_hotkey('f10', lambda: self.clear_queue())
```

### Tip 2: Queue UI in OBS

**Add Browser Source:**
1. OBS → Sources → Browser
2. URL: `http://127.0.0.1:8080/queue`
3. Width: 400, Height: 600
4. CSS: `body {background: transparent;}`

### Tip 3: Logging Advanced

**Log la fisier automat:**
```powershell
# Creaza start script
python main.py 2>&1 | Tee-Object -FilePath "output\log_$(Get-Date -Format 'yyyy-MM-dd').log"
```

### Tip 4: Multi-Monitor Setup

- **Monitor 1**: OBS + AR App
- **Monitor 2**: Python logs
- **Monitor 3 (optional)**: Queue UI browser

### Tip 5: Quick Restart Hotkey

**Adauga in run.bat sau creaza restart.bat:**
```batch
@echo off
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
start python main.py
```

---

## Next Steps

Dupa ce esti familiar cu utilizarea:

1. **[DEZVOLTARE.md](DEZVOLTARE.md)** - Customizeaza si extinde sistemul
2. **[API_INTEGRATION.md](API_INTEGRATION.md)** - Intelegere profunda API-uri
3. **[ARHITECTURA.md](ARHITECTURA.md)** - Intelege cum functioneaza intern

---

## Feedback & Support

**Raportare probleme:**
- Include versiune Python
- Attach loguri relevante
- Descrie pasi reproducere

**Feature requests:**
- Deschide GitHub Issue
- Descrie use case
- Sugereaza implementare

Mult succes cu streaming-ul! 🚀
