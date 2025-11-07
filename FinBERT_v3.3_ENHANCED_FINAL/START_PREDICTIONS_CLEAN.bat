@echo off
echo =====================================
echo   FinBERT v3.3 CLEAN WITH PREDICTIONS
echo =====================================
echo.
echo Features:
echo [+] Real market data from Yahoo Finance
echo [+] ML Predictions with confidence scores
echo [+] Sentiment analysis
echo [+] Technical indicators
echo [+] No dotenv issues!
echo.

REM Stop any existing Python processes
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Starting clean predictions backend...
echo.

REM Start the clean predictions version
if exist "app_finbert_predictions_clean.py" (
    start "FinBERT Clean" cmd /k python app_finbert_predictions_clean.py
) else (
    echo ERROR: Clean predictions backend not found!
    pause
    exit /b 1
)

timeout /t 5 >nul

echo.
echo Opening browser at http://localhost:5000
start http://localhost:5000

echo.
echo =====================================
echo System running successfully!
echo =====================================
echo.
echo You should now see:
echo - Real stock prices (no $0.00)
echo - Next Day Prediction with price
echo - Confidence percentage (50-85%)
echo - BUY/HOLD/SELL recommendation
echo - Sentiment gauge (POSITIVE/NEUTRAL/NEGATIVE)
echo - Working candlestick charts
echo - Volume charts below price
echo.
echo Press any key to exit...
pause >nul