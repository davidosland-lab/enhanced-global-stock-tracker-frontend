@echo off
cls
color 0A
title GSMT - Global Stock Market Tracker

echo ============================================================
echo     GLOBAL STOCK MARKET TRACKER (GSMT) v7.0
echo     Real-Time Market Data - Yahoo Finance
echo ============================================================
echo.

REM Set current directory
set GSMT_HOME=%~dp0
cd /d "%GSMT_HOME%"

echo [1/4] Checking Python installation...
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
echo [2/4] Installing/updating dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet fastapi uvicorn yfinance pandas numpy python-multipart requests
echo      Dependencies ready!

echo.
echo [3/4] Starting live market data server...
REM Kill any existing servers on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Start the backend server
start "GSMT Backend Server" /min cmd /c "cd /d "%GSMT_HOME%backend" && python live_market_server_simple.py"

echo      Waiting for server initialization...
timeout /t 3 /nobreak >nul
echo      Server started!

echo.
echo [4/4] Opening tracker in your browser...

REM Use Python to open the browser (most reliable method)
python browser_launcher.py

echo.
echo ============================================================
echo     GSMT is now running!
echo ============================================================
echo.
echo     Market Hours (AEST):
echo     • ASX 200:    10:00 - 16:00
echo     • FTSE 100:   17:00 - 01:30
echo     • S&P 500:    23:30 - 06:00
echo.
echo     Features:
echo     ✓ Real-time Yahoo Finance data
echo     ✓ Markets shown only during trading hours
echo     ✓ Automatic refresh every minute
echo     ✓ NO demo or synthetic data
echo.
echo     Keep this window open for the backend server.
echo     Press any key to stop GSMT and exit...
echo ============================================================
pause >nul

echo.
echo Stopping GSMT services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 2^>nul') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo GSMT stopped successfully.
timeout /t 2 /nobreak >nul