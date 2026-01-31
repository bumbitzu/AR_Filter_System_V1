@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM AR Filter System - Lansator Interactiv
REM ============================================================

set "PID_FILE=%TEMP%\ar_filter_system.pid"
set "LOG_FILE=ar_filter_system.log"

:MAIN_MENU
cls
echo.
echo ============================================================
echo   AR FILTER SYSTEM - PANOU DE CONTROL
echo ============================================================
echo.
E
set "IS_RUNNING=false"
if exist "%PID_FILE%" (
    set /p STORED_PID=<"%PID_FILE%"
    tasklist /FI "PID eq !STORED_PID!" 2>NUL | find /I /N "python.exe">NUL
    if !ERRORLEVEL! EQU 0 (
        set "IS_RUNNING=true"
    ) else (
        REM PID file exists but process is not running - clean up
        del "%PID_FILE%" 2>NUL
    )
)

if "!IS_RUNNING!"=="true" (
    echo   Status: [92mRULEAZA[0m  ^(PID: !STORED_PID!^)
    echo.
    echo   [1] Opreste Programul
    echo   [2] Reporneste Programul
    echo   [3] Vezi Loguri Live
    echo   [4] Deschide Queue UI ^(Browser^)
    echo   [5] Verifica Status
    echo   [Q] Iesire
) else (
    echo   Status: [91mOPRIT[0m
    echo.
    echo   [1] Porneste Programul
    echo   [2] Porneste cu Queue UI Server
    echo   [3] Vezi Ultimele Loguri
    echo   [4] Verifica Mediul
    echo   [Q] Iesire
)

echo.
echo ============================================================
echo.

set /p choice="Selecteaza optiunea: "

if "!IS_RUNNING!"=="true" (
    if /i "!choice!"=="1" goto STOP_PROGRAM
    if /i "!choice!"=="2" goto RESTART_PROGRAM
    if /i "!choice!"=="3" goto VIEW_LOGS
    if /i "!choice!"=="4" goto OPEN_UI
    if /i "!choice!"=="5" goto CHECK_STATUS
    if /i "!choice!"=="Q" goto END
) else (
    if /i "!choice!"=="1" goto START_PROGRAM
    if /i "!choice!"=="2" goto START_WITH_UI
    if /i "!choice!"=="3" goto VIEW_LOGS
    if /i "!choice!"=="4" goto CHECK_ENV
    if /i "!choice!"=="Q" goto END
)

goto MAIN_MENU

:START_PROGRAM
echo.
echo [Pornesc AR Filter System in fereastra noua...]
echo.
echo [93mNota: Pastreaza fereastra Python deschisa pentru ca tastele sa functioneze![0m
echo.
start "AR Filter System" python main.py
timeout /t 2 >NUL

REM Obtine PID-ul procesului pornit
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /NH ^| findstr /R /C:"python.exe"') do (
    set "NEW_PID=%%a"
    goto FOUND_PID
)

:FOUND_PID
echo !NEW_PID! > "%PID_FILE%"
echo [92mProgram pornit cu succes! PID: !NEW_PID![0m
echo [93mApasa tastele 1-9 in fereastra Python pentru a activa filtrele![0m
echo.
pause
goto MAIN_MENU

:START_WITH_UI
echo.
echo [Pornesc AR Filter System cu Queue UI in fereastra noua...]
echo.
echo [93mNota: Pastreaza fereastra Python deschisa pentru ca tastele sa functioneze![0m
echo.
start "AR Filter System" python main.py

timeout /t 3 >NUL

REM Obtine PID
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /NH ^| findstr /R /C:"python.exe"') do (
    set "NEW_PID=%%a"
    goto FOUND_PID2
)

:FOUND_PID2
echo !NEW_PID! > "%PID_FILE%"
echo [92mProgram pornit![0m
echo.
echo Deschid Queue UI in browser...
timeout /t 2 >NUL
start http://127.0.0.1:8080
echo.
pause
goto MAIN_MENU

:STOP_PROGRAM
echo.
echo [Opresc AR Filter System...]
if exist "%PID_FILE%" (
    set /p STORED_PID=<"%PID_FILE%"
    taskkill /PID !STORED_PID! /F >NUL 2>&1
    del "%PID_FILE%" 2>NUL
    echo [92mProgram oprit cu succes![0m
) else (
    echo [91mFisier PID negasit![0m
)
echo.
pause
goto MAIN_MENU

:RESTART_PROGRAM
echo.
echo [Repornesc AR Filter System...]
if exist "%PID_FILE%" (
    set /p STORED_PID=<"%PID_FILE%"
    taskkill /PID !STORED_PID! /F >NUL 2>&1
    del "%PID_FILE%" 2>NUL
)
timeout /t 1 >NUL

start "AR Filter System" python main.py
timeout /t 2 >NUL

for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /NH ^| findstr /R /C:"python.exe"') do (
    set "NEW_PID=%%a"
    goto FOUND_PID3
)

:FOUND_PID3
echo !NEW_PID! > "%PID_FILE%"
echo [92mProgram repornit! PID nou: !NEW_PID![0m
echo.
pause
goto MAIN_MENU

:VIEW_LOGS
echo.
echo ============================================================
echo   LOGURI
echo ============================================================
echo.
if exist "%LOG_FILE%" (
    type "%LOG_FILE%"
) else (
    echo Fisier de loguri negasit.
)
echo.
echo ============================================================
pause
goto MAIN_MENU

:OPEN_UI
echo.
echo [Deschid Queue UI in browser...]
start http://127.0.0.1:8080
timeout /t 1 >NUL
goto MAIN_MENU

:CHECK_STATUS
echo.
echo ============================================================
echo   STATUS PROGRAM
echo ============================================================
echo.
if exist "%PID_FILE%" (
    set /p STORED_PID=<"%PID_FILE%"
    tasklist /FI "PID eq !STORED_PID!" 2>NUL | find /I /N "python.exe">NUL
    if !ERRORLEVEL! EQU 0 (
        echo Status: [92mRULEAZA[0m
        echo PID: !STORED_PID!
        echo.
        echo Detalii Proces:
        tasklist /FI "PID eq !STORED_PID!" /V
    ) else (
        echo Status: [91mOPRIT[0m
        echo ^(Fisierul PID exista dar procesul nu ruleaza^)
    )
) else (
    echo Status: [91mOPRIT[0m
)
echo.
echo ============================================================
pause
goto MAIN_MENU

:CHECK_ENV
echo.
echo ============================================================
echo   VERIFICARE MEDIU
echo ============================================================
echo.
if exist ".env" (
    echo [92mFisier configurare gasit: .env[0m
    echo.
    findstr /C:"ENVIRONMENT=" .env
    echo.
) else (
    echo [91mFisier .env negasit![0m
    echo.
    echo Ruleaza switch_env.bat pentru a configura mediul
)
echo.
echo ============================================================
pause
goto MAIN_MENU

:END
echo.
if "!IS_RUNNING!"=="true" (
    echo [93mAtentie: Programul inca ruleaza![0m
    echo.
    set /p confirm="Vrei sa-l opresti inainte de iesire? (y/n): "
    if /i "!confirm!"=="y" (
        if exist "%PID_FILE%" (
            set /p STORED_PID=<"%PID_FILE%"
            taskkill /PID !STORED_PID! /F >NUL 2>&1
            del "%PID_FILE%" 2>NUL
            echo [92mProgram oprit.[0m
        )
    )
)
echo.
echo La revedere! 👋
timeout /t 2 >NUL
exit /b 0
