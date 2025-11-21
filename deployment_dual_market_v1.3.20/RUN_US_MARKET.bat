@echo off
REM ============================================================================
REM Run US Market Screening - Full Pipeline (Windows)
REM ============================================================================

echo ================================================================================
echo   US MARKET SCREENING PIPELINE
echo   240 stocks across 8 sectors
echo ================================================================================
echo.
echo This will run the complete US market screening pipeline
echo Expected duration: 15-20 minutes
echo.
pause
echo.

REM Run US market pipeline
python run_screening.py --market us

echo.
echo ================================================================================
echo   US MARKET SCREENING COMPLETE
echo ================================================================================
echo.
echo Outputs:
echo   - Report: reports\us\us_morning_report_*.html
echo   - Data: data\us\us_pipeline_results_*.json
echo   - CSV: data\us\us_opportunities_*.csv
echo   - Logs: logs\screening\us\us_overnight_pipeline.log
echo.
pause
