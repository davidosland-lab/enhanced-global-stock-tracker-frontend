@echo off
REM Stock Tracker V6 - Windows Startup Script
REM Clean Real ML Implementation

echo ==================================
echo Stock Tracker V6 - Clean Install
echo Real ML Implementation
echo ==================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Create directories
if not exist logs mkdir logs
if not exist saved_models mkdir saved_models
if not exist data mkdir data

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting services...
echo.

REM Start Main Backend
echo [1/3] Starting Main Backend on port 8002...
start "Main Backend" cmd /c "python backend.py"
timeout /t 3 >nul

REM Start ML Backend
echo [2/3] Starting ML Backend on port 8003...
start "ML Backend" cmd /c "python ml_backend.py"
timeout /t 3 >nul

REM Start Web Server
echo [3/3] Starting Web Server on port 8080...
start "Web Server" cmd /c "python -m http.server 8080"
timeout /t 2 >nul

echo.
echo ==================================
echo All services started!
echo ==================================
echo.
echo Access the application at:
echo http://localhost:8080
echo.
echo Services running:
echo - Main API: http://localhost:8002
echo - ML Backend: http://localhost:8003  (REAL ML)
echo - Web Interface: http://localhost:8080
echo.
echo Features:
echo - Real machine learning training
echo - Real predictions (no fake data)
echo - Real backtesting with ML signals
echo.
echo Opening browser...
timeout /t 2 >nul
start http://localhost:8080

echo.
echo Press any key to stop all services...
pause >nul

echo Stopping services...
taskkill /F /FI "WINDOWTITLE eq Main Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq ML Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Web Server*" >nul 2>&1

echo Services stopped.
pause