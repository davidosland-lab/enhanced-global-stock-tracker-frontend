@echo off
echo ==========================================
echo Stock Tracker v14.0 - Complete System Startup
echo ==========================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

:: Kill any existing processes on our ports
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1

:: Install required packages
echo.
echo Installing required packages...
pip install fastapi uvicorn yfinance pandas numpy python-multipart aiofiles requests -q

:: Start Frontend Server
echo.
echo Starting Frontend Server on port 8000...
start /min cmd /c "cd /d %~dp0 && python -m http.server 8000"

:: Wait a moment
timeout /t 2 /nobreak >nul

:: Start Main Backend
echo Starting Main Backend on port 8002...
start /min cmd /c "cd /d %~dp0 && python backend.py"

:: Wait a moment
timeout /t 2 /nobreak >nul

:: Start ML Backend v2 (with fixed column handling)
echo Starting ML Backend on port 8003...
start /min cmd /c "cd /d %~dp0 && python ml_backend_v2.py"

:: Wait for services to start
echo.
echo Waiting for services to initialize...
timeout /t 5 /nobreak

:: Check service status
echo.
echo ==========================================
echo Checking Service Status...
echo ==========================================

:: Check Frontend
curl -s http://localhost:8000 >nul 2>&1
if errorlevel 1 (
    echo [FAILED] Frontend Server
) else (
    echo [OK] Frontend Server - http://localhost:8000
)

:: Check Main Backend
curl -s http://localhost:8002/health >nul 2>&1
if errorlevel 1 (
    echo [FAILED] Main Backend
) else (
    echo [OK] Main Backend - http://localhost:8002
)

:: Check ML Backend
curl -s http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo [FAILED] ML Backend
) else (
    echo [OK] ML Backend - http://localhost:8003
)

echo.
echo ==========================================
echo Stock Tracker is ready!
echo ==========================================
echo.
echo Access the application at: http://localhost:8000
echo.
echo Features:
echo - Real-time Yahoo Finance data only (no synthetic data)
echo - ML Training with correct column handling
echo - 100MB document upload support
echo - All modules working with real data
echo.
echo Press any key to open in browser...
pause >nul

:: Open in default browser
start http://localhost:8000

echo.
echo ==========================================
echo IMPORTANT: Keep this window open!
echo Closing this window will stop all services.
echo ==========================================
echo.
echo To stop all services, press Ctrl+C or close this window.
pause >nul