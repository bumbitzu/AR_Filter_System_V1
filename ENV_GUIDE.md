# 🔄 Ghid de Utilizare Environment Files (.env)

## 📋 Prezentare Generală

Sistemul AR Filter folosește fișiere `.env` pentru a gestiona configurația. Acest lucru permite schimbarea ușoară între environment-uri (test/producție) fără a modifica codul.

---

## 📁 Fișiere Disponibile

### 1. **`.env.test`** - Configurație pentru Testare
- Mock server local (http://127.0.0.1:5000)
- Toate platformele activate
- Output mode: window
- Debug mode: activat

### 2. **`.env.production`** - Template pentru Producție
- API-uri reale (placeholders)
- Necesită completare cu API keys reale
- Output mode: vcam
- Debug mode: dezactivat

### 3. **`.env`** - Fișier Activ
- Fișierul folosit efectiv de aplicație
- Trebuie să fie copie din `.env.test` SAU `.env.production`
- **NU UPLOADA acest fișier pe GitHub!**

---

## 🚀 Cum să Schimbi Environment-ul

### Mod TEST (Mock Server)

**Windows:**
```cmd
copy .env.test .env
```

**Linux/Mac:**
```bash
cp .env.test .env
```

Apoi pornește aplicația:
```bash
python main.py
```

Ar trebui să vezi:
```
============================================================
🚀 AR FILTER SYSTEM - TEST MODE
============================================================

📡 Platforme configurate:
   ✅ Chaturbate: http://127.0.0.1:5000/events/chaturbate
   ✅ Stripchat: http://127.0.0.1:5000/events/stripchat
   ✅ Camsoda: http://127.0.0.1:5000/events/camsoda

⚙️  Settings:
   Output Mode: window
   Quality: 1080p
   Debug Mode: On
============================================================
```

---

### Mod PRODUCTION (API-uri Reale)

#### Pas 1: Completează API Keys

Editează **`.env.production`** și completează cu API keys reale:

```bash
# CHATURBATE
CHATURBATE_USERNAME=your_actual_username
CHATURBATE_TOKEN=abc123xyz789

# STRIPCHAT
STRIPCHAT_TOKEN=def456uvw012

# CAMSODA
CAMSODA_API_KEY=ghi789rst345
```

#### Pas 2: Activează Production Environment

**Windows:**
```cmd
copy .env.production .env
```

**Linux/Mac:**
```bash
cp .env.production .env
```

#### Pas 3: Rulează Aplicația

```bash
python main.py
```

Ar trebui să vezi:
```
============================================================
🚀 AR FILTER SYSTEM - PRODUCTION MODE
============================================================

📡 Platforme configurate:
   ✅ Chaturbate: https://eventsapi.chaturbate.com/events/...
   ✅ Stripchat: https://b2b.stripchat.com/api/...
   ✅ Camsoda: https://api.camsoda.com/api/v1/events/...

⚙️  Settings:
   Output Mode: vcam
   Quality: 1080p
   Debug Mode: Off
============================================================
```

---

## ⚙️ Configurații Disponibile

### Variables Environment

| Variabilă | Descriere | Valori Acceptate | Default |
|-----------|-----------|------------------|---------|
| `ENVIRONMENT` | Tipul environment-ului | test, production | test |
| `CHATURBATE_ENABLED` | Activează Chaturbate | true, false | true |
| `STRIPCHAT_ENABLED` | Activează Stripchat | true, false | true |
| `CAMSODA_ENABLED` | Activează Camsoda | true, false | true |
| `OUTPUT_MODE` | Modul de output | window, vcam | window |
| `QUALITY` | Calitatea video | 1080p, 4K | 1080p |
| `DEBUG_MODE` | Mod debug | true, false | false |
| `VERBOSE_LOGGING` | Logging detaliat | true, false | false |

---

## 🎯 Exemple de Configurări Personalizate

### Exemplu 1: Doar Chaturbate în Test Mode

Editează `.env`:
```bash
ENVIRONMENT=test
CHATURBATE_ENABLED=true
STRIPCHAT_ENABLED=false
CAMSODA_ENABLED=false
CHATURBATE_URL=http://127.0.0.1:5000/events/chaturbate
OUTPUT_MODE=window
QUALITY=1080p
```

### Exemplu 2: Stripchat + Camsoda în Production

Editează `.env`:
```bash
ENVIRONMENT=production
CHATURBATE_ENABLED=false
STRIPCHAT_ENABLED=true
CAMSODA_ENABLED=true
STRIPCHAT_URL=https://b2b.stripchat.com/api/events?token=YOUR_TOKEN
CAMSODA_URL=https://api.camsoda.com/v1/events?api_key=YOUR_KEY
OUTPUT_MODE=vcam
QUALITY=4K
```

### Exemplu 3: 4K Output în Window Mode

Editează `.env`:
```bash
ENVIRONMENT=test
OUTPUT_MODE=window
QUALITY=4K
# ... restul configurației
```

---

## 🔒 Securitate

### ⚠️ IMPORTANT: Best Practices

1. **NU uploada `.env` sau `.env.production` pe GitHub**
   - Aceste fișiere conțin API keys sensibile
   - Sunt deja în `.gitignore`

2. **Păstrează `.env.test` public**
   - Conține doar URL-uri locale
   - Sigur pentru versioning

3. **Backup pentru `.env.production`**
   - Salvează într-un loc sigur (KeePass, 1Password, etc.)
   - NU în repository

4. **Schimbă API keys regulat**
   - Lunar sau trimestrial
   - După orice suspiciune de compromitere

---

## 🐛 Troubleshooting

### Eroare: "No module named 'dotenv'"

**Soluție:**
```bash
pip install python-dotenv
```
SAU
```bash
pip install -r requirements.txt
```

---

### Eroare: Configurația nu se încarcă

**Verificări:**
1. Există fișierul `.env` în folder-ul root al proiectului?
   ```bash
   dir .env          # Windows
   ls -la .env       # Linux/Mac
   ```

2. `.env` este copie din `.env.test` sau `.env.production`?
   ```bash
   type .env         # Windows
   cat .env          # Linux/Mac
   ```

3. Format corect în `.env`:
   - Fără spații în jurul `=`
   - Fără ghilimele în jurul valorilor
   ```bash
   # ✅ Corect
   OUTPUT_MODE=window
   
   # ❌ Greșit
   OUTPUT_MODE = "window"
   ```

---

### Platformele nu se activează

**Verifică că variabilele ENABLED sunt true:**
```bash
CHATURBATE_ENABLED=true
STRIPCHAT_ENABLED=true
CAMSODA_ENABLED=true
```

**NU:**
```bash
CHATURBATE_ENABLED=True    # Majuscula nu funcționează
CHATURBATE_ENABLED="true"  # Ghilimelele nu sunt necesare
```

---

## 📊 Verificare Configurație

Pentru a vedea ce configurație este încărcată, rulează:

```bash
python main.py
```

Aplicația va afișa la startup:
- Environment mode (TEST/PRODUCTION)
- Platforme activate/dezactivate
- Settings (output_mode, quality, debug_mode)

Exemplu output:
```
============================================================
🚀 AR FILTER SYSTEM - TEST MODE
============================================================

📡 Platforme configurate:
   ✅ Chaturbate: http://127.0.0.1:5000/events/chaturbate
   ✅ Stripchat: http://127.0.0.1:5000/events/stripchat
   ❌ Camsoda: Disabled

⚙️  Settings:
   Output Mode: window
   Quality: 1080p
   Debug Mode: On
============================================================
```

---

## 🔄 Revenire la Mod Test

Dacă vrei să revii rapid la testare:

**Windows:**
```cmd
copy .env.test .env
python main.py
```

**Linux/Mac:**
```bash
cp .env.test .env
python main.py
```

---

## 📞 Quick Reference

| Acțiune | Windows | Linux/Mac |
|---------|---------|-----------|
| Activează Test Mode | `copy .env.test .env` | `cp .env.test .env` |
| Activează Production | `copy .env.production .env` | `cp .env.production .env` |
| Verifică .env activ | `type .env` | `cat .env` |
| Editează .env | `notepad .env` | `nano .env` |

---

## ✅ Checklist: Trecere la Production

- [ ] Obține API keys de la toate platformele
- [ ] Editează `.env.production` cu keys reale
- [ ] Verifică că `.env.production` este în `.gitignore`
- [ ] Copiază `.env.production` ca `.env`
- [ ] Rulează `python main.py` și verifică că toate platformele conectează
- [ ] Testează câteva tips pentru a valida
- [ ] Salvează backup `.env.production` într-un manager de parole

---

**Creat**: 2026-01-28  
**Versiune**: 1.0  
**Status**: Production Ready
