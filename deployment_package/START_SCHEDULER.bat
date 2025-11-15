@echo off
title ASX Stock Scanner v4.4.4 - Scheduler (Running)
color 0B

echo ================================================================================
echo ASX OVERNIGHT STOCK SCANNER v4.4.4 - Python Scheduler
echo ================================================================================
echo.
echo This runs the Python scheduler that will execute the pipeline at 5:00 AM AEST
echo.
echo Schedule: Daily at 5:00 AM Australia/Sydney timezone
echo Email Reports: Sent to configured recipients after completion
echo.
echo Note: This window must stay open for the scheduler to work.
echo       For automatic startup, use SCHEDULE_PIPELINE.bat instead.
echo.
echo ================================================================================
echo.

REM Check dependencies
echo Checking dependencies...
python -c "import schedule, pytz" 2>nul
if errorlevel 1 (
    echo ERROR: Required packages not installed!
    echo.
    echo Please run: INSTALL_DEPENDENCIES.bat
    echo.
    pause
    exit /b 1
)

echo Dependencies: OK
echo.
echo Starting scheduler...
echo.
echo ================================================================================
echo Press Ctrl+C to stop the scheduler
echo ================================================================================
echo.

REM Run the Python scheduler
python schedule_pipeline.py

echo.
echo ================================================================================
echo Scheduler stopped.
echo ================================================================================
pause
