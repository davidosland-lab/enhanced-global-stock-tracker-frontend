@echo off

REM Change to script directory
cd /d "%~dp0"

echo ===============================================
echo ULTIMATE Trading System v1.3.15.96
echo Target: 75-85%% Win Rate (Two-Stage System)
echo FinBERT v4.4.4: INCLUDED
echo ===============================================
echo.
echo This will run:
echo 1. Overnight pipelines (AU/US/UK)
echo 2. Enhanced live trading with signal adapter
echo.
echo Estimated time: 60 minutes
echo.

set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Cancelled
    pause
    exit /b
)

REM Save the base directory
set BASE_DIR=%CD%

REM Change to scripts directory
cd /d "%BASE_DIR%\scripts"
if errorlevel 1 (
    echo ERROR: Could not find scripts directory
    cd /d "%BASE_DIR%"
    pause
    exit /b 1
)

echo.
echo ========================================
echo Stage 1: Running Overnight Pipelines
echo ========================================
echo.
echo [NOTE] Running with --ignore-market-hours flag
echo        (Allows execution outside trading hours)
echo.

echo Running AU Pipeline...
python run_au_pipeline_v1.3.13.py --full-scan --ignore-market-hours
if errorlevel 1 (
    echo ERROR in AU pipeline
    cd /d "%BASE_DIR%"
    pause
    exit /b 1
)

echo Running US Pipeline...
python run_us_full_pipeline.py --full-scan --ignore-market-hours
if errorlevel 1 (
    echo ERROR in US pipeline
    cd /d "%BASE_DIR%"
    pause
    exit /b 1
)

echo Running UK Pipeline...
python run_uk_full_pipeline.py --full-scan --ignore-market-hours
if errorlevel 1 (
    echo ERROR in UK pipeline
    cd /d "%BASE_DIR%"
    pause
    exit /b 1
)

echo.
echo ========================================
echo Stage 2: Running Enhanced Trading
echo ========================================
echo.

REM Check if complete_workflow.py exists
if exist "complete_workflow.py" (
    python complete_workflow.py --execute-trades --markets AU,US,UK
) else (
    echo [INFO] complete_workflow.py not found - skipping Stage 2
    echo [INFO] Pipelines completed successfully
)

REM Return to base directory
cd /d "%BASE_DIR%"

echo.
echo ===============================================
echo Complete Workflow Finished
echo Target Performance: 75-85%% Win Rate
echo ===============================================
echo.

pause
