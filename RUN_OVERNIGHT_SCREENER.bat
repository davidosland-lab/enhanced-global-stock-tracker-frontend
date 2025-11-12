@echo off
REM ===================================================================
REM Overnight Stock Screener - Main Execution Script
REM Runs: 10:00 PM - 7:00 AM AEST
REM ===================================================================

echo ========================================
echo   Overnight Stock Screener Starting
echo ========================================
echo Start Time: %TIME%
echo Date: %DATE%
echo.

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found
    echo Continuing with system Python...
)

REM Create logs directory if it doesn't exist
if not exist "logs\screening" mkdir "logs\screening"

REM Run the overnight screener
echo.
echo Running stock screening pipeline...
echo Mode: FULL (all sectors, 30 stocks each)
echo.

python -u models/screening/overnight_pipeline.py --mode full --stocks-per-sector 30

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] Screener failed with error code %ERRORLEVEL%
    echo Check logs\screening\overnight_pipeline.log for details
    echo.
    
    REM Send error notification (if email module exists)
    if exist "models\screening\send_notification.py" (
        echo Sending error notification...
        python models\screening\send_notification.py --type error --code %ERRORLEVEL%
    )
    
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Screening Complete!
echo ========================================
echo End Time: %TIME%
echo.
echo Report generated in: reports\morning_reports
echo Latest report: reports\morning_reports\%DATE:~-4%-%DATE:~4,2%-%DATE:~7,2%_market_report.html
echo.

REM Send success notification (if email module exists)
if exist "models\screening\send_notification.py" (
    echo Sending success notification...
    python models\screening\send_notification.py --type success
)

echo Press any key to exit...
pause > nul
