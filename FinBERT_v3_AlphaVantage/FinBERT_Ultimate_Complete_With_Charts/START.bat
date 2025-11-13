@echo off
cls
echo ================================================================
echo    FinBERT Ultimate Trading System with Charts
echo    Version 3.0 - Complete Edition
echo ================================================================
echo.

:: Set environment variable to skip .env file issues
set FLASK_SKIP_DOTENV=1

:: Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not accessible
    echo Please run INSTALL.bat first
    pause
    exit /b 1
)

echo [1/3] Starting FinBERT Ultimate backend server...
echo.

:: Start the backend server in a new window
start "FinBERT Ultimate Server" /min cmd /c "python app_finbert_ultimate.py"

:: Wait for server to initialize
echo Waiting for server to initialize...
timeout /t 5 /nobreak >nul

:: Check if server is running
echo [2/3] Checking server status...
curl -s http://localhost:5000/ >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] Server might still be starting up...
    echo If charts don't load data, please wait a moment and refresh.
    echo.
) else (
    echo [SUCCESS] Server is running!
)

echo.
echo [3/3] Opening FinBERT Charts interface...
echo.

:: Open the charts in default browser
start "" "finbert_charts.html"

echo.
echo ================================================================
echo    System Started Successfully!
echo ================================================================
echo.
echo Access Points:
echo   - Charts UI:  [Browser should open automatically]
echo   - API Server: http://localhost:5000
echo   - API Docs:   http://localhost:5000/api
echo.
echo Available Endpoints:
echo   - GET  /api/stock/{symbol}       - Get stock data
echo   - GET  /api/predict/{symbol}     - Get AI predictions
echo   - POST /api/train               - Train new model
echo   - GET  /api/historical/{symbol}  - Get historical data
echo   - GET  /api/news/{symbol}        - Get news & sentiment
echo.
echo Quick Start Guide:
echo   1. Enter a stock symbol (e.g., AAPL, MSFT, TSLA)
echo   2. Select time period (1D to 1Y)
echo   3. Click "Analyze" to load data
echo   4. Toggle indicators on/off as needed
echo   5. View predictions and sentiment scores
echo.
echo Tips:
echo   - First prediction may take 30-60 seconds (model training)
echo   - Subsequent predictions are faster (~2-5 seconds)
echo   - Use mouse wheel to zoom charts
echo   - Click and drag to pan through time
echo.
echo To stop: Press Ctrl+C in the server window or close this window
echo.
echo ================================================================
echo.
pause