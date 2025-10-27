@echo off
title FinBERT Ultimate Trading System v4.0 - Server
color 0B
cls

echo ================================================================
echo    FINBERT ULTIMATE TRADING SYSTEM v4.0 - STARTING
echo    Fixed: Predictions, Charts, SMA_50, Auto-Training  
echo ================================================================
echo.
echo Starting the enhanced API server with all fixes...
echo.
echo Features:
echo  - Fixed prediction service with auto-training
echo  - Fixed next-day and 5-10 day predictions
echo  - Fixed SMA_50 calculation
echo  - Fixed candlestick chart rendering
echo  - Real data only mode
echo  - FinBERT sentiment analysis
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

:: Check if the fixed API file exists
if not exist app_finbert_api_fixed.py (
    echo ERROR: app_finbert_api_fixed.py not found!
    echo Please ensure all files are extracted correctly.
    pause
    exit /b 1
)

:: Check if the main app exists
if not exist app_finbert_ultimate.py (
    echo ERROR: app_finbert_ultimate.py not found!
    echo Please ensure all files are extracted correctly.
    pause
    exit /b 1
)

echo [1/3] Starting Fixed API Server...
echo.
echo Server will run on: http://localhost:5000
echo.

:: Start the server in a new window
start "FinBERT API Server" cmd /k python app_finbert_api_fixed.py

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
echo SYSTEM IS RUNNING
echo ================================================================
echo.
echo API Server: http://localhost:5000
echo Charts: Open finbert_charts.html in your browser
echo.
echo Available API Endpoints:
echo  - GET  /api/stock/{symbol}     - Get stock data with indicators
echo  - GET  /api/predict/{symbol}   - Get AI predictions (auto-trains)
echo  - GET  /api/historical/{symbol} - Get historical data
echo  - GET  /api/news/{symbol}      - Get news with sentiment
echo  - GET  /api/economic           - Get economic indicators
echo  - POST /api/train              - Force retrain model
echo.
echo Test Links:
echo  - http://localhost:5000/api/stock/AAPL
echo  - http://localhost:5000/api/predict/AAPL
echo.
echo To stop the server, close the server window or press Ctrl+C
echo.
echo ================================================================
echo.
pause