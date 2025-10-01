@echo off
title Global Stock Market Tracker v9.3 - FIXED Market Timing
color 0A

echo ============================================================
echo   Global Stock Market Tracker v9.3 - Windows Deployment
echo   CRITICAL FIX: S&P 500 now shows at 00:30-07:00 AEST
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Starting Enhanced Backend Server (Port 8000)...
echo -----------------------------------------------------
cd backend
start "GSMT Backend - Port 8000" cmd /k "python enhanced_market_backend.py"
timeout /t 3 >nul

echo.
echo [2/4] Starting Frontend Server (Port 3001)...
echo -----------------------------------------------------
cd ../frontend
start "GSMT Frontend - Port 3001" cmd /k "python -m http.server 3001"
timeout /t 2 >nul

echo.
echo [3/4] Waiting for services to initialize...
echo -----------------------------------------------------
timeout /t 3 >nul

echo.
echo [4/4] Opening browser...
echo -----------------------------------------------------
start http://localhost:3001

echo.
echo ============================================================
echo   GSMT v9.3 is now running!
echo ============================================================
echo.
echo   Main Dashboard:  http://localhost:3001
echo   Indices Tracker: http://localhost:3001/indices_tracker_final.html
echo   Backend API:     http://localhost:8000/api/indices
echo.
echo   Market Hours (AEST):
echo   - Americas:   00:30 - 07:00 (BEFORE ASX - FIXED!)
echo   - Asia-Pac:   10:00 - 16:00
echo   - Europe:     18:00 - 02:30
echo.
echo   Press any key to view logs...
echo ============================================================
pause >nul

:: Keep window open to show status
echo.
echo Services are running. Close this window to stop monitoring.
echo To stop all services, run STOP_GSMT.bat
echo.
pause