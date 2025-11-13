@echo off
echo ================================================================================
echo   Financial Sector Test Screener - yahooquery ONLY
echo   NO yfinance, NO Alpha Vantage
echo ================================================================================
echo.
echo This script will:
echo   1. Test market sentiment calculation
echo   2. Screen Financial sector stocks (CBA, WBC, NAB, ANZ, MQG)
echo   3. Generate results CSV
echo.
echo Press any key to start or Ctrl+C to cancel...
pause > nul
echo.

python test_financial_screener_yahooquery.py

echo.
echo ================================================================================
echo   Test Complete!
echo ================================================================================
echo.
echo Check the output above for results.
echo Results saved to: financial_sector_results_yahooquery.csv
echo.
pause
