@echo off
REM ============================================================================
REM  INTEGRATED MANUAL PAPER TRADING PLATFORM
REM ============================================================================
REM  Runs on PORT 5004 to avoid conflicts with other modules
REM  - Main Dashboard (port 5000) - unified_trading_platform.py
REM  - Manual Trading (port 5004) - THIS SCRIPT
REM  Auto-opens browser to http://localhost:5004
REM ============================================================================

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

cls
echo.
echo ============================================================================
echo   INTEGRATED MANUAL PAPER TRADING PLATFORM
echo ============================================================================
echo   Port: 5004 (separate from main dashboard on 5000)
echo   Auto-opens: http://localhost:5004
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected: 
python --version
echo.

REM Check if port 5004 is already in use
echo [CHECK] Verifying port 5004 is available...
netstat -ano | findstr ":5004" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [WARNING] Port 5004 is already in use!
    echo.
    echo Options:
    echo   1. Close the application using port 5004
    echo   2. Or continue anyway (may fail)
    echo.
    choice /C 12 /N /M "Choose option (1 or 2): "
    if errorlevel 2 (
        echo.
        echo [INFO] Continuing anyway...
        echo.
    ) else (
        echo.
        echo [INFO] Please close the application and try again
        pause
        exit /b 1
    )
) else (
    echo [OK] Port 5004 is available
    echo.
)

REM Check if required files exist
echo [STEP 1/4] Checking required files...
echo.

if not exist "unified_trading_platform.py" (
    echo [ERROR] unified_trading_platform.py not found!
    echo.
    echo This file is required. Download from:
    echo https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/unified_trading_platform.py
    echo.
    pause
    exit /b 1
)
echo [OK] unified_trading_platform.py found

if not exist "manual_paper_trading.py" (
    echo [WARNING] manual_paper_trading.py not found! Downloading...
    echo.
    
    powershell -Command "try { Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/manual_paper_trading.py' -OutFile 'manual_paper_trading.py' -UseBasicParsing; Write-Host '[OK] Downloaded manual_paper_trading.py'; exit 0 } catch { Write-Host '[ERROR] Download failed'; exit 1 }" 2>nul
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Could not download manual_paper_trading.py
        echo.
        echo Please download manually from:
        echo https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/manual_paper_trading.py
        echo.
        echo Save it to: %CD%\manual_paper_trading.py
        echo.
        pause
        exit /b 1
    )
)
echo [OK] manual_paper_trading.py found

if not exist "templates\dashboard.html" (
    echo [WARNING] Dashboard templates not found!
    echo [INFO] Will use basic dashboard mode
    echo.
)

echo.

REM Check and install dependencies
echo [STEP 2/4] Checking dependencies...
echo.

python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [INSTALLING] Flask and Flask-CORS...
    pip install flask flask-cors --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Failed to install Flask
        pause
        exit /b 1
    )
)
echo [OK] Flask installed

python -c "import yfinance" >nul 2>&1
if errorlevel 1 (
    echo [INSTALLING] yfinance (for real-time stock prices)...
    pip install yfinance --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Failed to install yfinance
        pause
        exit /b 1
    )
)
echo [OK] yfinance installed

python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo [INSTALLING] pandas...
    pip install pandas --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Failed to install pandas
        pause
        exit /b 1
    )
)
echo [OK] pandas installed

python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo [INSTALLING] numpy...
    pip install numpy --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Failed to install numpy
        pause
        exit /b 1
    )
)
echo [OK] numpy installed

echo.
echo [OK] All dependencies installed
echo.

REM Validate files
echo [STEP 3/4] Validating Python files...
echo.

python -c "import unified_trading_platform" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] unified_trading_platform.py has syntax errors
    pause
    exit /b 1
)
echo [OK] unified_trading_platform.py validated

python -c "import manual_paper_trading" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] manual_paper_trading.py has syntax errors
    pause
    exit /b 1
)
echo [OK] manual_paper_trading.py validated

echo.

