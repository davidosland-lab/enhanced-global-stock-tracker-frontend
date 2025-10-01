@echo off
cls
color 0B
title GSMT - Launch Global Indices Tracker in Browser

echo ================================================
echo  GSMT - Global Indices Tracker
echo  Market Hours Display Version
echo  LIVE Yahoo Finance Data ONLY
echo ================================================
echo.

REM Get the current directory
set CURRENT_DIR=%~dp0

echo Starting backend server...
REM Kill any existing servers on port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)

REM Start the live backend server
start "GSMT Live Server" /min cmd /c "cd /d "%CURRENT_DIR%backend" && python live_market_server_simple.py"

echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo.
echo Opening tracker in browser...
echo.

REM Try multiple methods to open in browser
REM Method 1: Using start with full path
start "" "%CURRENT_DIR%frontend\indices_tracker_market_hours.html"

REM Method 2: If that fails, try with explorer
if errorlevel 1 (
    explorer "%CURRENT_DIR%frontend\indices_tracker_market_hours.html"
)

REM Method 3: If that fails, try with rundll32
if errorlevel 1 (
    rundll32 url.dll,FileProtocolHandler "%CURRENT_DIR%frontend\indices_tracker_market_hours.html"
)

echo.
echo ================================================
echo  Tracker opened in your default browser!
echo ================================================
echo.
echo Features:
echo - Markets display ONLY during trading hours
echo - ASX: 10:00-16:00 AEST
echo - FTSE: 17:00-01:30 AEST
echo - S&P 500: 23:30-06:00 AEST
echo - Real Yahoo Finance data
echo - NO demo/synthetic data
echo.
echo Keep this window open for the backend server.
echo Press any key to stop the server and exit...
pause >nul

REM Kill the server when done
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)