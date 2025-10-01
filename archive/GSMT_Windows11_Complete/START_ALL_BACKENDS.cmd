@echo off
cls
color 0A
title GSMT v8.0 - Starting All Backend Servers

echo ============================================================
echo     GSMT v8.0 - Complete Backend Startup
echo     Starting All Required Servers
echo ============================================================
echo.

REM Set current directory
set GSMT_HOME=%~dp0
cd /d "%GSMT_HOME%"

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)
echo      Python found!

echo.
echo [2/5] Installing/updating dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet fastapi uvicorn yfinance pandas numpy python-multipart requests tensorflow scikit-learn

echo.
echo [3/5] Starting Live Market Data Server (Port 8000)...
REM Kill any existing servers on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
start "GSMT Market Server" /min cmd /c "cd /d "%GSMT_HOME%backend" && python live_market_server_simple.py"
echo      Market server started on port 8000

timeout /t 2 /nobreak >nul

echo.
echo [4/5] Starting Enhanced ML Backend (Port 8001)...
REM Kill any existing servers on port 8001
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
start "GSMT ML Backend" /min cmd /c "cd /d "%GSMT_HOME%backend" && python enhanced_ml_backend.py"
echo      ML backend started on port 8001

timeout /t 2 /nobreak >nul

echo.
echo [5/5] Starting CBA Specialist Server (Port 8002)...
REM Kill any existing servers on port 8002
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
start "GSMT CBA Server" /min cmd /c "cd /d "%GSMT_HOME%backend" && python cba_specialist_server.py"
echo      CBA specialist server started on port 8002

echo.
echo ============================================================
echo     ALL BACKEND SERVERS STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo Running Servers:
echo • Live Market Data Server - Port 8000 (Yahoo Finance)
echo • Enhanced ML Backend - Port 8001 (Predictions)
echo • CBA Specialist Server - Port 8002 (Commonwealth Bank)
echo.
echo Data Sources:
echo • Real-time market data from Yahoo Finance
echo • NO demo or synthetic data
echo • 5-minute interval updates
echo.
echo Press any key to open the dashboard...
pause >nul

echo Opening dashboard in browser...

REM Use Python to open browser reliably
python -c "import webbrowser; webbrowser.open('file:///%GSMT_HOME:\=/%frontend/comprehensive_dashboard_v8.html')" >nul 2>&1

if errorlevel 1 (
    REM Fallback to direct browser launch
    start "" "%GSMT_HOME%frontend\comprehensive_dashboard_v8.html"
)

echo.
echo ============================================================
echo     GSMT v8.0 is now running!
echo ============================================================
echo.
echo To stop all servers, close this window or press Ctrl+C
echo.
echo Keep this window open for servers to continue running.
pause >nul

echo.
echo Stopping all GSMT servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo All servers stopped.
timeout /t 2 /nobreak >nul