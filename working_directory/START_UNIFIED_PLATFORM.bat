@echo off
REM ====================================================================
REM  UNIFIED TRADING PLATFORM STARTER
REM  All-in-One: Paper Trading + Dashboard + Monitoring
REM ====================================================================

title Unified Trading Platform - Paper Trading Mode

cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║       UNIFIED TRADING PLATFORM - ALL-IN-ONE MODULE             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Check Python
echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Install Python 3.9+ from python.org
    pause
    exit /b 1
)
echo ✅ Python detected
echo.

REM Install dependencies
echo [2/3] Installing dependencies...
python -m pip install --quiet flask flask-cors >nul 2>&1
echo ✅ Dependencies ready
echo.

REM Start platform
echo [3/3] Starting Unified Trading Platform...
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              PAPER TRADING MODE - ALL-IN-ONE                   ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 💰 Initial Capital: $100,000 (simulated)
echo 📊 Market: US Stock Market
echo 🌐 Dashboard: http://localhost:5000
echo.
echo ⚠️  PAPER TRADING MODE - NO REAL MONEY
echo    Everything runs in ONE module!
echo.
echo Features Included:
echo   ✅ Paper Trading Engine (simulated trades)
echo   ✅ Real-time Web Dashboard
echo   ✅ Position Tracking
echo   ✅ Trade History
echo   ✅ Performance Metrics
echo   ✅ Risk Management
echo   ✅ Alert System
echo   ✅ Auto-scanning every 5 minutes
echo.
echo Press CTRL+C to stop
echo.
echo ════════════════════════════════════════════════════════════════
echo.

python unified_trading_platform.py --paper-trading

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error starting platform
    pause
)

pause
