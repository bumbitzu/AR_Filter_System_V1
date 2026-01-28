@echo off
REM ============================================================
REM AR Filter System - Setup Script
REM Automated installation and verification
REM ============================================================

echo.
echo ============================================================
echo   AR FILTER SYSTEM - MULTI-PLATFORM SETUP
echo ============================================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo OK: Python is installed
echo.

REM Check pip
echo [2/5] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Installing pip...
    python -m ensurepip --upgrade
)
echo OK: pip is available
echo.

REM Install dependencies
echo [3/5] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK: All dependencies installed
echo.

REM Verify installations
echo [4/5] Verifying installations...
python -c "import cv2; import mediapipe; import numpy; import requests; import flask; print('OK: All modules imported successfully')"
if %errorlevel% neq 0 (
    echo ERROR: Some modules failed to import
    pause
    exit /b 1
)
echo.

REM Create necessary directories
echo [5/5] Creating project structure...
if not exist "recordings" mkdir recordings
if not exist "output" mkdir output
echo OK: Directories created
echo.

REM Success message
echo ============================================================
echo   SETUP COMPLETE!
echo ============================================================
echo.
echo Next steps:
echo   1. Start mock server:    python tests\mock_server.py
echo   2. Test system:          python tests\test_multi_platform.py
echo   3. Run application:      python main.py
echo.
echo Documentation:
echo   - Quick Start:           README_QUICK_START.md
echo   - Full Guide:            MULTI_PLATFORM_GUIDE.md
echo   - Production Setup:      PRODUCTION_API_SETUP.md
echo.
echo ============================================================
echo.
pause
