@echo off
REM Run Australian Market Overnight Pipeline
REM Uses shared FinBERT v4.4.4 virtual environment
REM
REM Expected Runtime: 15-25 minutes
REM Stocks Scanned: 240 (8 sectors x 30 stocks)
REM Output: reports/screening/au_morning_report.json

chcp 65001 >nul
setlocal EnableDelayedExpansion

set "VENV=%~dp0..\finbert_v4.4.4\venv\Scripts\python.exe"
set "SCRIPT=%~dp0run_au_pipeline.py"

echo ================================================================================
echo AUSTRALIAN MARKET OVERNIGHT PIPELINE v1.3.15.87
echo ================================================================================
echo.
echo Using FinBERT v4.4.4 shared environment
echo Virtual Environment: %VENV%
echo Script: %SCRIPT%
echo.
echo Expected Runtime: 15-25 minutes
echo Stocks to Scan: 240 (8 sectors)
echo.
echo ================================================================================
echo.

REM Check if venv exists
if not exist "%VENV%" (
    echo [ERROR] FinBERT venv not found at: %VENV%
    echo.
    echo Please install the environment first:
    echo   cd ..\finbert_v4.4.4
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Create required directories
echo Ensuring directories exist...
if not exist "..\logs\screening" mkdir "..\logs\screening"
if not exist "..\logs\screening\errors" mkdir "..\logs\screening\errors"
if not exist "..\reports\screening" mkdir "..\reports\screening"
if not exist "..\reports\csv_exports" mkdir "..\reports\csv_exports"
if not exist "..\data\au" mkdir "..\data\au"
echo.

REM Run pipeline
echo Starting Australian market pipeline...
echo.

"%VENV%" "%SCRIPT%" --full-scan --capital 100000 --ignore-market-hours

set EXIT_CODE=%ERRORLEVEL%

echo.
echo ================================================================================
if %EXIT_CODE% EQU 0 (
    echo PIPELINE COMPLETED SUCCESSFULLY
    echo.
    echo Output Reports:
    echo   - JSON: ..\reports\screening\au_morning_report.json
    echo   - CSV:  ..\reports\csv_exports\au_screening_results_*.csv
    echo   - Logs: ..\logs\screening\overnight_pipeline.log
) else (
    echo PIPELINE FAILED - Exit Code: %EXIT_CODE%
    echo.
    echo Check logs for details:
    echo   - ..\logs\screening\overnight_pipeline.log
    echo   - ..\logs\screening\errors\
)
echo ================================================================================
echo.

pause
exit /b %EXIT_CODE%
