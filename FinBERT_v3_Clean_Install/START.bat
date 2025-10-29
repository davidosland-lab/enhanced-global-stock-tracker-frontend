@echo off
echo ========================================================
echo FinBERT Ultimate Trading System v3.0 - FIXED
echo ========================================================
echo.
echo Starting the system with real market data...
echo.
echo Features:
echo - Alpha Vantage API (Key: 68ZFANK047DL0KSR)
echo - Direct Yahoo Finance API (bypasses broken yfinance)
echo - FinBERT sentiment analysis
echo - Random Forest ML predictions with confidence
echo - NO synthetic/fallback data - REAL DATA ONLY
echo.

:: Set environment variable to skip .env file issues
set FLASK_SKIP_DOTENV=1

echo Starting server...
echo.
echo Once started:
echo 1. Open your browser to: http://localhost:5000
echo 2. Enter any stock symbol (e.g., AAPL, MSFT, GOOGL)
echo 3. For Australian stocks use .AX suffix (e.g., CBA.AX)
echo.
echo Press Ctrl+C to stop the server
echo.

python app_finbert_v3_fixed.py

if errorlevel 1 (
    echo.
    echo ========================================================
    echo ERROR: Failed to start the server
    echo ========================================================
    echo.
    echo Possible issues:
    echo 1. Python not installed or not in PATH
    echo 2. Required packages not installed
    echo    Run: INSTALL_FINBERT_FIXED.bat
    echo 3. Port 5000 already in use
    echo.
    pause
)