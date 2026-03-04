@echo off
REM ============================================================================
REM Mobile Remote Access Launcher
REM ============================================================================
REM
REM Launches the Unified Trading Dashboard with mobile remote access enabled.
REM Provides secure HTTPS tunnel via ngrok for accessing from mobile devices.
REM
REM Features:
REM - Automatic ngrok tunnel setup
REM - QR code generation for easy mobile connection
REM - Secure authentication with username/password
REM - Mobile-responsive UI
REM
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo         UNIFIED TRADING DASHBOARD - MOBILE REMOTE ACCESS
echo ============================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo [WARNING] Virtual environment not found. Creating...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if ngrok is installed
where ngrok >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================================
    echo                            NGROK NOT FOUND
    echo ============================================================================
    echo.
    echo Ngrok is required for mobile remote access but was not found.
    echo.
    echo Installation Instructions:
    echo.
    echo 1. Download ngrok from: https://ngrok.com/download
    echo 2. Extract ngrok.exe to: C:\Windows\System32\
    echo    ^(or any folder in your PATH^)
    echo 3. Sign up for free account: https://dashboard.ngrok.com/signup
    echo 4. Get your authtoken and run: ngrok authtoken YOUR_AUTH_TOKEN
    echo 5. Re-run this script
    echo.
    echo ============================================================================
    echo.
    pause
    exit /b 1
)

REM Install required packages
echo [INFO] Installing required packages...
pip install --quiet qrcode[pil] requests >nul 2>&1

REM Check authentication mode
set AUTH_MODE=enabled
set USERNAME=trader
set PASSWORD=

echo.
echo ============================================================================
echo                      MOBILE ACCESS CONFIGURATION
echo ============================================================================
echo.
echo Authentication is ENABLED by default for security.
echo.
set /p "USE_AUTH=Enable authentication? (Y/n): " || set USE_AUTH=Y

if /i "%USE_AUTH%"=="n" (
    set AUTH_MODE=disabled
    echo [INFO] Authentication DISABLED
) else (
    set AUTH_MODE=enabled
    echo.
    set /p "USERNAME=Enter username (default: trader): " || set USERNAME=trader
    if "!USERNAME!"=="" set USERNAME=trader
    
    echo.
    set /p "PASSWORD=Enter password (leave blank for auto-generated): "
    
    echo [INFO] Authentication ENABLED
    echo [INFO] Username: !USERNAME!
)

echo.
echo ============================================================================
echo                         STARTING DASHBOARD
echo ============================================================================
echo.

REM Create startup script
echo import sys > temp_mobile_launcher.py
echo import os >> temp_mobile_launcher.py
echo from pathlib import Path >> temp_mobile_launcher.py
echo. >> temp_mobile_launcher.py
echo sys.path.insert^(0, str^(Path^(__file__^).parent / 'core'^)^) >> temp_mobile_launcher.py
echo. >> temp_mobile_launcher.py
echo from mobile_access import MobileAccessManager >> temp_mobile_launcher.py
echo import threading >> temp_mobile_launcher.py
echo import time >> temp_mobile_launcher.py
echo. >> temp_mobile_launcher.py
echo # Start mobile access manager in background >> temp_mobile_launcher.py
echo manager = MobileAccessManager^( >> temp_mobile_launcher.py
echo     username='%USERNAME%', >> temp_mobile_launcher.py
if not "%PASSWORD%"=="" (
    echo     password='%PASSWORD%', >> temp_mobile_launcher.py
)
echo     port=8050 >> temp_mobile_launcher.py
echo ^) >> temp_mobile_launcher.py
echo. >> temp_mobile_launcher.py
echo def start_tunnel^(^): >> temp_mobile_launcher.py
echo     time.sleep^(5^)  # Wait for dashboard to start >> temp_mobile_launcher.py
echo     manager.start^(^) >> temp_mobile_launcher.py
echo. >> temp_mobile_launcher.py
echo tunnel_thread = threading.Thread^(target=start_tunnel, daemon=True^) >> temp_mobile_launcher.py
echo tunnel_thread.start^(^) >> temp_mobile_launcher.py
echo. >> temp_mobile_launcher.py
echo # Import and run dashboard >> temp_mobile_launcher.py
echo os.chdir^('core'^) >> temp_mobile_launcher.py
echo with open^('unified_trading_dashboard.py', 'r', encoding='utf-8'^) as f: >> temp_mobile_launcher.py
echo     exec^(f.read^(^)^) >> temp_mobile_launcher.py

echo.
echo [INFO] Launching dashboard with mobile access...
echo [INFO] Dashboard will start on: http://localhost:8050
echo [INFO] Mobile access URL will be displayed shortly...
echo.
echo ============================================================================
echo.

REM Run the dashboard
python temp_mobile_launcher.py

REM Cleanup
if exist temp_mobile_launcher.py del temp_mobile_launcher.py

echo.
echo [INFO] Dashboard stopped.
pause
