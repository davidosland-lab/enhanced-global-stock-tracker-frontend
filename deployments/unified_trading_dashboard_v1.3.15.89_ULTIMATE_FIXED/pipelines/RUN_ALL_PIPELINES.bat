@echo off
REM Run ALL Overnight Pipelines (AU + US + UK)
REM Uses shared FinBERT v4.4.4 virtual environment
REM
REM Total Runtime: 50-80 minutes
REM Total Stocks Scanned: 720 (240 per market)
REM Outputs: 3 morning reports (au/us/uk)

chcp 65001 >nul
setlocal EnableDelayedExpansion

set "VENV=%~dp0..\finbert_v4.4.4\venv\Scripts\python.exe"
set "START_TIME=%TIME%"

echo ================================================================================
echo MULTI-MARKET OVERNIGHT PIPELINE v1.3.15.87
echo ================================================================================
echo.
echo Running ALL Markets: Australian + US + UK
echo Total Stocks: 720 (240 per market)
echo Expected Total Runtime: 50-80 minutes
echo.
echo Using FinBERT v4.4.4 shared environment
echo Virtual Environment: %VENV%
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

REM Track failures
set FAILED_MARKETS=
set SUCCESS_COUNT=0
set FAIL_COUNT=0

REM ===============================================================
REM 1. Australian Market
REM ===============================================================
echo.
echo ================================================================================
echo [1/3] AUSTRALIAN MARKET PIPELINE
echo ================================================================================
echo Start Time: %TIME%
echo.

"%VENV%" "%~dp0run_au_pipeline.py" --full-scan --capital 100000 --ignore-market-hours

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Australian pipeline completed
    set /A SUCCESS_COUNT+=1
) else (
    echo [FAILED] Australian pipeline failed - Exit Code: %ERRORLEVEL%
    set FAILED_MARKETS=!FAILED_MARKETS! AU
    set /A FAIL_COUNT+=1
)

REM ===============================================================
REM 2. US Market
REM ===============================================================
echo.
echo ================================================================================
echo [2/3] US MARKET PIPELINE
echo ================================================================================
echo Start Time: %TIME%
echo.

"%VENV%" "%~dp0run_us_pipeline.py" --full-scan --capital 100000 --ignore-market-hours

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] US pipeline completed
    set /A SUCCESS_COUNT+=1
) else (
    echo [FAILED] US pipeline failed - Exit Code: %ERRORLEVEL%
    set FAILED_MARKETS=!FAILED_MARKETS! US
    set /A FAIL_COUNT+=1
)

REM ===============================================================
REM 3. UK Market
REM ===============================================================
echo.
echo ================================================================================
echo [3/3] UK MARKET PIPELINE
echo ================================================================================
echo Start Time: %TIME%
echo.

"%VENV%" "%~dp0run_uk_pipeline.py" --full-scan --capital 100000 --ignore-market-hours

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] UK pipeline completed
    set /A SUCCESS_COUNT+=1
) else (
    echo [FAILED] UK pipeline failed - Exit Code: %ERRORLEVEL%
    set FAILED_MARKETS=!FAILED_MARKETS! UK
    set /A FAIL_COUNT+=1
)

REM ===============================================================
REM Final Summary
REM ===============================================================
echo.
echo ================================================================================
echo MULTI-MARKET PIPELINE SUMMARY
echo ================================================================================
echo.
echo Start Time: %START_TIME%
echo End Time:   %TIME%
echo.
echo Markets Completed: %SUCCESS_COUNT%/3
echo Markets Failed:    %FAIL_COUNT%/3

if %FAIL_COUNT% GTR 0 (
    echo.
    echo FAILED MARKETS:%FAILED_MARKETS%
    echo.
    echo Check logs in:
    echo   - ..\logs\screening\
)

echo.
echo Output Reports:
if %SUCCESS_COUNT% GTR 0 (
    echo   - JSON: ..\reports\screening\{au,us,uk}_morning_report.json
    echo   - CSV:  ..\reports\csv_exports\
)

echo.
echo ================================================================================
if %FAIL_COUNT% EQU 0 (
    echo ALL PIPELINES COMPLETED SUCCESSFULLY
    set EXIT_CODE=0
) else (
    echo SOME PIPELINES FAILED - Review logs above
    set EXIT_CODE=1
)
echo ================================================================================
echo.

pause
exit /b %EXIT_CODE%
