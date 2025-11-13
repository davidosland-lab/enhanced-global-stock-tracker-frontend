@echo off
REM ===================================================================
REM Schedule Overnight Screener with Windows Task Scheduler
REM Sets up automated execution at 10:00 PM daily
REM ===================================================================

echo ========================================
echo   Schedule Overnight Screener
echo ========================================
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges
    echo Please right-click and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo Setting up Windows Task Scheduler...
echo.

REM Get current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%RUN_OVERNIGHT_SCREENER.bat"

echo Script Location: %SCRIPT_PATH%
echo.

REM Delete existing task if it exists
schtasks /Query /TN "OvernightStockScreener" >nul 2>&1
if %errorLevel% equ 0 (
    echo Removing existing scheduled task...
    schtasks /Delete /TN "OvernightStockScreener" /F
)

REM Create new scheduled task
echo Creating new scheduled task...
echo Task Name: OvernightStockScreener
echo Schedule: Daily at 10:00 PM (22:00)
echo.

schtasks /Create /TN "OvernightStockScreener" ^
    /TR "\"%SCRIPT_PATH%\"" ^
    /SC DAILY ^
    /ST 22:00 ^
    /RU "%USERNAME%" ^
    /RP ^
    /RL HIGHEST ^
    /F

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create scheduled task
    echo Error code: %ERRORLEVEL%
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Scheduled Task Created Successfully!
echo ========================================
echo.
echo Task Name: OvernightStockScreener
echo Run Time: 10:00 PM (22:00) daily
echo User: %USERNAME%
echo.
echo To view the task:
echo   1. Open Task Scheduler (taskschd.msc)
echo   2. Look for "OvernightStockScreener"
echo.
echo To test the task now:
echo   schtasks /Run /TN "OvernightStockScreener"
echo.
echo To disable the task:
echo   schtasks /Change /TN "OvernightStockScreener" /DISABLE
echo.
echo To delete the task:
echo   schtasks /Delete /TN "OvernightStockScreener" /F
echo.

pause
