@echo off
echo Starting Yahoo Finance Backend Server...
echo =====================================
echo.
echo This server provides real Yahoo Finance data to all modules
echo Server will run on http://localhost:8002
echo.
echo Press Ctrl+C to stop the server
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

REM Install required packages if needed
echo Checking/Installing required packages...
pip install yfinance fastapi uvicorn python-multipart cachetools pandas pytz --quiet

REM Start the backend server
echo.
echo Starting server...
echo =====================================
python backend_fixed_v2.py

pause