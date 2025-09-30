@echo off
title GSMT v9 - Global Stock Market Tracker
color 0A

echo ================================================================
echo            GSMT v9 - GLOBAL STOCK MARKET TRACKER
echo                     UNIFIED BACKEND SYSTEM
echo ================================================================
echo.

:: Check Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
python --version
echo.

:: Install required packages
echo [2/4] Installing required packages...
pip install --quiet --upgrade yfinance fastapi uvicorn pandas numpy 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Some packages may not have installed correctly.
    echo Attempting to continue...
)
echo Required packages installed.
echo.

:: Kill any existing processes on port 8000
echo [3/4] Clearing port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    echo Stopping existing process on port 8000...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo Port 8000 cleared.
echo.

:: Start the unified backend
echo [4/4] Starting GSMT Unified Backend v9...
echo.
echo ================================================================
echo Backend will start on: http://localhost:8000
echo Dashboard will open at: frontend/dashboard_v9.html
echo ================================================================
echo.

:: Start backend in new window
start "GSMT Backend v9" /min cmd /c "cd backend && python unified_backend_v9.py"

:: Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

:: Check if backend is running
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Backend may not have started correctly.
    echo Attempting to open dashboard anyway...
)

:: Open dashboard in default browser
echo.
echo Opening GSMT Dashboard in your browser...
start "" "frontend/dashboard_v9.html"

echo.
echo ================================================================
echo GSMT v9 is now running!
echo.
echo Dashboard: frontend/dashboard_v9.html
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to view backend logs...
echo ================================================================
pause >nul

:: Show backend logs
echo.
echo Backend Logs:
echo -------------
cd backend
python unified_backend_v9.py