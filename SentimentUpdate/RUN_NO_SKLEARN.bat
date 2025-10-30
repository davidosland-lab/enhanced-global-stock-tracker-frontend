@echo off
title Stock Analysis - No sklearn Required
echo ========================================================
echo    STOCK ANALYSIS WITH SENTIMENT - NO SKLEARN VERSION
echo ========================================================
echo.
echo This version works without scikit-learn!
echo.
echo Features:
echo - Market sentiment analysis (VIX, Breadth, Yields, etc.)
echo - Technical indicators (RSI, MACD, Bollinger Bands)
echo - Simple trend-based predictions
echo - Australian stock support (.AX suffix)
echo - Real-time data from Yahoo Finance
echo.

REM Set encoding to prevent Unicode errors
chcp 65001 >nul 2>&1

REM Kill any existing Python processes on port 5000
echo [*] Checking for existing processes...
netstat -ano | findstr :5000 >nul 2>&1
if %errorlevel%==0 (
    echo [!] Port 5000 in use, attempting to free it...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
        taskkill /PID %%a /F >nul 2>&1
    )
    timeout /t 2 >nul
)

REM Start the application
echo [*] Starting application...
echo.
echo ========================================================
echo    Server running at http://localhost:5000
echo    Press Ctrl+C to stop
echo ========================================================
echo.

python app_sentiment_no_sklearn.py

if errorlevel 1 (
    echo.
    echo [!] Error: Application failed to start
    echo.
    echo Troubleshooting:
    echo 1. Make sure Python is installed
    echo 2. Check if required packages are installed:
    echo    - flask
    echo    - yfinance
    echo    - pandas
    echo    - numpy
    echo.
    echo To install missing packages:
    echo pip install flask yfinance pandas numpy flask-cors
    echo.
)

pause