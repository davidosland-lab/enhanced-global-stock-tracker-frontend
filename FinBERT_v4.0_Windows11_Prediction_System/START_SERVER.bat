@echo off
echo ========================================================================
echo   FinBERT v4.0 - Prediction Caching System
echo   Starting Server...
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/3] Checking Python version...
python --version

echo.
echo [2/3] Checking dependencies...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Flask not installed
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Remove problematic .env file if it exists
if exist .env (
    echo Removing problematic .env file...
    del .env
)

REM Set environment variable to disable .env file loading
set FLASK_SKIP_DOTENV=1

echo [3/3] Starting FinBERT v4.0 Server...
echo.
echo ========================================================================
echo   Server will start on http://localhost:5001
echo   Open your browser and navigate to that address
echo   Press Ctrl+C to stop the server
echo ========================================================================
echo.

python app_finbert_v4_dev.py

pause
