@echo off
echo ====================================
echo   AR Filter System - Instalare
echo ====================================
echo.

REM Verificare daca Python este instalat
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo EROARE: Python nu este instalat sau nu este in PATH
    echo Te rog instaleaza Python 3.8+ de pe https://www.python.org/
    pause
    exit /b 1
)

echo Python gasit!
python --version
echo.

REM Verificare daca pip este disponibil
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo EROARE: pip nu este disponibil
    echo Te rog reinstaleaza Python cu pip inclus
    pause
    exit /b 1
)

echo Pip gasit!
echo.

REM Actualizare pip
echo Actualizez pip...
python -m pip install --upgrade pip
echo.

REM Instalare requirements
echo Instalez pachetele necesare din requirements.txt...
python -m pip install -r requirements.txt
echo.

if %errorlevel% equ 0 (
    echo ====================================
    echo   Instalare finalizata cu succes!
    echo ====================================
    echo.
    echo Poti acum rula sistemul:
    echo   - Sistem principal: python main.py
    echo   - Queue UI: python queue_ui_server.py
    echo.
) else (
    echo ====================================
    echo   Instalare esuata!
    echo ====================================
    echo Te rog verifica mesajele de eroare de mai sus
    echo.
)

pause
