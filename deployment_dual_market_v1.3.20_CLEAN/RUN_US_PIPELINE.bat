@echo off
REM ============================================================================
REM US Market Screening Pipeline - Direct Execution
REM Based on working ASX v1.3.20 architecture
REM ============================================================================

echo ================================================================================
echo   US MARKET SCREENING PIPELINE
echo   Based on Event Risk Guard v1.3.20 Architecture
echo ================================================================================
echo.
echo This will run the US market screening:
echo   - S&P 500 market sentiment
echo   - HMM regime analysis
echo   - 8 US sectors
echo   - Top opportunities identification
echo.
echo Expected duration: 10-15 minutes
echo.
pause

echo.
echo Starting US pipeline...
python models\screening\us_overnight_pipeline.py

echo.
echo ================================================================================
echo   US PIPELINE COMPLETE
echo ================================================================================
echo.
echo Check results:
echo   - Report: reports\us\YYYY-MM-DD_us_market_report.html
echo   - Data: data\us\
echo   - Logs: logs\screening\us\
echo.
pause
