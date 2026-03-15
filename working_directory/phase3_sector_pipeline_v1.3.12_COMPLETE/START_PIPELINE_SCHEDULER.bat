@echo off
REM ============================================================================
REM Pipeline Scheduler - Windows Service Startup
REM ============================================================================
REM 
REM Automatically runs overnight pipeline reports 2.5 hours before market open
REM
REM Market Schedule:
REM   AU (ASX):   Market opens 10:00 AEDT -> Pipeline runs 07:30 AEDT
REM   US (NYSE):  Market opens 09:30 EST  -> Pipeline runs 07:00 EST
REM   UK (LSE):   Market opens 08:00 GMT  -> Pipeline runs 05:30 GMT
REM
REM Usage:
REM   START_PIPELINE_SCHEDULER.bat           - Run all markets
REM   START_PIPELINE_SCHEDULER.bat UK        - Run UK only
REM   START_PIPELINE_SCHEDULER.bat AU,US,UK  - Run specific markets
REM
REM ============================================================================

echo ================================================================================
echo PIPELINE SCHEDULER - Starting Service
echo ================================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.8+ or add it to your PATH
    pause
    exit /b 1
)

REM Check if schedule package is installed
python -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo Installing required package: schedule
    pip install schedule
    if errorlevel 1 (
        echo ERROR: Failed to install schedule package
        pause
        exit /b 1
    )
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo.
echo Starting Pipeline Scheduler...
echo.
echo Markets monitored:
echo   - Australia (AU):     Pipeline runs at 07:30 AEDT
echo   - United States (US): Pipeline runs at 07:00 EST
echo   - UK (UK):            Pipeline runs at 05:30 GMT
echo.
echo Press Ctrl+C to stop the scheduler
echo.
echo Logs: logs\pipeline_scheduler.log
echo ================================================================================
echo.

REM Run scheduler as daemon
if "%1"=="" (
    REM No arguments - run all markets
    python pipeline_scheduler.py --daemon
) else (
    REM Run specific market(s)
    python pipeline_scheduler.py --daemon --markets %1
)

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo ERROR: Scheduler failed to start
    echo ================================================================================
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Scheduler stopped
echo ================================================================================
pause
