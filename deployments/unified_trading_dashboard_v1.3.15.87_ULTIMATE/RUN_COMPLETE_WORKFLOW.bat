@echo off
echo ===============================================
echo ULTIMATE Trading System v1.3.15.87
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

cd scripts

echo.
echo ========================================
echo Stage 1: Running Overnight Pipelines
echo ========================================
echo.

echo Running AU Pipeline...
python run_au_pipeline_v1.3.13.py --full-scan
if errorlevel 1 (
    echo ERROR in AU pipeline
    pause
    exit /b 1
)

echo Running US Pipeline...
python run_us_full_pipeline.py --full-scan
if errorlevel 1 (
    echo ERROR in US pipeline
    pause
    exit /b 1
)

echo Running UK Pipeline...
python run_uk_full_pipeline.py --full-scan
if errorlevel 1 (
    echo ERROR in UK pipeline
    pause
    exit /b 1
)

echo.
echo ========================================
echo Stage 2: Running Enhanced Trading
echo ========================================
echo.

python complete_workflow.py --execute-trades --markets AU,US,UK

echo.
echo ===============================================
echo Complete Workflow Finished
echo Target Performance: 75-85%% Win Rate
echo ===============================================
echo.

pause
