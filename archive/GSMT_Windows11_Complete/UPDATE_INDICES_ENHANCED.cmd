@echo off
cls
color 0A
title GSMT - Global Indices Tracker Update v2.0

echo =========================================
echo  GSMT - Global Indices Tracker Update
echo  Version 2.0 - Percentage Changes View
echo =========================================
echo.

echo Updating Global Indices Tracker...
echo.

REM Check if the frontend directory exists
if not exist "frontend" (
    echo ERROR: Frontend directory not found!
    echo Please run this update from the GSMT installation directory.
    pause
    exit /b 1
)

REM Backup the old tracker if it exists
if exist "frontend\indices_tracker_unified.html" (
    echo Creating backup of existing tracker...
    copy /Y "frontend\indices_tracker_unified.html" "frontend\indices_tracker_unified.backup.html" >nul 2>&1
)

REM The new file is already in place as indices_tracker_percentage.html
echo Installing enhanced indices tracker with:
echo  - Percentage changes on Y-axis
echo  - Regional market selection (Asia, Europe, Americas)
echo  - Real-time data fetching from Yahoo Finance
echo  - Improved visual design and performance
echo.

REM Update the main dashboard to use the new tracker
echo Updating main dashboard link...
if exist "frontend\dashboard.html" (
    powershell -Command "(Get-Content 'frontend\dashboard.html') -replace 'indices_tracker_unified.html', 'indices_tracker_percentage.html' | Set-Content 'frontend\dashboard.html'"
)

echo.
echo =========================================
echo  Update Complete!
echo =========================================
echo.
echo The Global Indices Tracker has been updated with:
echo.
echo 1. Y-axis now shows percentage change from previous close
echo 2. Regional market selection buttons (Asia, Europe, Americas)
echo 3. Enhanced market cards with status indicators
echo 4. Real-time statistics display
echo 5. Improved chart visualization
echo.
echo To use the updated tracker:
echo 1. Run RUN_GSMT.cmd to start the application
echo 2. Navigate to the Global Indices Tracker
echo 3. Select your region (Asia, Europe, or Americas)
echo 4. Choose markets to track
echo 5. View percentage changes in real-time
echo.
echo Press any key to exit...
pause >nul