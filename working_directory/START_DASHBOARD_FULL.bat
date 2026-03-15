@echo off
REM ====================================================================
REM  DASHBOARD STARTER WITH DEPENDENCY CHECK - Windows Batch File
REM  This version installs dependencies first, then starts dashboard
REM ====================================================================

title Live Trading Dashboard Starter

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║         LIVE TRADING DASHBOARD - STARTUP WIZARD               ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Navigate to the script's directory
cd /d "%~dp0"

echo [STEP 1/5] Checking location...
echo Current directory: %CD%
echo.

REM Check Python
echo [STEP 2/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Python not found!
    echo.
    echo Please install Python 3.9 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% detected
echo.

REM Check files
echo [STEP 3/5] Checking dashboard files...
set FILES_OK=1

if not exist "live_trading_dashboard.py" (
    echo ❌ Missing: live_trading_dashboard.py
    set FILES_OK=0
)

if not exist "templates\dashboard.html" (
    echo ❌ Missing: templates\dashboard.html
    set FILES_OK=0
)

if not exist "static\css\dashboard.css" (
    echo ❌ Missing: static\css\dashboard.css
    set FILES_OK=0
)

if not exist "static\js\dashboard.js" (
    echo ❌ Missing: static\js\dashboard.js
    set FILES_OK=0
)

if %FILES_OK%==0 (
    echo.
    echo ❌ ERROR: Required files are missing!
    echo.
    echo Please run INSTALL_DASHBOARD_FIXED.bat first to install all files.
    echo Or copy the following from dashboard_deployment_package:
    echo   - live_trading_dashboard.py
    echo   - live_trading_with_dashboard.py
    echo   - templates/ folder
    echo   - static/ folder
    echo.
    pause
    exit /b 1
)

echo ✅ All required files present
echo.

REM Install dependencies
echo [STEP 4/5] Installing/updating dependencies...
echo (This may take 30-60 seconds on first run)
echo.

python -m pip install --quiet --upgrade pip 2>nul
if %errorlevel% neq 0 (
    echo ⚠ Warning: Could not upgrade pip, continuing anyway...
)

echo Installing Flask...
python -m pip install --quiet flask 2>nul || python -m pip install flask

echo Installing Flask-CORS...
python -m pip install --quiet flask-cors 2>nul || python -m pip install flask-cors

echo Installing Pandas...
python -m pip install --quiet pandas 2>nul || python -m pip install pandas

echo Installing NumPy...
python -m pip install --quiet numpy 2>nul || python -m pip install numpy

echo.
echo ✅ Dependencies installed
echo.

REM Final check
echo [STEP 5/5] Starting dashboard server...
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  DASHBOARD SERVER STARTING                     ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Access dashboard at: http://localhost:5000
echo.
echo 📊 The dashboard will show:
echo    • Portfolio summary (Total Value, P^&L, Win Rate)
echo    • Live positions and trades
echo    • Interactive charts (Cumulative Returns, Daily P^&L)
echo    • Real-time alerts and market sentiment
echo.
echo 🔄 Auto-refresh: Every 5 seconds
echo.
echo ⏹  Press CTRL+C to stop the server
echo.
echo ════════════════════════════════════════════════════════════════
echo.

REM Start the dashboard
python live_trading_dashboard.py

REM Server stopped
echo.
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              DASHBOARD SERVER STOPPED                          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo To restart, double-click this file again.
echo.
pause
