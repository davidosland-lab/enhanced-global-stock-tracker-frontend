@echo off
:: ============================================================================
:: Event Risk Guard - Run Pipeline in TEST MODE with DEBUG OUTPUT
:: ============================================================================

color 0E
cls

echo.
echo ================================================================================
echo EVENT RISK GUARD - TEST MODE (DEBUG)
echo ================================================================================
echo.
echo This will run the pipeline with FULL ERROR OUTPUT captured.
echo.
echo If the pipeline crashes, you'll see:
echo   - The exact error message
echo   - The line number where it crashed
echo   - The full traceback
echo.
echo The output will be saved to: pipeline_test_debug.log
echo.
echo Press Ctrl+C to cancel
echo.
pause

cd /d "%~dp0"
set LOG_FILE=pipeline_test_debug.log

echo.
echo Starting pipeline in TEST MODE with debug logging...
echo Output will be saved to: %LOG_FILE%
echo.

:: Run with both stdout and stderr captured
cd models\screening
python overnight_pipeline.py --mode test 2>&1 | tee ..\..\%LOG_FILE%

set EXIT_CODE=%errorlevel%

cd ..\..

echo.
echo ================================================================================
if %EXIT_CODE% equ 0 (
    echo TEST COMPLETED SUCCESSFULLY!
    echo ================================================================================
    echo.
    echo Log saved to: %LOG_FILE%
    echo.
    echo Checking for generated HTML report...
    echo.
    
    :: Go back to root and check for reports
    if exist "reports\morning_reports\*_market_report.html" (
        echo [32m[FOUND][0m HTML Report in: reports\morning_reports\
        for %%F in ("reports\morning_reports\*_market_report.html") do (
            echo          File: %%~nxF (%%~zF bytes)
        )
    )
    
    if exist "models\screening\reports\morning_reports\*_market_report.html" (
        echo [32m[FOUND][0m HTML Report in: models\screening\reports\morning_reports\
        for %%F in ("models\screening\reports\morning_reports\*_market_report.html") do (
            echo          File: %%~nxF (%%~zF bytes)
        )
    )
    
    echo.
    echo To view the report in browser, run: START_WEB_UI.bat
    echo.
) else (
    echo TEST FAILED (Exit Code: %EXIT_CODE%)
    echo ================================================================================
    echo.
    echo [31m[ERROR][0m Pipeline crashed or returned error code: %EXIT_CODE%
    echo.
    echo Full output saved to: %LOG_FILE%
    echo.
    echo [33mLAST 50 LINES OF LOG:[0m
    echo ----------------------------------------
    powershell -Command "Get-Content %LOG_FILE% -Tail 50"
    echo ----------------------------------------
    echo.
    echo Check the full log for details: %LOG_FILE%
    echo Look for lines containing: ERROR, Exception, Traceback
    echo.
)

pause
