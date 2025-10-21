@echo off
cls
echo ============================================================
echo ML STOCK PREDICTOR - YAHOO FINANCE OPTIMIZED VERSION
echo ============================================================
echo.
echo This version uses Yahoo Finance ONLY (Best for Australian stocks)
echo Alpha Vantage is DISABLED for better reliability
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8 or later
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing required packages...
pip install flask flask-cors yfinance pandas numpy requests --no-cache-dir -q

echo.
echo ============================================================
echo STARTING YAHOO-OPTIMIZED SERVER
echo ============================================================
echo.
echo Features:
echo - Yahoo Finance ONLY (more reliable)
echo - Australian stocks auto-detection (CBA becomes CBA.AX)
echo - Real-time predictions
echo - Natural language AI assistant
echo.
echo Supported Markets:
echo - Australian (ASX): CBA, BHP, CSL, NAB, WBC, ANZ, etc.
echo - US Stocks: AAPL, MSFT, GOOGL, AMZN, etc.
echo - International: UK (.L), Germany (.DE), Japan (.T)
echo.
echo ============================================================
echo.
echo Starting server...
echo Open your browser to: http://localhost:8000
echo.

python yahoo_only_server.py

pause