@echo off
REM ============================================================================
REM Run Pipeline Scheduler in Background (Hidden Console)
REM ============================================================================
REM 
REM Runs the pipeline scheduler without showing a console window
REM Useful for running in the background without interruption
REM
REM Usage:
REM   START_SCHEDULER_BACKGROUND.bat         - All markets
REM   START_SCHEDULER_BACKGROUND.bat UK      - UK only
REM   START_SCHEDULER_BACKGROUND.bat AU,US   - AU and US
REM
REM To stop: taskkill /f /im pythonw.exe
REM View logs: logs\pipeline_scheduler.log
REM
REM ============================================================================

cd /d "%~dp0"

REM Check if already running
tasklist /fi "imagename eq pythonw.exe" /fi "windowtitle eq pipeline_scheduler*" 2>nul | find /i "pythonw.exe" >nul
if not errorlevel 1 (
    echo Pipeline Scheduler is already running
    echo To view logs: type logs\pipeline_scheduler.log
    echo To stop: taskkill /f /im pythonw.exe
    pause
    exit /b 0
)

echo Starting Pipeline Scheduler (background mode)...
echo.

if "%1"=="" (
    REM No arguments - run all markets
    start /b pythonw.exe pipeline_scheduler.py --daemon
) else (
    REM Run specific market(s)
    start /b pythonw.exe pipeline_scheduler.py --daemon --markets %1
)

echo.
echo ✓ Pipeline Scheduler started in background
echo.
echo Logs: logs\pipeline_scheduler.log
echo Stop: taskkill /f /im pythonw.exe
echo.
timeout /t 3 >nul
