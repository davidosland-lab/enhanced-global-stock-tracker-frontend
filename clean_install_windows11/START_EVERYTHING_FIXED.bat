@echo off
echo ============================================================
echo COMPLETE STOCK TRACKER STARTUP - WITH HISTORICAL DATA FIX
echo ============================================================
echo.

:: Set window title
title Stock Tracker Complete System

:: Kill any existing Python processes on our ports
echo [1/6] Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Kill any Python processes
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

timeout /t 2 >nul

:: Check Python installation
echo [2/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

:: Install/upgrade required packages
echo [3/6] Installing required packages...
echo Installing yfinance with urllib3 fix for Python 3.12...
pip install --upgrade --quiet yfinance "urllib3<2" pandas numpy fastapi uvicorn python-multipart cachetools pytz

:: Create historical data directory
echo [4/6] Setting up directories...
if not exist "historical_data" mkdir historical_data
if not exist "uploads" mkdir uploads

:: Start Frontend Server (HTTP server on port 8000)
echo [5/6] Starting Frontend Server on port 8000...
start /min cmd /c "title Frontend Server && python -m http.server 8000"

timeout /t 2 >nul

:: Start Main Backend with Historical Data Manager (port 8002)
echo [6/6] Starting Main Backend with Historical Data Manager on port 8002...
start cmd /k "title Backend Server - Port 8002 && echo. && echo ===================================== && echo BACKEND SERVER WITH HISTORICAL DATA && echo ===================================== && echo. && echo Starting backend with complete Historical Data Manager support... && echo. && python backend.py"

timeout /t 3 >nul

:: Check if services are running
echo.
echo ============================================================
echo CHECKING SERVICE STATUS...
echo ============================================================
netstat -an | findstr :8000 >nul
if errorlevel 1 (
    echo WARNING: Frontend server not running on port 8000
) else (
    echo [OK] Frontend server running on port 8000
)

netstat -an | findstr :8002 >nul
if errorlevel 1 (
    echo WARNING: Backend server not running on port 8002
) else (
    echo [OK] Backend server running on port 8002
)

:: Open the application
echo.
echo ============================================================
echo OPENING STOCK TRACKER APPLICATION
echo ============================================================
echo.
echo The application will open in your default browser...
echo.
echo IMPORTANT:
echo - Frontend: http://localhost:8000
echo - Backend API: http://localhost:8002
echo - Historical Data Manager is now fully functional!
echo.
echo To test Historical Data Manager:
echo 1. Click on "Historical Data Manager" module
echo 2. Click "Download Common Symbols" to download ASX stocks
echo 3. Or enter custom symbols and download
echo.
timeout /t 3 >nul
start http://localhost:8000

echo ============================================================
echo SYSTEM READY!
echo ============================================================
echo.
echo Press Ctrl+C in each window to stop the servers
echo Or close this window to keep servers running
echo.
pause