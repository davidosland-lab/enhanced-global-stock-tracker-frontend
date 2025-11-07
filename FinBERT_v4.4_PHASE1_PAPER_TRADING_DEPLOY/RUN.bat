@echo off
echo ========================================================================
echo   FinBERT v4.4 - Enhanced Accuracy + Paper Trading
echo   Starting Server...
echo ========================================================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Starting FinBERT v4.4 server...
echo.
echo Server will start on: http://localhost:5001
echo Press Ctrl+C to stop the server
echo.
echo ========================================================================
echo.

python app_finbert_v4_dev.py

pause
