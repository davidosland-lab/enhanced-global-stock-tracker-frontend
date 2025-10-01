@echo off
cls
color 0C
title GSMT - Remove ALL Demo Data Update

echo ================================================
echo  GSMT - CRITICAL UPDATE
echo  Removing ALL Demo/Synthetic Data
echo  Installing Live Data Only Version
echo ================================================
echo.

echo This update will:
echo - Remove ALL demo/synthetic data generation
echo - Install live-only market tracker
echo - Configure backend for Yahoo Finance only
echo - No fallback to fake data
echo.

echo Press any key to continue with update...
pause >nul

echo.
echo Step 1: Backing up current configuration...
if not exist backup_before_live mkdir backup_before_live
copy /Y "frontend\indices_tracker_percentage.html" "backup_before_live\indices_tracker_percentage_old.html" 2>nul
copy /Y "backend\market_data_server.py" "backup_before_live\market_data_server_old.py" 2>nul

echo.
echo Step 2: Installing live-only tracker...
copy /Y "frontend\indices_tracker_live_only.html" "frontend\indices_tracker_percentage.html"

echo.
echo Step 3: Updating launcher scripts...
echo Updated to use live_market_server.py

echo.
echo Step 4: Stopping any existing demo servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)

echo.
echo ================================================
echo  UPDATE COMPLETE - DEMO DATA REMOVED
echo ================================================
echo.
echo IMPORTANT: 
echo - The tracker now uses ONLY real Yahoo Finance data
echo - No demo/synthetic data will be generated
echo - If backend is unavailable, you'll see connection errors
echo - This is intentional - no fake data fallback
echo.
echo To start the tracker:
echo 1. Run START_LIVE_BACKEND.cmd first (for real data)
echo 2. Then run LAUNCH_INDICES_TRACKER.cmd
echo.
echo Press any key to exit...
pause >nul