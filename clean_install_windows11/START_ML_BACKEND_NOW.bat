@echo off
title ML Backend Startup - Port 8003
color 0A

echo ================================================================================
echo                        STARTING ML BACKEND
echo ================================================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher from python.org
    echo.
    pause
    exit /b 1
)

:: Check if backend_ml_enhanced.py exists
if not exist backend_ml_enhanced.py (
    echo ERROR: backend_ml_enhanced.py not found!
    echo.
    echo Current directory: %cd%
    echo.
    echo Please make sure you're running this from the Stock Tracker folder
    echo that contains backend_ml_enhanced.py
    echo.
    dir *.py
    echo.
    pause
    exit /b 1
)

echo Found backend_ml_enhanced.py
echo.

:: Kill any existing process on port 8003
echo Checking if port 8003 is already in use...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8003') do (
    echo Stopping existing process on port 8003 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo Installing required packages (this may take a moment)...
pip install fastapi uvicorn yfinance pandas numpy scikit-learn python-multipart --quiet

echo.
echo ================================================================================
echo                    STARTING ML BACKEND ON PORT 8003
echo ================================================================================
echo.
echo DO NOT CLOSE THIS WINDOW!
echo The ML Backend must keep running for the ML Training Centre to work.
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo ML Backend starting now...
echo If you see errors below, they will help identify the problem.
echo.
echo --------------------------------------------------------------------------------

:: Run the ML Backend
python backend_ml_enhanced.py

:: If we get here, the backend stopped
echo.
echo --------------------------------------------------------------------------------
echo.
echo ML Backend has stopped!
echo.
echo If you see errors above, they indicate what's wrong.
echo Common issues:
echo   - Missing packages (run: pip install -r requirements.txt)
echo   - Port 8003 blocked by firewall
echo   - Syntax errors in backend_ml_enhanced.py
echo.
pause