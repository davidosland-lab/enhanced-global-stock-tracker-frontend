@echo off
REM ============================================================================
REM  MANUAL TRADING - PHASE 3 ENHANCED (PORT 5004)
REM ============================================================================
REM  Integrates Phase 3 swing trading + intraday monitoring enhancements
REM  Auto-opens browser to http://localhost:5004
REM ============================================================================

setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

cls
echo.
echo ============================================================================
echo   MANUAL PAPER TRADING - PHASE 3 ENHANCED
echo ============================================================================
echo   Port: 5004 ^| Capital: $100,000 ^| Phase 3 Features Enabled
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
    echo [WARNING] Port 5004 in use!
    choice /C YN /N /M "Continue anyway? (Y/N): "
    if errorlevel 2 exit /b 1
)
echo [OK] Port 5004 available
echo.

REM Check required files
echo [STEP 1/3] Checking files...
if not exist "unified_trading_platform.py" (
    echo [ERROR] unified_trading_platform.py missing!
    echo.
    echo Download from:
    echo https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/unified_trading_platform.py
    echo.
    pause
    exit /b 1
)
echo [OK] unified_trading_platform.py found

if not exist "manual_trading_phase3.py" (
    echo [DOWNLOAD] manual_trading_phase3.py...
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/market-timing-critical-fix/working_directory/manual_trading_phase3.py' -OutFile 'manual_trading_phase3.py' -UseBasicParsing" 2>nul
    if errorlevel 1 (
        echo [ERROR] Download failed. Download manually from GitHub.
        pause
        exit /b 1
    )
)
echo [OK] manual_trading_phase3.py found

REM Check for Phase 3 config (optional)
if exist "swing_intraday_integration_v1.0\config.json" (
    echo [OK] Phase 3 config found
) else (
    echo [INFO] Using default Phase 3 configuration
)
echo.

REM Install dependencies
echo [STEP 2/3] Dependencies...
python -c "import flask, yfinance, pandas, numpy" >nul 2>&1
if errorlevel 1 (
    echo [INSTALL] Installing packages...
    pip install flask flask-cors yfinance pandas numpy --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [ERROR] Installation failed
        pause
        exit /b 1
    )
)
echo [OK] All dependencies ready
echo.

REM Display Phase 3 features
echo [STEP 3/3] Starting Phase 3 Enhanced Platform...
echo.
echo ============================================================================
echo   PHASE 3 ENHANCEMENTS ENABLED
echo ============================================================================
echo.
echo   Swing Trading Features:
echo     - Regime Detection (bullish/neutral/bearish)
echo     - Multi-Timeframe Analysis
echo     - Volatility-Based Position Sizing
echo     - Trailing Stops and Profit Targets
echo.
echo   Intraday Monitoring:
echo     - 15-minute interval scanning
echo     - Breakout/Breakdown alerts
echo     - Volume and momentum analysis
echo.
echo   Cross-Timeframe Integration:
echo     - Entry enhancement with sentiment boost
echo     - Exit enhancement with early signals
echo     - Sentiment-based blocking
echo.
echo ============================================================================
echo   TRADING COMMANDS
echo ============================================================================
echo.
echo   buy('AAPL', 100)              Buy with Phase 3 analysis
echo   sell('AAPL')                  Sell with cross-timeframe checks
echo   status()                      Portfolio with regime info
echo   positions()                   Positions with sentiment
echo   scan_intraday()               Manual intraday scan
echo   market_sentiment()            Current market conditions
echo   update_regime('AAPL', 'bullish')  Set regime manually
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
echo [STARTING] Phase 3 Enhanced Manual Trading on PORT 5004...
echo.

REM Start with port argument
python manual_trading_phase3.py --port 5004

REM Handle exit
echo.
echo.
echo ============================================================================
echo   Phase 3 Enhanced Platform stopped
echo ============================================================================
echo.
pause
