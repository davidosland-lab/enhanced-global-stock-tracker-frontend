@echo off
REM Unified Paper Trading Dashboard Startup
REM ========================================
REM 
REM All-in-one solution:
REM - Stock selection via web interface
REM - Paper trading with ML signals
REM - Live dashboard
REM
REM No need for separate terminals!

echo.
echo ================================================================
echo   UNIFIED PAPER TRADING DASHBOARD
echo ================================================================
echo.
echo Starting all-in-one trading system...
echo.
echo This will:
echo   1. Start the unified dashboard server
echo   2. Open your browser to http://localhost:8050
echo   3. Let you select stocks from the web interface
echo   4. Run paper trading in the background
echo   5. Show live results in real-time
echo.
echo ----------------------------------------------------------------
echo.

REM Change to the correct directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version
echo.

echo [2/3] Verifying required packages...
python -c "import dash, plotly, pandas, numpy" 2>nul
if errorlevel 1 (
    echo.
    echo [WARN] Some packages missing. Installing...
    pip install dash plotly pandas numpy torch keras transformers xgboost lightgbm catboost scikit-learn yfinance
    echo.
)
echo [OK] All packages available
echo.

echo [3/3] Starting Unified Dashboard...
echo.
echo ================================================================
echo   DASHBOARD STARTING
echo ================================================================
echo.
echo   URL: http://localhost:8050
echo.
echo   Actions:
echo   1. Select stocks from dropdown or enter custom symbols
echo   2. Set your initial capital (default: $100,000)
echo   3. Click "Start Trading" button
echo   4. Watch live dashboard updates every 5 seconds
echo.
echo   To stop: Close this window or press Ctrl+C
echo.
echo ================================================================
echo.

REM Start the unified dashboard
python unified_trading_dashboard.py

pause
