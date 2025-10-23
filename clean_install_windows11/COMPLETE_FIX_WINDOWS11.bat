@echo off
echo ===============================================
echo COMPLETE STOCK TRACKER FIX FOR WINDOWS 11
echo Fixes ALL Module Loading Issues
echo ===============================================
echo.

:: Kill any existing Python processes on our ports
echo [1/5] Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

:: Check if Python is installed
echo [2/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Install required packages
echo [3/5] Installing required packages...
pip install --quiet --upgrade pip
pip install --quiet fastapi uvicorn yfinance pandas numpy cachetools python-multipart aiofiles

:: Start backend on port 8002
echo [4/5] Starting backend server on port 8002...
start /min cmd /c "title Stock Tracker Backend & python backend.py"
timeout /t 3 >nul

:: Start frontend HTTP server on port 8000
echo [5/5] Starting frontend server on port 8000...
start /min cmd /c "title Stock Tracker Frontend & python -m http.server 8000"
timeout /t 2 >nul

:: Open the application in default browser
echo.
echo ===============================================
echo STOCK TRACKER IS NOW RUNNING!
echo ===============================================
echo.
echo Backend API: http://localhost:8002
echo Frontend UI: http://localhost:8000
echo.
echo Opening application in your default browser...
start http://localhost:8000

echo.
echo Press any key to stop all servers and exit...
pause >nul

:: Kill servers when done
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Servers stopped. Goodbye!
timeout /t 2 >nul