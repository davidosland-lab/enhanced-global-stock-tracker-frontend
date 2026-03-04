@echo off
REM ============================================================================
REM Run Pipeline Reports Once - Manual Execution
REM ============================================================================
REM 
REM Manually runs pipeline reports for all or specific markets
REM Useful for testing or running outside of scheduled times
REM
REM Usage:
REM   RUN_PIPELINES_ONCE.bat        - Run all markets
REM   RUN_PIPELINES_ONCE.bat UK     - Run UK only
REM   RUN_PIPELINES_ONCE.bat AU,US  - Run AU and US
REM
REM ============================================================================

echo ================================================================================
echo PIPELINE REPORTS - Manual Execution
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

if "%1"=="" (
    echo Running all market pipelines...
    python pipeline_scheduler.py --once
) else (
    echo Running pipelines for: %1
    python pipeline_scheduler.py --once --markets %1
)

echo.
echo ================================================================================
echo Execution complete
echo ================================================================================
pause
