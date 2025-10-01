@echo off
cls
color 0A
title GSMT - Global Stock Market Tracker (Ultimate Launcher)

echo ============================================================
echo     GLOBAL STOCK MARKET TRACKER (GSMT) v7.0
echo     Ultimate Browser Launcher
echo ============================================================
echo.

REM Set current directory
set GSMT_HOME=%~dp0
cd /d "%GSMT_HOME%"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet fastapi uvicorn yfinance pandas numpy python-multipart requests

echo.
echo Starting backend server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
start "GSMT Backend" /min cmd /c "cd /d "%GSMT_HOME%backend" && python live_market_server_simple.py"
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo     OPENING GSMT IN BROWSER
echo ============================================================
echo.

REM Build the URL
set HTML_PATH=%GSMT_HOME%frontend\indices_tracker_market_hours.html
set FILE_URL=file:///%HTML_PATH:\=/%

echo Trying multiple methods to open browser...
echo.

REM Method 1: Python webbrowser (most reliable)
echo [Method 1] Using Python webbrowser module...
python -c "import webbrowser; webbrowser.open('%FILE_URL%')" >nul 2>&1
if not errorlevel 1 (
    echo SUCCESS! Browser opened with Python.
    goto browser_opened
)

REM Method 2: PowerShell Start-Process
echo [Method 2] Using PowerShell...
powershell -Command "Start-Process '%FILE_URL%'" >nul 2>&1
if not errorlevel 1 (
    echo SUCCESS! Browser opened with PowerShell.
    goto browser_opened
)

REM Method 3: Direct browser executables
echo [Method 3] Trying Chrome...
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "%FILE_URL%"
    echo SUCCESS! Opened with Chrome.
    goto browser_opened
)

echo [Method 4] Trying Edge...
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" "%FILE_URL%"
    echo SUCCESS! Opened with Edge.
    goto browser_opened
)

echo [Method 5] Trying Firefox...
if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" (
    start "" "%ProgramFiles%\Mozilla Firefox\firefox.exe" "%FILE_URL%"
    echo SUCCESS! Opened with Firefox.
    goto browser_opened
)

REM Method 6: Start command with URL
echo [Method 6] Using start command with URL...
start "%FILE_URL%" >nul 2>&1
if not errorlevel 1 (
    echo SUCCESS! Browser opened with start command.
    goto browser_opened
)

REM Method 7: Explorer
echo [Method 7] Using Windows Explorer...
explorer "%HTML_PATH%"

REM If all methods fail
echo.
echo ============================================================
echo     MANUAL BROWSER OPENING REQUIRED
echo ============================================================
echo.
echo Could not open browser automatically.
echo.
echo To open GSMT manually:
echo 1. Open any web browser (Chrome, Edge, Firefox)
echo 2. Copy this address:
echo.
echo %FILE_URL%
echo.
echo 3. Paste it in the browser's address bar and press Enter
echo.
echo Alternative local path:
echo %HTML_PATH%
echo ============================================================

:browser_opened
echo.
echo ============================================================
echo     GSMT SERVER IS RUNNING
echo ============================================================
echo.
echo Backend server is running on http://localhost:8000
echo.
echo Market Trading Hours (AEST):
echo • ASX 200:    10:00 - 16:00
echo • FTSE 100:   17:00 - 01:30
echo • S&P 500:    23:30 - 06:00
echo.
echo The tracker shows markets ONLY during their trading hours.
echo Data is from Yahoo Finance - NO demo/synthetic data.
echo.
echo IMPORTANT: Keep this window open for the server to run!
echo Press any key to stop the server and exit...
echo ============================================================
pause >nul

echo.
echo Stopping GSMT server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo Server stopped.
timeout /t 2 /nobreak >nul