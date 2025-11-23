@echo off
:: ============================================================================
:: Run ASX Pipeline Directly (matches working v1.3.20 pattern)
:: ============================================================================

color 0A
cls

echo.
echo ================================================================================
echo ASX OVERNIGHT STOCK SCREENING (Direct Execution)
echo ================================================================================
echo.
echo This will run the ASX overnight screening pipeline directly:
echo   1. Market Regime Detection (ASX 200)
echo   2. Stock Screening and Scoring (240 stocks)
echo   3. Event Risk Assessment
echo   4. FinBERT Sentiment Analysis (optional)
echo   5. LSTM Predictions (optional)
echo   6. Report Generation
echo.
echo ESTIMATED TIME: 15-20 minutes
echo.
echo Press Ctrl+C to cancel
echo.
pause

cd /d "%~dp0"
cd models\screening

echo.
echo Starting ASX pipeline...
echo.

python overnight_pipeline.py

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo ASX PIPELINE COMPLETED SUCCESSFULLY!
    echo ================================================================================
    echo.
    echo Reports saved to: ..\..\reports\morning_reports\
    echo Logs saved to: ..\..\logs\screening\
    echo.
) else (
    echo.
    echo ================================================================================
    echo ASX PIPELINE FAILED
    echo ================================================================================
    echo.
    echo Check logs for details: ..\..\logs\screening\
    echo.
)

pause
