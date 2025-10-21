@echo off
REM ============================================================
REM ML STOCK PREDICTOR - WINDOWS 11 STARTUP SCRIPT
REM ============================================================
REM This script starts the ML Stock Predictor server
REM ============================================================

title ML Stock Predictor - Starting...
color 0A
cls

echo ============================================================
echo    ML STOCK PREDICTOR - WINDOWS 11 EDITION
echo ============================================================
echo.
echo Starting server setup...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check for virtual environment
if exist "venv\" (
    echo [OK] Virtual environment found
    call venv\Scripts\activate
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo [OK] Virtual environment created and activated
)

echo.
echo Installing/updating required packages...
echo.

REM Install required packages
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

echo.
echo [OK] Packages installed
echo.

REM Kill any existing server on port 8000
echo Checking for existing servers on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping existing server (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

REM Clear the screen and show final message
cls
color 0A
echo ============================================================
echo    ML STOCK PREDICTOR SERVER
echo ============================================================
echo.
echo Server Configuration:
echo   - Port: 8000
echo   - URL: http://localhost:8000
echo   - Yahoo Finance: Primary data source
echo   - Alpha Vantage: Backup (API Key configured)
echo   - Australian stocks: Auto-detection enabled
echo.
echo ============================================================
echo.
echo Starting server...
echo.
echo Once started, access the interface at:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the server
python server.py

REM If server exits, show message
echo.
echo ============================================================
echo Server stopped.
echo ============================================================
echo.
pause