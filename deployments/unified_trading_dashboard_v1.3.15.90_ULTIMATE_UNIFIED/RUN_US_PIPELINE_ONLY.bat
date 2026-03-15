@echo off
REM ============================================================================
REM RUN_US_PIPELINE_ONLY.bat - Run US Pipeline Only
REM ============================================================================

REM Change to script directory
cd /d "%~dp0"

echo.
echo ============================================================================
echo  US Pipeline - American Markets
echo ============================================================================
echo.
echo  This will scan 240 US stocks across major sectors:
echo    - NYSE and NASDAQ listed stocks
echo    - Technology, Healthcare, Finance, Energy, etc.
echo.
echo  Market: NYSE/NASDAQ
echo  Trading Hours: 9:30-16:00 EST
echo.
echo  Output: reports/us_morning_report.json
echo  Estimated time: ~20 minutes
echo.
echo ============================================================================
echo.

set /p confirm="Run US Pipeline now? (Y/N): "
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

REM Run US pipeline
echo.
echo [2/2] Running US Pipeline...
echo.
cd scripts
python run_us_full_pipeline.py --full-scan --ignore-market-hours

if errorlevel 1 (
    echo.
    echo [ERROR] US Pipeline failed
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ============================================================================
echo  US Pipeline Complete!
echo ============================================================================
echo.
echo  Report saved to: reports/us_morning_report.json
echo.
echo  Next steps:
echo    - Review the report
echo    - Run AU Pipeline: RUN_AU_PIPELINE_ONLY.bat
echo    - Run UK Pipeline: RUN_UK_PIPELINE_ONLY.bat
echo    - Or run all: RUN_COMPLETE_WORKFLOW.bat
echo.
echo ============================================================================
echo.
pause
