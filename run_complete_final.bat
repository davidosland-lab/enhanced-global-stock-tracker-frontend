@echo off
echo ===============================================
echo Starting Complete Final Stock Analysis System
echo ===============================================
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install --quiet flask flask-cors yfinance pandas numpy plotly scikit-learn requests

echo.
echo ===============================================
echo Starting server on http://localhost:8000
echo ===============================================
echo.
echo FEATURES:
echo - Working Plotly charts (displays properly)
echo - Intraday options (1m, 5m, 15m, 30m, 1h)
echo - Fixed ML predictions (realistic 1-5%% changes)
echo - Australian stocks auto .AX suffix
echo - Yahoo Finance + Alpha Vantage backup
echo - All 12 technical indicators
echo - Clean console (no errors)
echo.
echo Press Ctrl+C to stop the server
echo ===============================================
echo.

python unified_stock_complete_final.py

pause