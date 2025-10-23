@echo off
echo ========================================
echo Stock Tracker V5 - Service Launcher
echo With ML Backtesting & FinBERT Sentiment
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Starting services...
echo.

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Start Main Backend (Port 8002)
echo [1/4] Starting Main Backend API on port 8002...
start "Main Backend" cmd /k "python backend.py 2>&1 | tee logs\backend.log"
timeout /t 3 >nul

REM Start ML Backend (Port 8003)
echo [2/4] Starting ML Backend on port 8003...
start "ML Backend" cmd /k "python ml_backend_enhanced.py 2>&1 | tee logs\ml_backend.log"
timeout /t 3 >nul

REM Start Integration Bridge (Port 8004)
echo [3/4] Starting Integration Bridge on port 8004...
start "Integration Bridge" cmd /k "python integration_bridge.py 2>&1 | tee logs\integration.log"
timeout /t 3 >nul

REM Start Web Server (Port 8080)
echo [4/4] Starting Web Interface on port 8080...
start "Web Server" cmd /k "python -m http.server 8080 2>&1 | tee logs\webserver.log"
timeout /t 2 >nul

echo.
echo ========================================
echo All services started successfully!
echo ========================================
echo.
echo Services running on:
echo - Web Interface: http://localhost:8080
echo - Main API:      http://localhost:8002
echo - ML Backend:    http://localhost:8003
echo - Integration:   http://localhost:8004
echo.
echo Features available:
echo - Real-time Stock Tracking
echo - ML Training & Prediction
echo - Backtesting with $100,000 capital
echo - FinBERT Sentiment Analysis
echo - 5 Trading Strategies
echo - SQLite Historical Data Cache
echo.
echo Opening browser...
timeout /t 2 >nul
start http://localhost:8080

echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping all services...
taskkill /F /FI "WINDOWTITLE eq Main Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq ML Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Integration Bridge*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Web Server*" >nul 2>&1

echo Services stopped.
echo.
pause