@echo off
REM ============================================================
REM AR Filter System - Script de Instalare
REM Instalare si verificare automata
REM ============================================================

echo.
echo ============================================================
echo   AR FILTER SYSTEM - INSTALARE MULTI-PLATFORMA
echo ============================================================
echo.

REM Verificare instalare Python
echo [1/5] Verific instalarea Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo EROARE: Python nu este instalat sau nu este in PATH
    echo Te rog instaleaza Python 3.8+ de pe https://www.python.org/
    pause
    exit /b 1
)
python --version
echo OK: Python este instalat
echo.

REM Verificare pip
echo [2/5] Verific pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo EROARE: pip nu este disponibil
    echo Instalez pip...
    python -m ensurepip --upgrade
)
echo OK: pip este disponibil
echo.

REM Instalare dependinte
echo [3/5] Instalez dependintele...
echo Aceasta poate dura cateva minute...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo EROARE: Esec la instalarea dependintelor
    pause
    exit /b 1
)
echo OK: Toate dependintele au fost instalate
echo.

REM Verificare instalari
echo [4/5] Verific instalarile...
python -c "import cv2; import mediapipe; import numpy; import requests; import flask; print('OK: Toate modulele importate cu succes')"
if %errorlevel% neq 0 (
    echo EROARE: Unele module nu au putut fi importate
    pause
    exit /b 1
)
echo.

REM Creare directoare necesare
echo [5/5] Creez structura proiectului...
if not exist "recordings" mkdir recordings
if not exist "output" mkdir output
echo OK: Directoare create
echo.

REM Mesaj de succes
echo ============================================================
echo   INSTALARE COMPLETA!
echo ============================================================
echo.
echo Pasii urmatori:
echo   1. Porneste mock server pentru testare:    python tests\mock_server.py
echo   2. Ruleaza aplicatia:                      python main.py sau folosete run.bat
echo.
echo Documentatie:
echo   - README.md                  - Prezentare generala
echo   - INSTALARE.md               - Ghid de instalare
echo   - DEZVOLTARE.md              - Ghid de dezvoltare
echo   - UTILIZARE.md               - Ghid de utilizare
echo   - ARHITECTURA.md             - Arhitectura sistemului
echo   - API_INTEGRATION.md         - Integrare API-uri
echo.
echo ============================================================
echo.
pause
