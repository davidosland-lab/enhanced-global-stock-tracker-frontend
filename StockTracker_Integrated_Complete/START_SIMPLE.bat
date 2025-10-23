@echo off
REM ================================================================================
REM Stock Tracker - Simple Startup Script
REM This version has better error handling and simpler package installation
REM ================================================================================

echo.
echo =========================================================================
echo    STOCK TRACKER - SIMPLE STARTUP
echo =========================================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python detected successfully
echo.

REM Kill any existing processes
echo Cleaning up any existing services...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend Service*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq ML Service*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Frontend Server*" >nul 2>&1
timeout /t 2 >nul

REM Install only essential packages first
echo Installing essential packages (this may take 2-3 minutes)...
echo.

echo [1/6] Installing FastAPI...
python -m pip install fastapi --quiet --no-warn-script-location 2>nul

echo [2/6] Installing Uvicorn...
python -m pip install uvicorn --quiet --no-warn-script-location 2>nul

echo [3/6] Installing Yahoo Finance...
python -m pip install yfinance --quiet --no-warn-script-location 2>nul

echo [4/6] Installing Pandas...
python -m pip install pandas --quiet --no-warn-script-location 2>nul

echo [5/6] Installing NumPy...
python -m pip install numpy --quiet --no-warn-script-location 2>nul

echo [6/6] Installing support packages...
python -m pip install python-multipart pytz httpx --quiet --no-warn-script-location 2>nul

echo.
echo Package installation complete!
echo.

REM Start services
echo Starting services...
echo.

echo [1/3] Starting Backend Service (Port 8002)...
start "Backend Service" /min cmd /c "python backend.py 8002 2>backend_error.log"
timeout /t 3 >nul

echo [2/3] Starting ML Service (Port 8003)...
start "ML Service" /min cmd /c "python ml_backend.py 8003 2>ml_error.log"
timeout /t 3 >nul

echo [3/3] Starting Web Interface (Port 8000)...
start "Frontend Server" /min cmd /c "python -m http.server 8000 2>frontend_error.log"
timeout /t 2 >nul

echo.
echo =========================================================================
echo    STARTUP COMPLETE!
echo =========================================================================
echo.
echo Services should be running at:
echo   - Web Interface: http://localhost:8000
echo   - Backend API:   http://localhost:8002
echo   - ML Service:    http://localhost:8003
echo.
echo Opening browser...
start http://localhost:8000
echo.
echo If you see any errors, check:
echo   - backend_error.log
echo   - ml_error.log
echo   - frontend_error.log
echo.
echo Press any key to stop all services and exit...
pause >nul

REM Stop services
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend Service*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq ML Service*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Frontend Server*" >nul 2>&1

echo Services stopped.
pause