REM Start the platform
echo [STEP 4/4] Starting Integrated Manual Paper Trading...
echo.
echo ============================================================================
echo   MANUAL TRADING COMMANDS
echo ============================================================================
echo.
echo   buy('AAPL', 100)     Buy 100 shares of AAPL at current price
echo   sell('AAPL')         Sell all AAPL shares at current price
echo   status()             Show portfolio summary
echo   positions()          Show all open positions with P^&L
echo.
echo   Examples:
echo     ^>^>^> buy('NVDA', 50)
echo     ^>^>^> buy('TSLA', 25)
echo     ^>^>^> status()
echo     ^>^>^> sell('NVDA')
echo.
echo ============================================================================
echo   INTEGRATION INFO
echo ============================================================================
echo.
echo   This Manual Trading Platform runs on PORT 5004
echo   Other modules in your project can run simultaneously:
echo.
echo   - Main Dashboard: http://localhost:5000 (Unified Platform)
echo   - Manual Trading: http://localhost:5004 (This platform)
echo   - Live Coordinator: http://localhost:5001 (If running)
echo   - Intraday Monitor: http://localhost:5002 (If running)
echo.
echo ============================================================================
echo   Dashboard: http://localhost:5004
echo ============================================================================
echo.

REM Auto-open browser after 3 seconds
echo Opening browser in 3 seconds...
echo.
start "" timeout /t 3 /nobreak
start http://localhost:5004

REM Create a temporary Python launcher that sets port to 5004
echo Creating port configuration...
echo import sys > temp_manual_trading_launcher.py
echo sys.path.insert(0, '.') >> temp_manual_trading_launcher.py
echo. >> temp_manual_trading_launcher.py
echo # Override default port to 5004 >> temp_manual_trading_launcher.py
echo from manual_paper_trading import ManualTradingPlatform >> temp_manual_trading_launcher.py
echo import __main__ >> temp_manual_trading_launcher.py
echo. >> temp_manual_trading_launcher.py
echo if __name__ == "__main__": >> temp_manual_trading_launcher.py
echo     # Create platform with custom port >> temp_manual_trading_launcher.py
echo     print("\n" + "="*70) >> temp_manual_trading_launcher.py
echo     print("MANUAL PAPER TRADING PLATFORM - PORT 5004") >> temp_manual_trading_launcher.py
echo     print("="*70) >> temp_manual_trading_launcher.py
echo     print("\nCommands:") >> temp_manual_trading_launcher.py
echo     print("  buy('SYMBOL', quantity)  - Buy shares") >> temp_manual_trading_launcher.py
echo     print("  sell('SYMBOL')           - Sell all shares") >> temp_manual_trading_launcher.py
echo     print("  status()                 - Show portfolio") >> temp_manual_trading_launcher.py
echo     print("  positions()              - Show open positions") >> temp_manual_trading_launcher.py
echo     print("\nDashboard: http://localhost:5004") >> temp_manual_trading_launcher.py
echo     print("="*70 + "\n") >> temp_manual_trading_launcher.py
echo. >> temp_manual_trading_launcher.py
echo     platform = ManualTradingPlatform(initial_capital=100000) >> temp_manual_trading_launcher.py
echo     platform.dashboard_port = 5004  # Set custom port >> temp_manual_trading_launcher.py
echo. >> temp_manual_trading_launcher.py
echo     # Make functions available globally >> temp_manual_trading_launcher.py
echo     __main__.buy = platform.buy >> temp_manual_trading_launcher.py
echo     __main__.sell = platform.sell >> temp_manual_trading_launcher.py
echo     __main__.status = platform.status >> temp_manual_trading_launcher.py
echo     __main__.positions = platform.positions >> temp_manual_trading_launcher.py
echo. >> temp_manual_trading_launcher.py
echo     # Start (manual mode) >> temp_manual_trading_launcher.py
echo     platform.run() >> temp_manual_trading_launcher.py

echo.
echo [STARTING] Manual Paper Trading on PORT 5004...
echo.

REM Start Python with the custom launcher
python temp_manual_trading_launcher.py

REM Cleanup
if exist temp_manual_trading_launcher.py del temp_manual_trading_launcher.py

REM Handle exit
echo.
echo.
echo ============================================================================
echo   Manual Trading Platform (PORT 5004) stopped
echo ============================================================================
echo.
pause
