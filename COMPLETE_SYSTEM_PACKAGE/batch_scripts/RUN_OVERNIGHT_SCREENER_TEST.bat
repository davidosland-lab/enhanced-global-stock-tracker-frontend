@echo off
REM ===================================================================
REM Overnight Stock Screener - TEST MODE
REM Quick test with limited stocks (Financials only, 5 stocks)
REM ===================================================================

echo ========================================
echo   Overnight Screener - TEST MODE
echo ========================================
echo Start Time: %TIME%
echo.

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found
)

REM Create logs directory
if not exist "logs\screening" mkdir "logs\screening"

REM Run in test mode
echo.
echo Running in TEST MODE...
echo Sector: Financials only
echo Stocks: 5
echo.

python -u models/screening/overnight_pipeline.py --mode test

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] Test failed with error code %ERRORLEVEL%
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Test Complete!
echo ========================================
echo End Time: %TIME%
echo.
echo Check: reports\morning_reports\
echo.

pause
