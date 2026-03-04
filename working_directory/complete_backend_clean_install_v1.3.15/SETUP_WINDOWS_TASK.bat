@echo off
REM ============================================================================
REM Setup Windows Task Scheduler - Pipeline Scheduler
REM ============================================================================
REM 
REM Creates a Windows Task Scheduler task to run the pipeline scheduler
REM automatically at system startup (runs in background)
REM
REM Run as Administrator for best results
REM
REM ============================================================================

echo ================================================================================
echo WINDOWS TASK SCHEDULER SETUP
echo ================================================================================
echo.
echo This will create a scheduled task to run the Pipeline Scheduler
echo automatically when your computer starts.
echo.
echo The scheduler will run in the background and execute:
echo   - AU Pipeline at 07:30 AEDT (before 10:00 market open)
echo   - US Pipeline at 07:00 EST  (before 09:30 market open)
echo   - UK Pipeline at 05:30 GMT  (before 08:00 market open)
echo.
echo ================================================================================
echo.

REM Get current directory
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Task name
set TASK_NAME=PipelineScheduler_AutoTrading

echo Creating scheduled task: %TASK_NAME%
echo Script location: %SCRIPT_DIR%
echo.

REM Check if task already exists
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo WARNING: Task "%TASK_NAME%" already exists
    echo.
    choice /c YN /m "Do you want to delete and recreate it"
    if errorlevel 2 goto :EOF
    
    echo Deleting existing task...
    schtasks /delete /tn "%TASK_NAME%" /f
    if errorlevel 1 (
        echo ERROR: Failed to delete existing task
        pause
        exit /b 1
    )
)

REM Create the task
echo.
echo Creating task...
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "pythonw.exe \"%SCRIPT_DIR%\pipeline_scheduler.py\" --daemon" ^
    /sc onstart ^
    /rl highest ^
    /f

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo ERROR: Failed to create scheduled task
    echo ================================================================================
    echo.
    echo Try running this script as Administrator:
    echo   1. Right-click START_PIPELINE_SCHEDULER.bat
    echo   2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SUCCESS: Scheduled task created successfully!
echo ================================================================================
echo.
echo Task Name: %TASK_NAME%
echo Trigger:   At system startup
echo Action:    Run Pipeline Scheduler (background)
echo.
echo The scheduler will now run automatically when Windows starts.
echo.
echo Management:
echo   - View task:   Task Scheduler (taskschd.msc)
echo   - Start now:   schtasks /run /tn "%TASK_NAME%"
echo   - Stop:        taskkill /f /im pythonw.exe
echo   - Remove:      schtasks /delete /tn "%TASK_NAME%" /f
echo.
echo Logs: %SCRIPT_DIR%\logs\pipeline_scheduler.log
echo.
echo ================================================================================
echo.

choice /c YN /m "Do you want to start the scheduler now"
if errorlevel 2 goto :end

echo.
echo Starting scheduler...
schtasks /run /tn "%TASK_NAME%"

if errorlevel 1 (
    echo ERROR: Failed to start task
) else (
    echo.
    echo ✓ Scheduler started successfully
    echo.
    echo The scheduler is now running in the background.
    echo Check logs\pipeline_scheduler.log for activity.
)

:end
echo.
echo ================================================================================
pause
