@echo off
title ASX Stock Scanner v4.4.4 - Schedule Setup
color 0E

REM ============================================================================
REM Schedule Overnight Pipeline with Windows Task Scheduler
REM Sets up automated execution at 5:00 AM AEST/AEDT daily
REM ============================================================================

echo.
echo ================================================================================
echo        ASX STOCK SCANNER v4.4.4 - Windows Task Scheduler Setup
echo ================================================================================
echo.
echo This will set up Windows Task Scheduler to run the overnight pipeline
echo automatically at 5:00 AM AEST/AEDT every day.
echo.
echo Features:
echo   - Automatic daily execution
echo   - Email notifications with reports
echo   - Error notifications if pipeline fails
echo   - Full LSTM + FinBERT predictions
echo   - 240 ASX stocks analyzed
echo.
echo ================================================================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] This script must be run as Administrator
    echo.
    echo Right-click on this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [1/6] Checking administrator privileges... OK
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [2/6] Script location: %SCRIPT_DIR%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    echo.
    pause
    exit /b 1
)

echo [3/6] Python version:
python --version
echo.

REM Check required packages
echo [4/6] Checking required packages...
python -c "import yahooquery, pandas, numpy, yfinance, pytz, schedule" 2>nul
if errorlevel 1 (
    echo [ERROR] Required packages not installed!
    echo.
    echo Please run INSTALL_DEPENDENCIES.bat first
    echo.
    pause
    exit /b 1
)
echo Required packages: OK
echo.

REM Get full path to batch script
set "BATCH_PATH=%SCRIPT_DIR%RUN_OVERNIGHT_PIPELINE.bat"

echo [5/6] Task Configuration:
echo ================================================================================
echo Task Name:     ASX_OvernightScanner
echo Schedule:      Daily at 5:00 AM (05:00)
echo Script:        %BATCH_PATH%
echo User:          %USERNAME%
echo Priority:      High
echo.
echo Reports will be emailed to:
echo   - finbert_morning_report@proton.me
echo   - david.osland@gmail.com
echo ================================================================================
echo.

set /p CONFIRM="Create this scheduled task? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo.
    echo Task creation cancelled.
    pause
    exit /b 0
)

echo.
echo [6/6] Creating scheduled task...
echo.

REM Delete existing task if it exists
schtasks /Query /TN "ASX_OvernightScanner" >nul 2>&1
if errorlevel 0 (
    echo Removing existing task...
    schtasks /Delete /TN "ASX_OvernightScanner" /F >nul 2>&1
)

REM Create the scheduled task
schtasks /Create /TN "ASX_OvernightScanner" ^
    /TR "\"%BATCH_PATH%\"" ^
    /SC DAILY ^
    /ST 05:00 ^
    /RU "%USERNAME%" ^
    /RL HIGHEST ^
    /F

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo [ERROR] Failed to create scheduled task
    echo ================================================================================
    echo.
    echo Troubleshooting:
    echo   1. Make sure you are running as Administrator
    echo   2. Check if Task Scheduler service is running
    echo   3. Try: services.msc and verify "Task Scheduler" is started
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo [SUCCESS] Scheduled Task Created Successfully!
echo ================================================================================
echo.
echo Task Details:
echo   Name:      ASX_OvernightScanner
echo   Schedule:  Every day at 5:00 AM (05:00 AEST/AEDT)
echo   Status:    Enabled
echo   Priority:  High
echo.
echo The overnight scanner will now run automatically every morning.
echo.
echo ================================================================================
echo Task Management Commands:
echo ================================================================================
echo.
echo View task in Task Scheduler:
echo   1. Press Win+R
echo   2. Type: taskschd.msc
echo   3. Look for "ASX_OvernightScanner"
echo.
echo Run task immediately (test):
echo   schtasks /Run /TN "ASX_OvernightScanner"
echo.
echo Disable task:
echo   schtasks /Change /TN "ASX_OvernightScanner" /DISABLE
echo.
echo Enable task:
echo   schtasks /Change /TN "ASX_OvernightScanner" /ENABLE
echo.
echo Delete task:
echo   schtasks /Delete /TN "ASX_OvernightScanner" /F
echo.
echo View task info:
echo   schtasks /Query /TN "ASX_OvernightScanner" /V /FO LIST
echo.
echo ================================================================================
echo.

REM Ask if user wants to test run
set /p TEST_RUN="Run a test now (5 stocks per sector)? (Y/N): "
if /i "%TEST_RUN%"=="Y" (
    echo.
    echo Running test pipeline...
    echo.
    call "%BATCH_PATH%" test
)

echo.
echo ================================================================================
echo Setup Complete!
echo ================================================================================
echo.
echo Next Steps:
echo   1. Verify Gmail App Password is configured (screening_config.json line 90)
echo   2. Check Task Scheduler to confirm task is active
echo   3. Wait for 5:00 AM tomorrow, or run test immediately
echo   4. Check email for morning report delivery
echo.
echo Logs Location: logs\scheduler\scheduler.log
echo Reports Location: reports\morning_reports\
echo.
pause
