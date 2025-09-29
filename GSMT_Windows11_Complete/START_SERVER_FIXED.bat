@echo off
:: Fixed Server Start Script for GSMT Stock Tracker
:: Ensures correct backend is running with proper routes

color 0A
cls

echo ============================================================
echo  GSMT STOCK TRACKER - SERVER STARTUP
echo ============================================================
echo.

:: Change to the correct directory
cd /d "C:\GSMT\GSMT_Windows11_Complete"

:: Check if venv exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run FIX_INSTALLATION.bat first
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Kill any existing Python processes on port 8000
echo Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Killing existing process on port 8000...
    taskkill /F /PID %%a 2>nul
)

:: Clear screen for clean start
cls
echo ============================================================
echo  GSMT STOCK TRACKER - STARTING FASTAPI SERVER
echo ============================================================
echo.
echo The server will start with the following endpoints:
echo.
echo  Main Dashboard:    http://localhost:8000
echo  Stock Tracker:     http://localhost:8000/tracker  
echo  Health Check:      http://localhost:8000/health
echo  API Docs:          http://localhost:8000/docs
echo  Predictions:       http://localhost:8000/api/unified-prediction/{symbol}
echo.
echo ============================================================
echo.
echo Starting FastAPI backend...
echo.

:: Start the simple backend (more reliable)
echo Using Simple ML Backend (numpy-free, guaranteed to work)...
python backend\simple_ml_backend.py

:: If simple backend fails, show error
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo  ERROR: Backend failed to start!
    echo ============================================================
    echo.
    echo Possible causes:
    echo  1. Port 8000 is still in use
    echo  2. Missing Python packages
    echo  3. Backend file is corrupted
    echo.
    echo Try running these commands manually:
    echo   cd C:\GSMT\GSMT_Windows11_Complete
    echo   venv\Scripts\activate
    echo   python backend\simple_ml_backend.py
    echo.
    pause
)