@echo off
cls
color 0B
title GSMT - Global Indices Tracker (Enhanced)

echo =========================================
echo  GSMT - Global Indices Tracker
echo  Enhanced Version with % Changes
echo =========================================
echo.

echo Starting backend services...

REM Start the LIVE market data server (NO DEMO DATA)
tasklist /FI "WINDOWTITLE eq GSMT Live Market Server" 2>nul | find /I "cmd.exe" >nul
if errorlevel 1 (
    echo Starting LIVE Market Data Server on port 8000 (Yahoo Finance ONLY)...
    start "GSMT Live Market Server" /min cmd /c "cd backend && python live_market_server.py"
    timeout /t 3 /nobreak >nul
) else (
    echo Live Market Data Server already running.
)

echo.
echo Opening Enhanced Global Indices Tracker...
echo.

REM Open the enhanced indices tracker
start "" "frontend\indices_tracker_percentage.html"

echo.
echo =========================================
echo  Tracker Features:
echo =========================================
echo.
echo - Regional Market Selection (Asia, Europe, Americas)
echo - Percentage changes from previous close
echo - Real-time data updates every minute
echo - Historical date selection
echo - AEST/AEDT timezone toggle
echo - Market status indicators (Open/Closed)
echo.
echo The tracker is now open in your browser.
echo.
echo Press any key to close this window...
pause >nul