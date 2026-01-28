@echo off
REM ============================================================
REM AR Filter System - Environment Switcher
REM Schimbă rapid între TEST și PRODUCTION environments
REM ============================================================

:MENU
cls
echo.
echo ============================================================
echo   AR FILTER SYSTEM - ENVIRONMENT SWITCHER
echo ============================================================
echo.
echo   Selectează environment-ul:
echo.
echo   [1] TEST MODE (Mock Server)
echo   [2] PRODUCTION MODE (API-uri Reale)
echo   [3] Verifică environment activ
echo   [4] Editează .env
echo   [Q] Ieșire
echo.
echo ============================================================
echo.

set /p choice="Alege opțiunea (1/2/3/4/Q): "

if /i "%choice%"=="1" goto TEST_MODE
if /i "%choice%"=="2" goto PRODUCTION_MODE
if /i "%choice%"=="3" goto CHECK_ENV
if /i "%choice%"=="4" goto EDIT_ENV
if /i "%choice%"=="Q" goto END
goto MENU

:TEST_MODE
echo.
echo [Activare TEST MODE...]
copy /Y .env.test .env >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Environment setat pe TEST
    echo.
    echo Platforme configurate:
    echo   • Chaturbate: http://127.0.0.1:5000/events/chaturbate
    echo   • Stripchat:  http://127.0.0.1:5000/events/stripchat
    echo   • Camsoda:    http://127.0.0.1:5000/events/camsoda
    echo.
    echo 💡 Nu uita să pornești mock server-ul:
    echo    python tests\mock_server.py
) else (
    echo ❌ Eroare: Nu am putut copia .env.test
)
echo.
pause
goto MENU

:PRODUCTION_MODE
echo.
echo ⚠️  ATENȚIE: Aceasta va activa PRODUCTION MODE cu API-uri REALE!
echo.
set /p confirm="Ești sigur? (y/n): "
if /i not "%confirm%"=="y" goto MENU

echo.
echo [Activare PRODUCTION MODE...]

REM Verifică dacă .env.production există și conține keys reale
findstr /C:"your_username_here" .env.production >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ⚠️  WARNING: .env.production conține încă placeholders!
    echo.
    echo Trebuie să completezi API keys reale în .env.production
    echo Vrei să editezi acum .env.production? (y/n^)
    set /p edit_choice=": "
    if /i "%edit_choice%"=="y" (
        notepad .env.production
        echo.
        echo După salvare, rulează din nou acest script.
        pause
        goto MENU
    )
    pause
    goto MENU
)

copy /Y .env.production .env >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Environment setat pe PRODUCTION
    echo.
    echo ⚠️  Folosești API-uri REALE!
    echo Verifică că toate API keys sunt valide.
) else (
    echo ❌ Eroare: Nu am putut copia .env.production
)
echo.
pause
goto MENU

:CHECK_ENV
echo.
echo ============================================================
echo   ENVIRONMENT ACTIV
echo ============================================================
echo.

if not exist .env (
    echo ❌ Fișierul .env nu există!
    echo.
    echo Rulează opțiunea [1] sau [2] pentru a crea .env
    goto CHECK_END
)

findstr /C:"ENVIRONMENT=" .env >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims==" %%a in ('findstr /C:"ENVIRONMENT=" .env') do (
        echo Environment Type: %%a
    )
) else (
    echo Environment Type: Unknown
)

echo.
echo Conținut .env:
echo -----------------------------------------------------------
type .env
echo -----------------------------------------------------------

:CHECK_END
echo.
pause
goto MENU

:EDIT_ENV
echo.
echo [Deschidere .env în Notepad...]
if not exist .env (
    echo ❌ Fișierul .env nu există!
    echo Creez .env din .env.test...
    copy /Y .env.test .env >nul 2>&1
)
notepad .env
goto MENU

:END
echo.
echo Bye! 👋
echo.
timeout /t 2 >nul
exit /b 0
