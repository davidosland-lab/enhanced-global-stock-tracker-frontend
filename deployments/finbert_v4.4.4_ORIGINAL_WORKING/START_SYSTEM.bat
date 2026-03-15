@echo off
title FinBERT Trading System v3.3
color 0B
cls

echo ================================================================================
echo                     FinBERT Ultimate Trading System v3.3                       
echo                              STARTING SYSTEM                                   
echo ================================================================================
echo.
echo Features:
echo [+] Real Market Data from Yahoo Finance
echo [+] ML Predictions with BUY/HOLD/SELL signals
echo [+] Sentiment Analysis from news
echo [+] Technical Indicators (RSI, MACD, Bollinger)
echo [+] Candlestick & Volume Charts
echo.

REM Kill any existing Python processes on port 5000
echo Checking for existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Small delay to ensure port is freed
timeout /t 2 /nobreak >nul

REM Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Start the backend server
echo.
echo Starting FinBERT backend server...
echo.

if exist "app_finbert_predictions_clean.py" (
    REM Start backend in a new window
    start "FinBERT Backend" /MIN cmd /k "python app_finbert_predictions_clean.py"
    
    echo Backend server starting...
    echo Waiting for server to initialize...
    
    REM Wait for server to start
    timeout /t 5 /nobreak >nul
    
    REM Check if server is running
    curl -s http://localhost:5000/api/health >nul 2>&1
    if errorlevel 1 (
        echo.
        echo Warning: Server may still be starting up...
        echo Continuing anyway...
    ) else (
        echo Server is running successfully!
    )
    
) else (
    color 0C
    echo.
    echo ERROR: Backend file not found!
    echo Please ensure app_finbert_predictions_clean.py is in the current directory.
    echo.
    pause
    exit /b 1
)

REM Open the browser
echo.
echo Opening FinBERT in your default browser...
timeout /t 2 /nobreak >nul
start http://localhost:5000

echo.
echo ================================================================================
echo                         SYSTEM RUNNING SUCCESSFULLY!                           
echo ================================================================================
echo.
echo The FinBERT Trading System is now running at: http://localhost:5000
echo.
echo Instructions:
echo 1. Enter a stock symbol (e.g., AAPL, MSFT, GOOGL, TSLA)
echo 2. Click "Get Analysis" to load data
echo 3. View predictions, sentiment, and charts
echo 4. Use interval/period dropdowns to change timeframes
echo.
echo To stop the system: Close this window and the backend window
echo.
echo Press any key to view system status...
pause >nul

cls
echo ================================================================================
echo                          SYSTEM STATUS MONITOR                                
echo ================================================================================
echo.

:status_loop
echo Checking system status...
curl -s http://localhost:5000/api/health >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Backend server is not responding!
    echo.
    echo Troubleshooting:
    echo 1. Check if Python window is still open
    echo 2. Look for error messages in the Python window
    echo 3. Try restarting by running this batch file again
) else (
    color 0A
    echo [OK] Backend server is running
    echo [OK] API endpoint: http://localhost:5000/api/stock/[SYMBOL]
    echo [OK] Web interface: http://localhost:5000
    echo.
    echo Test URLs:
    echo - Apple Stock: http://localhost:5000/api/stock/AAPL
    echo - Microsoft: http://localhost:5000/api/stock/MSFT
    echo - Tesla: http://localhost:5000/api/stock/TSLA
)

echo.
echo Press 'R' to refresh status, 'T' to test API, or 'X' to exit...
choice /c RTX /n >nul
if errorlevel 3 goto end
if errorlevel 2 goto test_api
if errorlevel 1 cls & goto status_loop

:test_api
cls
echo ================================================================================
echo                              API TEST RESULTS                                 
echo ================================================================================
echo.
echo Testing AAPL endpoint...
curl -s "http://localhost:5000/api/stock/AAPL" | python -c "import json, sys; d=json.load(sys.stdin); print(f'Symbol: {d.get(\"symbol\")}'); print(f'Price: ${d.get(\"current_price\")}'); print(f'Prediction: {d.get(\"ml_prediction\",{}).get(\"prediction\")}')" 2>nul
echo.
pause
cls
goto status_loop

:end
echo.
echo Shutting down FinBERT Trading System...
taskkill /F /FI "WindowTitle eq FinBERT Backend*" >nul 2>&1
timeout /t 2 /nobreak >nul
exit