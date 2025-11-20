@echo off
REM Event Risk Guard - Run Overnight Pipeline
REM Executes the complete overnight screening with Event Risk Guard

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ================================================================================
echo Event Risk Guard - Overnight Screening Pipeline
echo ================================================================================
echo.
echo Starting overnight pipeline with Event Risk Guard enabled...
echo.
echo Pipeline phases:
echo   1. Market Sentiment Analysis (SPI 200)
echo   2. Stock Scanning (ASX stocks)
echo   3. Event Risk Assessment (Basel III, earnings, dividends)
echo   4. Prediction Generation (LSTM + FinBERT)
echo   5. Opportunity Scoring
echo   6. Report Generation + CSV Export
echo.
echo Reports will be saved to:
echo   - reports/html/ (HTML reports)
echo   - reports/csv/ (CSV exports with event risk data)
echo.

python models/screening/overnight_pipeline.py

echo.
echo ================================================================================
echo Pipeline Complete!
echo ================================================================================
echo.
echo Check the following directories:
echo   reports/html/ - HTML morning reports
echo   reports/csv/ - CSV exports (full results + event risk summary)
echo   logs/screening/ - Execution logs
echo.
pause
