@echo off
REM ====================================================================
REM  DASHBOARD STARTER WITH BROWSER AUTO-OPEN
REM  Starts dashboard and automatically opens browser
REM ====================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║      STARTING LIVE TRADING DASHBOARD WITH AUTO-OPEN           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.9+
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Install dependencies quietly
echo Installing dependencies...
python -m pip install --quiet flask flask-cors pandas numpy >nul 2>&1
echo ✅ Dependencies ready
echo.

echo Starting dashboard server...
echo Please wait 3 seconds for server to start...
echo.

REM Start the dashboard in the background
start /B python live_trading_dashboard.py

REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Open browser
echo ✅ Opening browser to http://localhost:5000
start http://localhost:5000

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    DASHBOARD RUNNING                           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Dashboard URL: http://localhost:5000
echo.
echo ⚠  DO NOT CLOSE THIS WINDOW!
echo    The dashboard server is running in the background
echo.
echo To stop the dashboard:
echo    1. Close this window, OR
echo    2. Press CTRL+C
echo.
echo ════════════════════════════════════════════════════════════════
echo.

REM Keep the window open
pause >nul
