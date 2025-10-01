@echo off
REM Setup script for cloud-connected Stock Predictor Pro

echo ==========================================
echo Stock Predictor Pro - Cloud Setup
echo ==========================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo Found Python:
python --version
echo.

REM Check/Install requests library
echo Checking for requests library...
python -c "import requests" 2>nul
if %errorlevel% neq 0 (
    echo Installing requests library for API connection...
    pip install requests
    if %errorlevel% neq 0 (
        echo.
        echo WARNING: Could not install requests
        echo The app will work but only in local simulation mode
        echo.
    )
) else (
    echo [OK] Requests library is installed
)

echo.
echo ==========================================
echo Configuration Created
echo ==========================================
echo.
echo Cloud API Endpoint:
echo https://8000-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev
echo.
echo The config.json file has been created with your
echo cloud API endpoint. The application will now
echo connect to your cloud prediction center!
echo.
echo ==========================================
echo.

REM Run the configured version
echo Starting Stock Predictor Pro (Cloud Connected)...
echo.
python stock_predictor_configured.py

if %errorlevel% neq 0 (
    echo.
    echo If the app didn't start, try:
    echo 1. python stock_predictor_configured.py
    echo 2. Or use the lite version instead
    echo.
)

pause