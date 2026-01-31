# Ghid Instalare - AR Filter System V1

## Cuprins

1. [Cerinte Sistem](#cerinte-sistem)
2. [Instalare Automata](#instalare-automata)
3. [Instalare Manuala](#instalare-manuala)
4. [Configurare Initiala](#configurare-initiala)
5. [Verificare Instalare](#verificare-instalare)
6. [Troubleshooting](#troubleshooting)
7. [Dezinstalare](#dezinstalare)

---

## Cerinte Sistem

### Software Obligatoriu

- **Python 3.8+** (Recomandat: Python 3.10 sau 3.11)
- **pip** (Package installer pentru Python)
- **Git** (Optional, pentru clonare repository)

### Sistem de Operare

- **Windows 10/11** (x64)
- **RAM**: Minim 2GB, Recomandat 4GB+
- **Spatiu Disk**: ~500MB pentru aplicatie si dependente
- **Internet**: Conexiune stabila pentru API calls

### Verificare Python

```powershell
# Verifica versiunea Python
python --version
# Output asteptat: Python 3.8.x sau mai nou

# Verifica pip
pip --version
# Output asteptat: pip XX.X.X
```

**Daca Python nu este instalat:**
1. Download de la: https://www.python.org/downloads/
2. **IMPORTANT**: Bifat "Add Python to PATH" la instalare
3. Restart terminal dupa instalare

---

## Instalare Automata

### Metoda Recomandata

Script-ul `setup.bat` automatizeaza intregul proces de instalare.

### Pasi Instalare

**1. Navigheaza in directorul proiectului:**
```powershell
cd C:\Users\YourName\AR_Filter_System_V1
```

**2. Ruleaza setup.bat:**
```powershell
setup.bat
```

**3. Urmareste procesul:**

```
============================================================
   INSTALARE AR FILTER SYSTEM - MULTI-PLATFORMA
============================================================

[Pasul 1/6] Verific instalarea Python...
✓ Python gasit: Python 3.10.5

[Pasul 2/6] Verific pip...
✓ pip gasit: pip 23.2.1

[Pasul 3/6] Actualizez pip...
✓ pip actualizat

[Pasul 4/6] Instalez dependente Python...
✓ Toate pachetele instalate cu succes

[Pasul 5/6] Creez directoare necesare...
✓ Director recordings/ creat
✓ Director output/ creat

[Pasul 6/6] Configurez environment...
✓ Fisier .env creat (TEST mode)

============================================================
              INSTALARE COMPLETA!
============================================================
```

### Dupa Instalare Automata

Sistemul este gata de folosit! Continua la [Configurare Initiala](#configurare-initiala).

---

## Instalare Manuala

### Cand folosesti instalarea manuala?

- Setup.bat nu functioneaza
- Vrei control granular
- Debugging probleme instalare

### Pasi Detaliati

#### 1. Cloneaza Repository (daca e pe Git)

```powershell
git clone https://github.com/yourusername/AR_Filter_System_V1.git
cd AR_Filter_System_V1
```

**SAU** descarca si extrage ZIP-ul proiectului.

#### 2. Creaza Virtual Environment (Optional dar Recomandat)

```powershell
# Creaza venv
python -m venv venv

# Activeaza venv
.\venv\Scripts\Activate.ps1

# Prompt-ul se va schimba: (venv) PS C:\...>
```

**Nota**: Virtual environment izoleaza dependentele proiectului.

#### 3. Actualizeaza pip

```powershell
python -m pip install --upgrade pip
```

#### 4. Instaleaza Dependente

```powershell
pip install -r requirements.txt
```

**Output asteptat:**
```
Collecting Flask==3.1.2
  Downloading Flask-3.1.2-py3-none-any.whl (102 kB)
Collecting pynput==1.7.7
  Downloading pynput-1.7.7-py2.py3-none-any.whl (89 kB)
...
Successfully installed Flask-3.1.2 pynput-1.7.7 ...
```

#### 5. Creaza Directoare Necesare

```powershell
# Creaza directoare
New-Item -ItemType Directory -Force -Path recordings
New-Item -ItemType Directory -Force -Path output

# Verifica
Test-Path recordings  # True
Test-Path output      # True
```

#### 6. Configureaza Environment

```powershell
# Copiaza template TEST
Copy-Item .env.test .env

# Verifica
Test-Path .env  # True
```

---

## Configurare Initiala

### Environment Modes

Sistemul suporta doua moduri:

- **TEST MODE**: Foloseste mock server (nu necesita API keys reale)
- **PRODUCTION MODE**: Foloseste API-uri reale (necesita credentials)

### Configurare TEST Mode (Recomandat Initial)

**1. Verifica ca .env este copiat din .env.test:**
```powershell
type .env
```

**Output asteptat:**
```bash
# TEST MODE CONFIGURATION
ENVIRONMENT=test

# Chaturbate Mock
CHATURBATE_ENABLED=true
CHATURBATE_EVENTS_URL=http://127.0.0.1:5000/events/chaturbate
CHATURBATE_POLL_INTERVAL=5

# Similar pentru Stripchat si Camsoda
```

**2. Porneste Mock Server:**
```powershell
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
```

**Lasa fereastra deschisa!** Mock server trebuie sa ruleze in background.

### Configurare PRODUCTION Mode

**IMPORTANT**: Necesita API credentials valide de la platforme.

**1. Editeaza .env.production:**
```powershell
notepad .env.production
```

**2. Completeaza API Keys:**
```bash
# PRODUCTION MODE CONFIGURATION
ENVIRONMENT=production

# Chaturbate Real API
CHATURBATE_ENABLED=true
CHATURBATE_EVENTS_URL=https://events.chaturbate.com/events/your_username
CHATURBATE_API_KEY=your_real_api_key_here
CHATURBATE_POLL_INTERVAL=5

# Stripchat Real API
STRIPCHAT_ENABLED=true
STRIPCHAT_EVENTS_URL=https://api.stripchat.com/v1/events
STRIPCHAT_TOKEN=your_real_token_here
STRIPCHAT_POLL_INTERVAL=5

# Camsoda Real API
CAMSODA_ENABLED=true
CAMSODA_EVENTS_URL=https://api.camsoda.com/external/events
CAMSODA_API_KEY=your_real_api_key_here
CAMSODA_POLL_INTERVAL=5
```

**3. Activeaza PRODUCTION mode:**
```powershell
switch_env.bat
# Selecteaza optiunea [2] - PRODUCTION MODE
```

### Obtinere API Keys

#### Chaturbate
1. Login pe Chaturbate ca broadcaster
2. Acceseaza Settings → API Settings
3. Genereaza Events API key
4. Copiaza si salveaza in .env.production

#### Stripchat
1. Login pe Stripchat
2. Dashboard → Developer Settings
3. Creaza API Token
4. Copiaza token-ul

#### Camsoda
1. Contacteaza suportul Camsoda
2. Solicita External API access
3. Primesti API credentials prin email

---

## Verificare Instalare

### Check 1: Dependente Python

```powershell
pip list
```

**Verifica ca sunt prezente:**
```
Flask           3.1.2
pynput          1.7.7
python-dotenv   1.0.1
requests        2.xx.x
```

### Check 2: Structura Fisiere

```powershell
Get-ChildItem -Recurse -Depth 1 -Directory
```

**Output asteptat:**
```
core/
recordings/
output/
templates/
tests/
```

### Check 3: Test Import Module

```powershell
python -c "import main; print('OK')"
```

**Output:** `OK`

**Daca primesti eroare:**
```powershell
# Reinstaleaza dependentele
pip install --force-reinstall -r requirements.txt
```

### Check 4: Test Mock Server

**Terminal 1:**
```powershell
python tests\mock_server.py
```

**Terminal 2:**
```powershell
curl http://127.0.0.1:5000/events/chaturbate
```

**Output JSON asteptat:**
```json
{"events": [...]}
```

### Check 5: Test Main Application

```powershell
python main.py
```

**Output asteptat:**
```
[chaturbate] Listener Chaturbate pornit pe http://127.0.0.1:5000/...
[stripchat] Listener Stripchat pornit pe http://127.0.0.1:5000/...
...
Thread worker pornit pentru procesare coada
Taste manuale activate: Ctrl+1...Ctrl+9
Serverul Queue UI porneste pe http://127.0.0.1:8080
```

**Apasa Ctrl+C pentru a opri.**

### Check 6: Test UI Web

1. Porneste aplicatia: `python main.py`
2. Deschide browser: `http://127.0.0.1:8080/queue`
3. Verifica pagina se incarca corect

---

## Troubleshooting

### Problema: Python nu este recunoscut

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solutie:**
1. Reinstaleaza Python cu "Add to PATH" bifat
2. SAU adauga manual Python la PATH:
   - System Properties → Environment Variables
   - Path → Edit → New → `C:\Python310\` (path-ul tau Python)
3. Restart terminal

### Problema: pip nu functioneaza

**Error:**
```
'pip' is not recognized...
```

**Solutie:**
```powershell
# Foloseste python -m pip
python -m pip install -r requirements.txt
```

### Problema: Eroare la instalare pynput

**Error:**
```
ERROR: Could not build wheels for pynput
```

**Solutie Windows:**
```powershell
# Instaleaza Visual C++ Build Tools
# Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# SAU foloseste pre-built wheel
pip install --only-binary :all: pynput
```

### Problema: Permission denied la creare directoare

**Error:**
```
Permission denied: 'recordings'
```

**Solutie:**
```powershell
# Ruleaza PowerShell ca Administrator
# SAU schimba ownership
icacls recordings /grant Users:F
```

### Problema: Port 5000 sau 8080 deja folosit

**Error:**
```
OSError: [WinError 10048] Address already in use
```

**Solutie:**
```powershell
# Gaseste procesul care foloseste portul
netstat -ano | findstr :5000

# Opreste procesul
taskkill /PID <PID> /F

# SAU schimba portul in .env
QUEUE_UI_PORT=8081
MOCK_SERVER_PORT=5001
```

### Problema: Mock server nu raspunde

**Verificari:**
1. Mock server ruleaza? (verifica terminal)
2. Firewall blocheaza portul?
   ```powershell
   # Adauga regula firewall
   netsh advfirewall firewall add rule name="Python" dir=in action=allow program="C:\Python310\python.exe"
   ```
3. URL corect in .env? (127.0.0.1, nu localhost)

### Problema: Taste nu se declanseaza

**Verificari:**
1. Fereastra Python ramane deschisa?
2. pynput instalat corect?
   ```powershell
   pip show pynput
   ```
3. Administrator rights necesare?
   - Click dreapta → Run as Administrator

### Problema: .env nu se incarca

**Error:**
```
KeyError: 'CHATURBATE_ENABLED'
```

**Solutie:**
```powershell
# Verifica .env exista
Test-Path .env

# Recreeaza din template
Copy-Item .env.test .env -Force

# Verifica encoding (trebuie sa fie UTF-8)
[System.IO.File]::ReadAllText(".env").GetType()
```

### Problema: Import errors

**Error:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solutie:**
```powershell
# Verifica virtual environment
# Daca folosesti venv, asigura-te ca e activat
.\venv\Scripts\Activate.ps1

# Reinstaleaza
pip install -r requirements.txt --force-reinstall
```

---

## Post-Installation Setup

### Configurare Shortcuts (Optional)

**Creaza shortcut pentru pornire rapida:**

1. Click dreapta Desktop → New → Shortcut
2. Location: `C:\Windows\System32\cmd.exe /c "cd /d C:\Path\To\AR_Filter_System && run.bat"`
3. Name: "AR Filter System"
4. Icon: Schimba daca vrei

**Shortcut Quick Launch:**
```powershell
# Creaza BAT file
@echo off
cd /d "C:\Path\To\AR_Filter_System_V1"
call run.bat
```

### Configurare Autostart (Optional)

**Pornire automata cu Windows:**

1. Apasa `Win + R` → `shell:startup`
2. Creaza shortcut catre `run.bat` in acest folder
3. Editeaza shortcut properties:
   - Target: `cmd /c "cd ... && run.bat"`
   - Start in: path-ul proiectului
   - Run: Minimized

### Configurare Firewall

**Permite Python prin firewall:**
```powershell
# Run as Administrator
netsh advfirewall firewall add rule name="AR Filter - Python" dir=in action=allow program="C:\Python310\python.exe" enable=yes

netsh advfirewall firewall add rule name="AR Filter - Flask" dir=in action=allow protocol=TCP localport=8080
```

---

## Update System

### Update Dependente

```powershell
# Update toate pachetele
pip install --upgrade -r requirements.txt

# Update pip insusi
python -m pip install --upgrade pip
```

### Update Cod

**Daca folosesti Git:**
```powershell
# Pull latest changes
git pull origin main

# Reinstall dependencies (daca s-au schimbat)
pip install -r requirements.txt
```

**Daca folosesti ZIP:**
1. Download ultima versiune
2. Extract peste fisierele existente (preserveaza .env!)
3. Run `pip install -r requirements.txt`

---

## Dezinstalare

### Dezinstalare Completa

**1. Opreste toate procesele:**
```powershell
run.bat
# Selecteaza [2] - Opreste Programul
```

**2. Dezactiveaza virtual environment (daca e folosit):**
```powershell
deactivate
```

**3. Sterge directorul proiect:**
```powershell
Remove-Item -Recurse -Force C:\Path\To\AR_Filter_System_V1
```

**4. Dezinstaleaza Python packages (optional):**
```powershell
pip uninstall -r requirements.txt -y
```

### Cleanup Partial

**Pastreaza configuratia, sterge doar cache:**
```powershell
# Sterge Python cache
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Sterge logs vechi
Remove-Item output\*.log -Force

# Sterge recordings vechi
Remove-Item recordings\* -Force
```

---

## Backup si Restore

### Backup Configuration

**Importante de salvat:**
```
.env
.env.production
recordings/        (optional)
output/logs/       (optional)
```

**Comanda Backup:**
```powershell
# Creaza arhiva
Compress-Archive -Path .env,.env.production,recordings -DestinationPath "backup_$(Get-Date -Format 'yyyy-MM-dd').zip"
```

### Restore Configuration

```powershell
# Extrage backup
Expand-Archive -Path backup_2024-01-15.zip -DestinationPath .

# Verifica .env
Test-Path .env
```

---

## FAQ Instalare

**Q: Pot folosi Python 3.7?**
A: Nu recomandat. Foloseste Python 3.8+. Unele features pot nu functiona pe 3.7.

**Q: Trebuie sa folosesc virtual environment?**
A: Nu e obligatoriu, dar e best practice. Izoleaza dependentele proiectului.

**Q: Pot instala pe Linux/Mac?**
A: Codul Python functioneaza, dar BAT files sunt Windows-only. Adapteaza cu bash scripts.

**Q: Cat dureaza instalarea?**
A: ~5-10 minute cu setup.bat automat, ~15-20 minute manual.

**Q: Pot rula multiple instante?**
A: Nu recomandat. O instanta per masina este suficient.

**Q: Unde gasesc loguri daca ceva nu merge?**
A: In terminal unde ai pornit aplicatia, si in `output/` daca ai activat file logging.

---

## Next Steps

Dupa instalare reusita:

1. **[Citeste UTILIZARE.md](UTILIZARE.md)** - Cum sa folosesti sistemul
2. **[Citeste API_INTEGRATION.md](API_INTEGRATION.md)** - Setup API credentials
3. **Testeaza in TEST mode** - Familiarizeaza-te cu sistemul
4. **Configureaza PRODUCTION** - Doar dupa ce esti confortabil

---

## Support

**Daca intampini probleme:**
1. Verifica [Troubleshooting](#troubleshooting)
2. Check GitHub Issues
3. Contacteaza suportul tehnic

**Include in raportul de bug:**
- Versiune Python (`python --version`)
- Versiune OS (Windows 10/11)
- Continut fisier `requirements.txt`
- Error message complet
- Pasi care reproduc problema
