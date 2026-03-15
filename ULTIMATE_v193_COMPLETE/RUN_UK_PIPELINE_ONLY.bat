@echo off
REM ============================================================================
REM RUN_UK_PIPELINE_ONLY.bat - Run UK (LSE) Pipeline Only
REM ============================================================================

REM Change to script directory
cd /d "%~dp0"

echo.
echo ============================================================================
echo  UK (LSE) Pipeline - London Stock Exchange
echo ============================================================================
echo.
echo  This will scan 240 UK stocks across 8 sectors:
echo    - Financials, Materials, Healthcare, Consumer Discretionary
echo    - Technology, Energy, Industrials, Utilities
echo.
echo  Market: LSE (London Stock Exchange)
echo  Trading Hours: 8:00-16:30 GMT
echo.
echo  Output: reports/uk_morning_report.json
echo  Estimated time: ~20 minutes
echo.
echo ============================================================================
echo.

set /p confirm="Run UK Pipeline now? (Y/N): "
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

REM Run UK pipeline
echo.
echo [2/2] Running UK Pipeline...
echo.
cd scripts
python run_uk_full_pipeline.py --full-scan --ignore-market-hours

if errorlevel 1 (
    echo.
    echo [ERROR] UK Pipeline failed
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ============================================================================
echo  UK Pipeline Complete!
echo ============================================================================
echo.
echo  Report saved to: reports/uk_morning_report.json
echo.
echo  Next steps:
echo    - Review the report
echo    - Run AU Pipeline: RUN_AU_PIPELINE_ONLY.bat
echo    - Run US Pipeline: RUN_US_PIPELINE_ONLY.bat
echo    - Or run all: RUN_COMPLETE_WORKFLOW.bat
echo.
echo ============================================================================
echo.
pause
