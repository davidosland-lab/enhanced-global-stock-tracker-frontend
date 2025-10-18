@echo off
echo =====================================
echo Fixing Yahoo Finance Connection
echo =====================================
echo.
echo This will try multiple methods to fix
echo the Yahoo Finance connection issue.
echo.

python fix_yfinance.py

echo.
echo =====================================
echo After running this fix:
echo 1. Run 4_quick_test.bat to verify
echo 2. If working, run 3_start_server.bat
echo =====================================
pause