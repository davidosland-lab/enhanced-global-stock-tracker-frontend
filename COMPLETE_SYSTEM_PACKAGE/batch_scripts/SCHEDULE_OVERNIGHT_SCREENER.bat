@echo off
REM ============================================================================
REM Schedule Overnight Stock Screener - Windows Task Scheduler Setup
REM 
REM This script sets up Windows Task Scheduler to run the overnight screener
REM automatically at 10:00 PM every night.
REM 
REM Requirements:
REM   - Run as Administrator
REM   - Python must be installed and in PATH
REM 
REM ============================================================================

echo.
echo ================================================================================
echo        SCHEDULE OVERNIGHT STOCK SCREENER - Windows Task Scheduler Setup
echo ================================================================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if errorlevel 1 (
    echo ERROR: This script must be run as Administrator
    echo.
    echo Right-click on this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Get full path to batch script
set BATCH_PATH=%SCRIPT_DIR%RUN_OVERNIGHT_SCREENER.bat

echo Task Configuration:
echo -------------------
echo Task Name: OvernightStockScreener
echo Schedule: Daily at 10:00 PM (22:00)
echo Script Path: %BATCH_PATH%
echo.

set /p CONFIRM="Create this scheduled task? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo.
    echo Task creation cancelled.
    pause
    exit /b 0
)

echo.
echo Creating scheduled task...
echo.

REM Create the scheduled task
schtasks /Create /TN "OvernightStockScreener" /TR "\"%BATCH_PATH%\"" /SC DAILY /ST 22:00 /RU "%USERNAME%" /F

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create scheduled task
    echo.
    echo Make sure you are running as Administrator
    pause
    exit /b 1
) else (
    echo.
    echo ================================================================================
    echo SCHEDULED TASK CREATED SUCCESSFULLY
    echo ================================================================================
    echo.
    echo Task Name: OvernightStockScreener
    echo Schedule: Every day at 10:00 PM (22:00)
    echo Status: Enabled
    echo.
    echo The overnight screener will now run automatically every night at 10 PM.
    echo.
    echo To manage the task:
    echo   - Open Task Scheduler (taskschd.msc)
    echo   - Look for "OvernightStockScreener" in the Task Scheduler Library
    echo.
    echo To disable the task:
    echo   schtasks /Change /TN "OvernightStockScreener" /DISABLE
    echo.
    echo To enable the task:
    echo   schtasks /Change /TN "OvernightStockScreener" /ENABLE
    echo.
    echo To delete the task:
    echo   schtasks /Delete /TN "OvernightStockScreener" /F
    echo.
    
    REM Ask if user wants to test run
    set /p TEST_RUN="Run a test now? (y/n): "
    if /i "%TEST_RUN%"=="y" (
        echo.
        echo Running test screener (5 stocks per sector)...
        echo.
        call "%BATCH_PATH%" test
    )
)

echo.
pause
