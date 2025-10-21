@echo off
echo ======================================================================
echo UNIFIED STOCK ANALYSIS SYSTEM - FINAL VERSION
echo ======================================================================
echo.
echo Features:
echo - Real Yahoo Finance data (no mock/demo data)
echo - Australian stocks with automatic .AX suffix
echo - Alpha Vantage backup (API key integrated)
echo - Chart.js for reliable charts
echo - ML Predictions (Random Forest + Gradient Boosting)
echo - 12 Technical indicators
echo - Windows UTF-8 issues fixed
echo.

REM Prevent dotenv UTF-8 errors
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8

echo Installing requirements...
pip install --quiet flask flask-cors yfinance pandas numpy scikit-learn requests

echo.
echo Starting server at http://localhost:8000
echo Press Ctrl+C to stop
echo.

python unified_stock_final.py

pause