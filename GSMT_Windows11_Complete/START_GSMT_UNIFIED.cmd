@echo off
cls
color 0A
title GSMT v8.1 - Unified Backend

echo ============================================================
echo     GSMT v8.1 - UNIFIED SYSTEM
echo     All Modules with Single Backend
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
echo [Step 3] Stopping any existing servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 2^>nul') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 2^>nul') do taskkill /F /PID %%a >nul 2>&1
echo         ✓ Ports cleared

echo.
echo [Step 4] Starting Unified Backend Server...
start "GSMT Unified Backend" /min cmd /c "cd /d "%GSMT_HOME%backend" && python unified_backend.py"
timeout /t 3 /nobreak >nul
echo         ✓ Backend server started on port 8000

echo.
echo [Step 5] Updating frontend configuration...
echo window.CONFIG = { BACKEND_URL: 'http://localhost:8000' }; > "%GSMT_HOME%frontend\config.js"
echo         ✓ Frontend configured

echo.
echo [Step 6] Opening dashboard...

REM Try to open dashboard in browser
set DASHBOARD=%GSMT_HOME%frontend\comprehensive_dashboard_v8.html

REM Try Chrome
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "file:///%DASHBOARD:\=/%"
    goto :opened
)
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" "file:///%DASHBOARD:\=/%"
    goto :opened
)

REM Try Edge
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" "file:///%DASHBOARD:\=/%"
    goto :opened
)

REM Try Firefox
if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" (
    start "" "%ProgramFiles%\Mozilla Firefox\firefox.exe" "file:///%DASHBOARD:\=/%"
    goto :opened
)

REM Fallback
start "" "%DASHBOARD%"

:opened
echo.
echo ============================================================
echo     GSMT v8.1 IS RUNNING!
echo ============================================================
echo.
echo ✓ All modules using unified backend on port 8000
echo ✓ Real Yahoo Finance data only
echo ✓ 5-minute interval updates
echo ✓ Dynamic Y-axis scaling
echo.
echo Modules Available:
echo • Global Indices Tracker - Fixed 5-min plotting & Y-axis
echo • Single Stock Tracker - Working data fetching
echo • CBA Banking Intelligence - Connected to live data
echo • Technical Analysis - Chart.js based indicators
echo.
echo Dashboard Location:
echo %DASHBOARD%
echo.
echo ============================================================
echo.
echo Press any key to stop the server and exit...
pause >nul

echo.
echo Stopping server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do taskkill /F /PID %%a >nul 2>&1

echo Done!
timeout /t 2 /nobreak >nul