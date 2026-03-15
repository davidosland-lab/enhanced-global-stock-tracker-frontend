@echo off
REM ============================================================================
REM RUN_AU_PIPELINE_ONLY.bat - Run AU (ASX) Pipeline Only
REM ============================================================================

REM Change to script directory
cd /d "%~dp0"

echo.
echo ============================================================================
echo  AU (ASX) Pipeline - Australian Market
echo ============================================================================
echo.
echo  This will scan 240 Australian stocks across 8 sectors:
echo    - Financials, Materials, Healthcare, Consumer Staples
echo    - Technology, Energy, Industrials, Real Estate
echo.
echo  Market: ASX (Australian Securities Exchange)
echo  Trading Hours: 10:00-16:00 AEDT
echo.
echo  Output: reports/au_morning_report.json
echo  Estimated time: ~20 minutes
echo.
echo ============================================================================
echo.

set /p confirm="Run AU Pipeline now? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Cancelled
    pause
    exit /b
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo.
    echo [ERROR] Virtual environment not found
    echo [INFO] Please run INSTALL_COMPLETE.bat first
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo.
echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Run AU pipeline
echo.
echo [2/2] Running AU Pipeline...
echo.
cd scripts
python run_au_pipeline_v1.3.13.py --full-scan --ignore-market-hours

if errorlevel 1 (
    echo.
    echo [ERROR] AU Pipeline failed
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ============================================================================
echo  AU Pipeline Complete!
echo ============================================================================
echo.
echo  Report saved to: reports/au_morning_report.json
echo.
echo  Next steps:
echo    - Review the report
echo    - Run US Pipeline: RUN_US_PIPELINE_ONLY.bat
echo    - Run UK Pipeline: RUN_UK_PIPELINE_ONLY.bat
echo    - Or run all: RUN_COMPLETE_WORKFLOW.bat
echo.
echo ============================================================================
echo.
pause
