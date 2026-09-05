# AR Filter System V1

## Descriere Generala

AR Filter System V1 este un sistem automatizat de aplicare a filtrelor AR bazat pe tipuri (tips) primite pe platformele de streaming live. Sistemul asculta evenimente in timp real de la Chaturbate, Stripchat si Camsoda, si declanseaza automat taste configurate pentru a activa filtre AR.

## Caracteristici Principale

- ✅ **Multi-Platform**: Suporta Chaturbate, Stripchat si Camsoda
- ✅ **Automatizare Completa**: Declanseaza automat taste la primirea tipurilor
- ✅ **Queue Management**: Gestioneaza coada de filtre cu prioritati
- ✅ **UI Web**: Interfata web pentru monitorizare coada in timp real
- ✅ **Teste Integrate**: Mock server pentru testare fara API-uri reale
- ✅ **Trigger Manual**: Activare filtre manual prin combinatii de taste
- ✅ **Configurabil**: Settings complete prin fisiere .env
- ✅ **Logging Avansat**: Loguri detaliate pentru debugging

## Structura Proiect

```
AR_Filter_System_V1/
├── main.py                    # Aplicatie principala
├── queue_ui_server.py         # Server Flask pentru UI web
├── requirements.txt           # Dependente Python
├── .env                       # Configurare activa (generat)
├── .env.test                  # Configurare TEST mode
├── .env.production            # Configurare PRODUCTION mode
├── core/                      # Module core sistem
│   ├── ChaturbateListener.py # Listener Chaturbate API
│   ├── StripchatListener.py  # Listener Stripchat API
│   └── CamsodaListener.py    # Listener Camsoda API
├── templates/                 # Template-uri HTML
│   ├── queue.html            # UI vizualizare coada
│   └── menu.html             # UI overlay menu
├── tests/                     # Suite de teste
│   ├── mock_server.py        # Mock API server pentru teste
│   └── test_key_sender.py    # Test keyboard simulation
├── recordings/                # Director video recordings (optional)
├── output/                    # Director output logs si rapoarte
├── setup.bat                  # Script instalare automata
├── install.bat                # Script instalare dependente
├── run.bat                    # Script pornire/oprire program
└── switch_env.bat            # Script comutare TEST/PRODUCTION
```

## Cerinte Sistem

- **Python**: 3.8 sau mai nou
- **Sistem Operare**: Windows (cu suport pentru scripturi BAT)
- **RAM**: Minim 2GB recomandat
- **Retea**: Conexiune internet stabila pentru API calls

## Instalare Rapida

### Metoda 1: Instalare Automata (Recomandat)

```batch
# Ruleaza script-ul de instalare automata
setup.bat
```

### Metoda 2: Instalare Manuala

```batch
# 1. Instaleaza dependentele
pip install -r requirements.txt

# 2. Creaza directoare necesare
mkdir recordings output

# 3. Configureaza environment
copy .env.test .env
```

## Configurare

### TEST Mode (Recomandat pentru inceput)

```batch
# Activeaza TEST mode
switch_env.bat
# Selecteaza optiunea [1]

# Porneste mock server
python tests\mock_server.py

# In alt terminal, porneste aplicatia
python main.py
```

### PRODUCTION Mode

```batch
# Editeaza .env.production cu API keys reale
notepad .env.production

# Activeaza PRODUCTION mode
switch_env.bat
# Selecteaza optiunea [2]

# Porneste aplicatia
python main.py
```

## Utilizare

### Pornire Program

```batch
# Metoda 1: Folosind script-ul run.bat
run.bat
# Selecteaza optiunea [1] - Porneste Programul

# Metoda 2: Direct cu Python
python main.py
```

### Monitorizare Coada

Deschide in browser:
```
http://127.0.0.1:8080/queue
```

### Trigger Manual Filtre

