@echo off
REM ============================================================================
REM  INTEGRATED MANUAL TRADING - PORT 5004
REM ============================================================================
REM  Runs alongside other project modules without port conflicts
REM  Auto-opens browser to http://localhost:5004
REM ============================================================================

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

cls
echo.
echo ============================================================================
echo   INTEGRATED MANUAL PAPER TRADING
echo ============================================================================
echo   Port: 5004 ^| Capital: $100,000 ^| Auto-opens browser
echo ============================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python: 
python --version
echo.

REM Check port availability
echo [CHECK] Port 5004 availability...
netstat -ano | findstr ":5004" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 5004 in use! Continue anyway? (Y/N^)
    choice /C YN /N /M ""
    if errorlevel 2 exit /b 1
)
echo.

REM Check required files
echo [STEP 1/3] Checking files...
if not exist "unified_trading_platform.py" (
    echo [ERROR] unified_trading_platform.py missing!
    echo Download: https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/unified_trading_platform.py
    pause
    exit /b 1
)
if not exist "manual_paper_trading.py" (
    echo [DOWNLOAD] manual_paper_trading.py...
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/manual_paper_trading.py' -OutFile 'manual_paper_trading.py' -UseBasicParsing" 2>nul
    if errorlevel 1 (
        echo [ERROR] Download failed
        pause
        exit /b 1
    )
)
echo [OK] Files present
echo.

REM Install dependencies
echo [STEP 2/3] Dependencies...
python -c "import flask, yfinance, pandas, numpy" >nul 2>&1
if errorlevel 1 (
    echo [INSTALL] Missing packages...
    pip install flask flask-cors yfinance pandas numpy --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Installation failed
        pause
        exit /b 1
    )
)
echo [OK] All dependencies ready
echo.

REM Display info
echo [STEP 3/3] Starting platform...
echo.
echo ============================================================================
echo   TRADING COMMANDS
echo ============================================================================
echo.
echo   buy('AAPL', 100)     Buy 100 shares
echo   sell('AAPL')         Sell all shares
echo   status()             Portfolio summary
echo   positions()          Open positions
echo.
echo ============================================================================
echo   INTEGRATION - MULTI-MODULE SETUP
echo ============================================================================
echo.
echo   This platform runs on PORT 5004 to avoid conflicts:
echo.
echo   Port 5000: Main Dashboard (unified_trading_platform.py)
echo   Port 5004: Manual Trading (THIS) - http://localhost:5004
echo   Port 5001: Live Coordinator (if running)
echo   Port 5002: Intraday Monitor (if running)
echo.
echo   All modules can run simultaneously!
echo.
echo ============================================================================
echo   Dashboard: http://localhost:5004
echo ============================================================================
echo.

REM Auto-open browser
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:5004

echo.
echo [STARTING] Manual Trading Platform on PORT 5004...
echo.

REM Start with port argument
python manual_paper_trading.py --port 5004

REM Handle exit
echo.
echo.
echo ============================================================================
echo   Platform stopped
echo ============================================================================
echo.
pause
