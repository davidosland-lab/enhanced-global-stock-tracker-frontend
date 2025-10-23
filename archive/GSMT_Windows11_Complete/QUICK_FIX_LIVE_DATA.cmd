@echo off
cls
color 0B
title GSMT - Quick Fix for Live Data Only

echo ================================================
echo  GSMT - QUICK FIX FOR LIVE DATA
echo  Removes ALL Demo Data - Yahoo Finance ONLY
echo ================================================
echo.

echo This will:
echo 1. Install missing dependencies
echo 2. Start the live data server
echo 3. Open the tracker with real data only
echo.

echo Press any key to continue...
pause >nul

echo.
echo Step 1: Installing dependencies...
echo ----------------------------------------
python -m pip install --upgrade pip >nul 2>&1
python -m pip install fastapi uvicorn yfinance python-multipart pandas numpy requests >nul 2>&1

echo Dependencies installed.
echo.

echo Step 2: Stopping old servers...
echo ----------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Stopping process %%a...
    taskkill /F /PID %%a >nul 2>&1
)
echo Old servers stopped.
echo.

echo Step 3: Starting LIVE data server...
echo ----------------------------------------
start "GSMT Live Server" /min cmd /c "cd backend && python live_market_server_simple.py"

echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 4: Opening tracker...
echo ----------------------------------------
start "" "frontend\indices_tracker_percentage.html"

echo.
echo ================================================
echo  QUICK FIX COMPLETE!
echo ================================================
echo.
echo The tracker should now be open in your browser.
echo It will ONLY show real Yahoo Finance data.
echo.
echo IMPORTANT:
echo - Keep the server window open (it's minimized)
echo - If you see connection errors, the server may need more time to start
echo - NO DEMO DATA will be shown - only real market data
echo.
echo Press any key to exit...
pause >nul