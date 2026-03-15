@echo off
REM ============================================================================
REM Stop Pipeline Scheduler
REM ============================================================================
REM 
REM Stops the pipeline scheduler if running in background
REM
REM ============================================================================

echo ================================================================================
echo STOPPING PIPELINE SCHEDULER
echo ================================================================================
echo.

REM Check if running
tasklist /fi "imagename eq pythonw.exe" 2>nul | find /i "pythonw.exe" >nul
if errorlevel 1 (
    tasklist /fi "imagename eq python.exe" 2>nul | find /i "pipeline_scheduler" >nul
    if errorlevel 1 (
        echo Pipeline Scheduler is not running
        echo.
        pause
        exit /b 0
    )
)

echo Stopping scheduler...
taskkill /f /im pythonw.exe >nul 2>&1
taskkill /f /fi "windowtitle eq *pipeline_scheduler*" >nul 2>&1

echo.
echo ✓ Pipeline Scheduler stopped
echo.
echo Check logs\pipeline_scheduler.log for execution history
echo.
pause
