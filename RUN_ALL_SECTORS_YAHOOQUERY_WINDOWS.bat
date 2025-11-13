@echo off
chcp 65001 >nul 2>&1
echo ================================================================================
echo FINBERT v4.4.4 - FULL MARKET SCAN (yahooquery ONLY)
echo Windows-Compatible Version (ASCII symbols)
echo ================================================================================
echo.
echo Data Source: yahooquery ONLY
echo NO yfinance, NO Alpha Vantage
echo.
echo This will scan ALL ASX sectors (may take 5-10 minutes)
echo Results will be saved to: screener_results_yahooquery_[timestamp].csv
echo.
echo ================================================================================
echo.
pause

echo Starting full market scan...
echo.

python run_all_sectors_yahooquery_WINDOWS.py

echo.
echo ================================================================================
echo Scan complete! Check the CSV file for results.
echo ================================================================================
echo.
pause
