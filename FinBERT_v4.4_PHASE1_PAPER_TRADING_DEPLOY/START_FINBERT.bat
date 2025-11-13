@echo off
echo ================================================================================
echo   FinBERT v4.4 - Starting Server
echo   Phase 1: Enhanced Accuracy + Paper Trading
echo ================================================================================
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Using system Python.
    echo To create venv: python -m venv venv
    echo.
)

echo Starting FinBERT server...
echo.
echo Server will be available at:
echo   http://localhost:5001
echo   (or http://localhost:5000 if 5001 is in use)
echo.
echo Press Ctrl+C to stop the server
echo.
echo ================================================================================
echo.

python app_finbert_v4_dev.py

pause