- **Ctrl+1**: Activeaza filtrul #1
- **Ctrl+2**: Activeaza filtrul #2
- **Ctrl+3**: Activeaza filtrul #3
- ... (configurabil pana la 9)

### Oprire Program

```batch
# Folosind run.bat
run.bat
# Selecteaza optiunea [2] - Opreste Programul

# SAU apasa Ctrl+C in consola Python
```

## Arhitectura Sistem

```
┌─────────────────┐
│  Platform APIs  │  (Chaturbate, Stripchat, Camsoda)
└────────┬────────┘
         │ HTTP Polling
         ↓
┌─────────────────┐
│   Listeners     │  (Core modules)
│   - Chaturbate  │
│   - Stripchat   │
│   - Camsoda     │
└────────┬────────┘
         │ Event normalization
         ↓
┌─────────────────┐
│ FilterAutomation│  (main.py)
│   - Queue Mgmt  │
│   - Priority    │
│   - Processing  │
└────────┬────────┘
         │
         ├─────────────────┐
         ↓                 ↓
┌─────────────────┐  ┌──────────────┐
│   KeySender     │  │  Queue UI    │
│ (pynput-based)  │  │  (Flask SSE) │
└─────────────────┘  └──────────────┘
```

## Flow Date

1. **Listener** → Poll API endpoint la interval configurat
2. **Event Normalization** → Converteste raspunsuri in format uniform
3. **Queue Management** → Adauga tip in coada cu prioritate
4. **Worker Thread** → Proceseaza coada FIFO
5. **KeySender** → Simuleaza taste pentru activare filtru
6. **UI Update** → Broadcast update prin SSE la browser

## Tehnologii Utilizate

- **Python 3.8+**: Limbaj principal
- **Flask 3.1.2**: Web framework pentru UI
- **pynput 1.7.7**: Keyboard control si global listeners
- **python-dotenv 1.0.1**: Environment configuration management
- **requests**: HTTP client pentru API calls
- **threading**: Multi-threading pentru listeners si workers

## Debugging

### Verificare Status

```batch
run.bat
# Selecteaza optiunea [5] - Verifica Status
```

### Vizualizare Loguri

```batch
run.bat
# Selecteaza optiunea [3] - Vizualizeaza Loguri
```

### Test Mock Server

```batch
# Porneste mock server
python tests\mock_server.py

# In alt terminal, testeaza endpoint
curl http://127.0.0.1:5000/events/chaturbate
```

## Probleme Comune

### Programul nu detecteaza taste

- Asigura-te ca fereastra Python ramane deschisa
- Verifica ca pynput este instalat corect
- Ruleaza ca Administrator daca e necesar

### Eroare conexiune API

- Verifica conexiunea internet
- Confirma ca API keys sunt valide (PRODUCTION mode)
- Verifica ca mock_server.py ruleaza (TEST mode)

### Coada nu se actualizeaza in UI

- Verifica ca queue_ui_server.py ruleaza
- Reincarca pagina browser
- Verifica port 8080 nu e folosit de alta aplicatie

## Contributie

Pentru a contribui la dezvoltarea proiectului:

1. Fork repository-ul
2. Creaza branch nou pentru feature
3. Implementeaza si testeaza modificarile
4. Creaza Pull Request cu descriere detaliata

## Licenta

Proiect privat - Toate drepturile rezervate.

## Contact & Suport

Pentru probleme sau intrebari, deschide un Issue pe GitHub.

## Versiuni

- **V1.0**: Release initial cu suport multi-platform
- **V2.0**: (In dezvoltare) Branch curent cu imbunatatiri

## Link-uri Utile

- [Ghid Instalare Detaliat](INSTALARE.md)
- [Ghid Utilizare](UTILIZARE.md)
- [Documentatie Arhitectura](ARHITECTURA.md)
- [Documentatie API Integration](API_INTEGRATION.md)
- [Ghid Dezvoltatori](DEZVOLTARE.md)
