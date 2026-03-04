@echo off
echo =====================================
echo   FinBERT v3.3 WITH PREDICTIONS
echo =====================================
echo.
echo This version includes:
echo - ML Predictions with confidence scores
echo - Sentiment analysis
echo - Technical indicators
echo - All working together!
echo.

REM Stop any existing Python processes
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Starting backend with predictions...
echo.

REM Start the predictions-enabled version
if exist "app_finbert_predictions_fixed.py" (
    start "FinBERT Predictions" cmd /k python app_finbert_predictions_fixed.py
) else (
    echo ERROR: Predictions backend not found!
    pause
    exit /b 1
)

timeout /t 5 >nul

echo.
echo Opening browser...
start http://localhost:5000

echo.
echo =====================================
echo System running with predictions!
echo =====================================
echo.
echo You should now see:
echo - Next Day Prediction with price
echo - Confidence percentage
echo - BUY/HOLD/SELL recommendation
echo - Sentiment gauge working
echo.
pause