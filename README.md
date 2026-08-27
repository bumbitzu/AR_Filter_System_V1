# 🚀 Quick Start Guide - Multi-Platform AR Filter System

## 📦 Instalare Dependențe

```bash
pip install -r requirements.txt
```

## ⚙️ Configurare Environment (ВАЖНО!)

Sistemul folosește fișiere `.env` pentru configurare. Există 2 environment-uri:

### Test Mode (Implicit)
Folosit pentru testare cu mock server local.

**Activare automată:**
Fișierul `.env` este deja configurat pentru test mode.

**Activare manuală (opțional):**
```bash
# Windows
copy .env.test .env

# Linux/Mac
cp .env.test .env
```

### Production Mode
Folosit cu API-uri reale. **Necesită API keys!**

1. Completează `.env.production` cu API keys reale
2. Activează:
```bash
# Windows
copy .env.production .env

# Linux/Mac
cp .env.production .env
```

**🎯 Shortcut:** Rulează `switch_env.bat` (Windows) pentru meniu interactiv!

📖 **Detalii complete:** Vezi [ENV_GUIDE.md](ENV_GUIDE.md)

---

## 🎯 Utilizare Rapidă

### Pas 1: Pornește Mock Server
Într-un terminal:
```bash
python tests/mock_server.py
```

Ar trebui să vezi:
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

### Pas 2: Rulează Testele (Opțional)
Într-un al doilea terminal:
```bash
python tests/test_multi_platform.py
```

Acest script va testa automat toate cele 3 platforme.

### Pas 3: Pornește Aplicația Principală
```bash
python main.py
```

Vei fi întrebat să selectezi camera (alege indexul camerei tale).

### Pas 4: Testează Filtrele

**Opțiune A: Browser (Recomandat)**
1. Deschide http://127.0.0.1:5000 în browser
2. Click pe link-urile de test pentru fiecare platformă
3. Observă filtrele activate în aplicația AR

**Opțiune B: Tastatura (Fără Server)**
În aplicația AR, apasă:
- `1` - Activează filtru Sparkles
- `2` - Activează filtru Big Eyes
- `3` - Activează filtru Cyber Mask
- `q` - Închide aplicația

## 🎨 Filtre Disponibile

| Tokens | Tastă | Filtru       | Durată |
|--------|-------|-------------|--------|
| 33     | 1     | Sparkles    | 10s    |
| 99     | 2     | Big Eyes    | 20s    |
| 200    | 3     | Cyber Mask  | 30s    |

## 🔧 Configurare

### Activare/Dezactivare Platforme

Editează `main.py`:

```python
# Pentru toate platformele:
CHATURBATE_URL = "http://127.0.0.1:5000/events/chaturbate"
STRIPCHAT_URL = "http://127.0.0.1:5000/events/stripchat"
CAMSODA_URL = "http://127.0.0.1:5000/events/camsoda"

# Pentru a dezactiva Stripchat:
CHATURBATE_URL = "http://127.0.0.1:5000/events/chaturbate"
STRIPCHAT_URL = None
CAMSODA_URL = "http://127.0.0.1:5000/events/camsoda"
```

### Schimbare Output Mode

```python
app = CameraFiltersAutomation(
    chaturbate_url=CHATURBATE_URL,
    stripchat_url=STRIPCHAT_URL,
    camsoda_url=CAMSODA_URL,
    output_mode="window",  # sau "vcam" pentru virtual camera
    quality="1080p"        # sau "4K"
)
```

## 📚 Documentație Detaliată

Pentru informații complete despre arhitectură, normalizarea datelor și gestionarea erorilor, consultă:
- **[MULTI_PLATFORM_GUIDE.md](MULTI_PLATFORM_GUIDE.md)** - Ghid complet

## 🐛 Troubleshooting

### Eroare: "Cannot connect to server"
- Verifică că `mock_server.py` rulează
- Verifică că port-ul 5000 nu este blocat

### Eroare: "No cameras detected"
- Verifică că o cameră este conectată
- Pe Windows, permite acces la cameră în Settings

### Filtrele nu se activează
- Verifică consolă pentru erori
- Asigură-te că suma tokens-urilor este exact 33, 99 sau 200
- Verifică că listener-ele au pornit cu succes

### Un API nu răspunde
Sistemul va afișa:
```
⚠️ Stripchat API connection failed. Retrying in 5s...
```
Celelalte platforme vor continua să funcționeze normal.

## 📞 Structura Proiectului

```
AR_Filter_System_V1/
├── main.py                          # Aplicația principală
├── requirements.txt                 # Dependențe Python
├── MULTI_PLATFORM_GUIDE.md         # Documentație detaliată
├── README_QUICK_START.md           # Acest fișier
│
├── core/
│   ├── OutputManager.py            # Manager video output
│   ├── ChaturbateListener.py       # Listener Chaturbate
│   ├── StripchatListener.py        # Listener Stripchat
│   └── CamsodaListener.py          # Listener Camsoda
│
├── filters/
│   ├── BigEyeFilter.py             # Filtru ochi mari
│   ├── FaceMask3DFilter.py         # Filtru mască 3D
│   └── RainSparkleFilter.py        # Filtru particule
│
└── tests/
    ├── mock_server.py              # Server de testare
    └── test_multi_platform.py      # Script auto-testare
```

## 🎉 Success!

Dacă ai ajuns până aici și totul funcționează, sistemul tău AR Filter suportă acum 3 platforme simultan! 🚀

Pentru întrebări sau probleme, consultă documentația detaliată din `MULTI_PLATFORM_GUIDE.md`.
