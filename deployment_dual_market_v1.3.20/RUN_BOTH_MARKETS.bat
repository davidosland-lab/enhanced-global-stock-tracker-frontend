@echo off
REM ============================================================================
REM Run Both Markets - ASX + US (Parallel) - Windows
REM ============================================================================

echo ================================================================================
echo   DUAL MARKET SCREENING - ASX + US
echo   480 stocks total (240 ASX + 240 US)
echo ================================================================================
echo.
echo This will run both ASX and US pipelines in PARALLEL
echo Expected duration: 20-25 minutes
echo.
pause
echo.

REM Run both markets in parallel
python run_screening.py --market both --parallel

echo.
echo ================================================================================
echo   DUAL MARKET SCREENING COMPLETE
echo ================================================================================
echo.
echo ASX Outputs:
echo   - Report: reports\morning_report_*.html
echo   - Data: data\pipeline_results_*.json
echo   - Logs: logs\screening\overnight_pipeline.log
echo.
echo US Outputs:
echo   - Report: reports\us\us_morning_report_*.html
echo   - Data: data\us\us_pipeline_results_*.json
echo   - Logs: logs\screening\us\us_overnight_pipeline.log
echo.
pause
