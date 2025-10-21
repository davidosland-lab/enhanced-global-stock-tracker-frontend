@echo off
echo ====================================================
echo ML STOCK PREDICTOR - UNIFIED SYSTEM
echo ====================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8 or later
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing dependencies...
pip install flask flask-cors yfinance pandas numpy scikit-learn requests --no-cache-dir -q

echo.
echo Starting Unified ML Stock Prediction System...
echo ====================================================
echo Features:
echo - Real Yahoo Finance data (WORKING)
echo - Alpha Vantage backup (API key included)
echo - Machine Learning models
echo - 35+ Technical indicators
echo - Web interface on http://localhost:8000
echo ====================================================
echo.

python unified_system.py

pause