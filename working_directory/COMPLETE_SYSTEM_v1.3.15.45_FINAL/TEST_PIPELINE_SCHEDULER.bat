@echo off
REM ============================================================================
REM Test Pipeline Scheduler - No Execution
REM ============================================================================
REM 
REM Tests the pipeline scheduler configuration without executing pipelines
REM Shows when each market's pipeline will run next
REM
REM ============================================================================

echo ================================================================================
echo PIPELINE SCHEDULER - Test Mode (No Execution)
echo ================================================================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Check schedule package
python -c "import schedule" >nul 2>&1
if errorlevel 1 (
    echo Installing schedule package...
    pip install schedule
)

echo Running scheduler test...
echo.

python pipeline_scheduler.py --test

echo.
echo ================================================================================
echo Test complete
echo ================================================================================
pause
