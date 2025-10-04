@echo off
echo ========================================
echo Stock Tracker Pro - Windows 11 Edition
echo Version 7.0 with Real ML Integration
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

echo.
echo [2/4] Installing/Updating dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
echo [3/4] Starting backend servers...

REM Kill any existing processes on ports 8002 and 8004
echo Cleaning up any existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8004') do (
    taskkill /PID %%a /F >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo Starting Main Backend Server (port 8002)...
start /B python backend.py

timeout /t 3 /nobreak >nul

echo Starting ML Backend Server (port 8004)...
start /B python backend_ml_enhanced.py

timeout /t 3 /nobreak >nul

echo.
echo [4/4] Launching application...
echo.
echo ========================================
echo Application is running!
echo ========================================
echo.
echo Main Dashboard: http://localhost:8002
echo Diagnostic Tool: http://localhost:8002/diagnostic_tool.html
echo Verify Setup: http://localhost:8002/verify_setup.html
echo.
echo Opening in your default browser...
start http://localhost:8002

echo.
echo Press Ctrl+C to stop all servers
echo.

REM Keep the window open and servers running
:loop
timeout /t 60 /nobreak >nul
goto loop