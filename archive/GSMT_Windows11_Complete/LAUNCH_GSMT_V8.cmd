@echo off
cls
color 0A
title GSMT v8.0 - Complete Trading Platform

echo ============================================================
echo     GSMT v8.0 - COMPLETE TRADING PLATFORM
echo     Starting All Systems...
echo ============================================================
echo.

REM Set current directory
set GSMT_HOME=%~dp0
cd /d "%GSMT_HOME%"

echo [Step 1] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo         ✓ Python ready

echo.
echo [Step 2] Installing dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet fastapi uvicorn yfinance pandas numpy requests
echo         ✓ Dependencies installed

echo.
echo [Step 3] Starting backend servers...

REM Kill existing servers
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 2^>nul') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 2^>nul') do taskkill /F /PID %%a >nul 2>&1

REM Start servers
start "Market Server" /min cmd /c "cd /d "%GSMT_HOME%backend" && python live_market_server_simple.py"
timeout /t 2 /nobreak >nul
start "ML Backend" /min cmd /c "cd /d "%GSMT_HOME%backend" && python enhanced_ml_backend.py"
timeout /t 2 /nobreak >nul
start "CBA Server" /min cmd /c "cd /d "%GSMT_HOME%backend" && python cba_specialist_server.py"

echo         ✓ Backend servers started

echo.
echo [Step 4] Opening dashboard in browser...
echo.

REM Set the dashboard file path
set DASHBOARD=%GSMT_HOME%frontend\comprehensive_dashboard_v8.html

REM Method 1: Try common browsers directly with full path
echo Trying Chrome...
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "file:///%DASHBOARD:\=/%"
    goto :success
)
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" "file:///%DASHBOARD:\=/%"
    goto :success
)

echo Trying Edge...
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" "file:///%DASHBOARD:\=/%"
    goto :success
)
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" "file:///%DASHBOARD:\=/%"
    goto :success
)

echo Trying Firefox...
if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" (
    start "" "%ProgramFiles%\Mozilla Firefox\firefox.exe" "file:///%DASHBOARD:\=/%"
    goto :success
)

REM Method 2: Try PowerShell
echo Trying PowerShell method...
powershell -Command "Start-Process 'file:///%DASHBOARD:\=/%'" >nul 2>&1
if not errorlevel 1 goto :success

REM Method 3: Try rundll32
echo Trying rundll32 method...
rundll32 url.dll,FileProtocolHandler "file:///%DASHBOARD:\=/%" >nul 2>&1

:success
echo.
echo ============================================================
echo     GSMT v8.0 IS NOW RUNNING!
echo ============================================================
echo.
echo If the dashboard didn't open automatically:
echo.
echo 1. Open ANY web browser (Chrome, Edge, Firefox)
echo 2. In the address bar, type exactly:
echo.
echo    file:///%DASHBOARD:\=/%
echo.
echo Or navigate to this file and drag it into your browser:
echo    %DASHBOARD%
echo.
echo ============================================================
echo     MODULES AVAILABLE:
echo ============================================================
echo.
echo • Global Indices Tracker - Real-time with 5-min intervals
echo • Single Stock Track & Predict - Fixed technical indicators
echo • CBA Banking Intelligence - Commonwealth Bank analysis
echo • Technical Analysis - Advanced indicators
echo • Prediction Performance - ML model metrics
echo.
echo Servers Running:
echo • Market Data Server - Port 8000
echo • ML Backend - Port 8001  
echo • CBA Server - Port 8002
echo.
echo ============================================================
echo.
echo Press any key to stop all servers and exit...
pause >nul

echo.
echo Stopping all servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 2^>nul') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 2^>nul') do taskkill /F /PID %%a >nul 2>&1

echo Done!
timeout /t 2 /nobreak >nul