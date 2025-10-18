@echo off
echo =====================================
echo Fixing Yahoo Finance Connection
echo =====================================
echo.
echo This will install the latest yfinance
echo and apply connection fixes...
echo.

python fix_yahoo_connection.py

echo.
echo After this fix, run 2_TEST.bat again
echo.
pause