@echo off
setlocal
cls
echo ============================================================
echo    STOCK ANALYSIS - LAUNCHER
echo ============================================================
echo.

REM Change to current directory
cd /d "%~dp0"

REM First check if Python exists
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b
)

REM Show Python version
echo Found Python:
python --version
echo.

REM Check if we have the right file
if exist "app_WORKING.py" (
    set APP_FILE=app_WORKING.py
    echo Found app_WORKING.py
) else if exist "app.py" (
    set APP_FILE=app.py
    echo Found app.py
) else (
    echo ERROR: No app.py or app_WORKING.py found!
    echo Please extract all files from the ZIP.
    echo.
    pause
    exit /b
)

echo.
echo Installing required packages (if needed)...
echo.

REM Install packages silently
pip install flask yfinance plotly scikit-learn pandas requests flask-cors numpy >nul 2>&1

echo Packages ready.
echo.
echo ============================================================
echo Starting Stock Analysis System...
echo ============================================================
echo.
echo Server will run at: http://localhost:8000
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000

echo.
echo Running server...
echo Press Ctrl+C to stop
echo.

REM Set environment variable
set FLASK_SKIP_DOTENV=1

REM Run Python and show all output
python %APP_FILE%

REM If Python exits, we'll see this
echo.
echo ============================================================
echo Server stopped or failed to start.
echo ============================================================
echo.
echo If the server failed immediately, try:
echo 1. Run this command in CMD: pip install -r requirements.txt
echo 2. Then run: python %APP_FILE%
echo.
pause