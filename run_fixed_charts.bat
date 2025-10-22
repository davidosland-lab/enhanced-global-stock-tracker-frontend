@echo off
echo ===============================================
echo Starting Fixed Chart Rendering System
echo ===============================================
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
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
echo FIXES APPLIED:
echo - Charts render properly for ALL timeframes
echo - 5-year data shows correctly (2020-2025)
echo - 1-day to 6-month charts now display
echo - Candlesticks render properly
echo - Intraday data working (1m, 5m, 15m, 30m, 1h)
echo - New window charts functional
echo.
echo Press Ctrl+C to stop the server
echo ===============================================
echo.

python unified_stock_fixed_charts.py

pause