@echo off
title FinBERT Ultimate Trading System v5.0 - Server
color 0B
cls

echo ================================================================
echo    FINBERT ULTIMATE TRADING SYSTEM v5.0 - STARTING
echo    All Indicators Fixed + Confidence Percentages
echo ================================================================
echo.
echo Starting the enhanced API server with ALL fixes...
echo.
echo Features Fixed in v5.0:
echo  ✓ Technical indicators (RSI, MACD, ATR) - Always show values
echo  ✓ Economic indicators (VIX, Treasury, Dollar, Gold) - Real data
echo  ✓ FinBERT sentiment - Properly calculated
echo  ✓ News feed - Working with yfinance
echo  ✓ Prediction confidence - Shows percentages
echo  ✓ Next-day predictions with confidence %
echo  ✓ 5-10 day targets with confidence %
echo.
echo ================================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

:: Check if the v5 fixed API file exists
if not exist app_finbert_api_v5_fixed.py (
    echo WARNING: v5 API not found, trying v4...
    if not exist app_finbert_api_fixed.py (
        echo ERROR: No API file found!
        echo Please ensure all files are extracted correctly.
        pause
        exit /b 1
    )
    set API_FILE=app_finbert_api_fixed.py
) else (
    set API_FILE=app_finbert_api_v5_fixed.py
)

:: Check if the main app exists
if not exist app_finbert_ultimate.py (
    echo ERROR: app_finbert_ultimate.py not found!
    echo Please ensure all files are extracted correctly.
    pause
    exit /b 1
)

echo [1/3] Starting Fixed API Server v5...
echo.
echo Server will run on: http://localhost:5000
echo Using: %API_FILE%
echo.

:: Start the server in a new window
start "FinBERT API Server v5" cmd /k python %API_FILE%

:: Wait for server to start
echo Waiting for server to initialize...
timeout /t 5 /nobreak >nul

:: Check if server is running
curl -s http://localhost:5000/api >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Server may still be starting up...
    echo If the server doesn't start, check the server window for errors.
    echo.
) else (
    echo Server is running successfully!
)

echo.
echo [2/3] Opening Charts Interface...
echo.

:: Open the charts interface
if exist finbert_charts.html (
    start "" finbert_charts.html
    echo Charts interface opened in browser!
) else (
    echo WARNING: finbert_charts.html not found
    echo You can manually open it from the installation directory
)

echo.
echo [3/3] System Ready!
echo.
echo ================================================================
echo SYSTEM IS RUNNING - v5.0 with ALL FIXES
echo ================================================================
echo.
echo API Server: http://localhost:5000
echo Charts: Open finbert_charts.html in your browser
echo.
echo Test These Fixed Endpoints:
echo  ✓ http://localhost:5000/api/stock/AAPL      (See RSI, MACD, ATR)
echo  ✓ http://localhost:5000/api/predict/AAPL    (See confidence %%)
echo  ✓ http://localhost:5000/api/economic        (See VIX, Gold, etc)
echo  ✓ http://localhost:5000/api/news/AAPL       (See news feed)
echo.
echo What's Working Now:
echo  • RSI, MACD, ATR indicators display correctly
echo  • Economic indicators show real values
echo  • FinBERT sentiment shows actual sentiment
echo  • News feed displays articles
echo  • Predictions show confidence percentages
echo.
echo To stop the server, close the server window or press Ctrl+C
echo.
echo ================================================================
echo.
pause