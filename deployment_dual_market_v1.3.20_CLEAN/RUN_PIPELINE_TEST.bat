@echo off
:: ============================================================================
:: Event Risk Guard - Run Pipeline in TEST MODE
:: ============================================================================

color 0A
cls

echo.
echo ================================================================================
echo EVENT RISK GUARD - TEST MODE
echo ================================================================================
echo.
echo This will run a QUICK TEST with reduced scope:
echo   - Processes only 10 stocks (vs 240 in full mode)
echo   - Trains 10 LSTM models (vs 100 in full mode)
echo   - Skips some non-critical checks
echo.
echo ESTIMATED TIME: 15-20 minutes
echo.
echo Perfect for:
echo   - Verifying installation
echo   - Testing after changes
echo   - Quick validation
echo.
echo Press Ctrl+C to cancel
echo.
pause

cd /d "%~dp0"
cd models\screening

echo.
echo Starting pipeline in TEST MODE...
echo.

python overnight_pipeline.py --mode test

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo TEST COMPLETED SUCCESSFULLY!
    echo ================================================================================
    echo.
    echo Checking for generated HTML report...
    echo.
    
    :: Check for today's HTML report in multiple locations
    set FOUND_REPORT=0
    
    for %%D in (reports\morning_reports models\screening\reports\morning_reports) do (
        if exist "%%D\*_market_report.html" (
            echo [32m[FOUND][0m HTML Report: %%D\
            for %%F in ("%%D\*_market_report.html") do (
                echo          File: %%~nxF (%%~zF bytes)
            )
            set FOUND_REPORT=1
        )
    )
    
    if %FOUND_REPORT%==0 (
        echo [33m[WARNING][0m No HTML report found in expected locations
        echo             Check: reports\morning_reports\ or models\screening\reports\morning_reports\
    )
    
    echo.
    echo Next steps:
    echo   1. Review logs: models\screening\logs\overnight_screening_YYYYMMDD.log
    echo   2. Check HTML report: reports\morning_reports\YYYY-MM-DD_market_report.html
    echo   3. Check results: results\overnight_screening_results_YYYYMMDD.csv
    echo   4. Look for:
    echo      - Market Regime Engine output
    echo      - PHASE 4.5: LSTM MODEL TRAINING
    echo      - Sentiment analysis with article counts
    echo      - LSTM training success rate
    echo.
    echo To view the report in browser, run: START_WEB_UI.bat
    echo If test passes, run full pipeline: RUN_PIPELINE.bat
    echo.
) else (
    echo.
    echo ================================================================================
    echo TEST FAILED
    echo ================================================================================
    echo.
    echo Check logs for details: models\screening\logs\
    echo.
)

pause
