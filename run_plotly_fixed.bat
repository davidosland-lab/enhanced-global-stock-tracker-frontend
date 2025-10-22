@echo off
echo ===============================================
echo Starting Fixed Stock Analysis with Plotly Charts
echo ===============================================
echo.

REM Set environment variable to skip .env file reading (prevents UTF-8 errors)
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

REM Install required packages if needed
echo Checking and installing dependencies...
pip install --quiet flask flask-cors yfinance pandas numpy plotly scikit-learn requests

echo.
echo ===============================================
echo Starting server on http://localhost:8000
echo ===============================================
echo.
echo Features:
echo - NO TradingView errors (using Plotly only)
echo - Working favicon route (no 404)
echo - Australian stocks with auto .AX suffix
echo - Yahoo Finance + Alpha Vantage backup
echo - ML predictions with real data
echo - Interactive Plotly charts
echo.
echo Press Ctrl+C to stop the server
echo ===============================================
echo.

REM Run the fixed server
python unified_stock_plotly_working.py

pause