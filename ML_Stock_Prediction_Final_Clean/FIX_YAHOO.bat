@echo off
echo ============================================================
echo FIXING Yahoo Finance "Expecting value" Error
echo ============================================================
echo.
echo The issue: yfinance needs curl_cffi but it's not installed
echo.
echo Installing curl_cffi now...
echo.

pip install curl_cffi

echo.
echo Testing the fix...
echo.

python diagnose_yahoo.py

echo.
echo ============================================================
echo If you see "SUCCESS" above, Yahoo Finance is now working!
echo If not, try:
echo   1. Close this window
echo   2. Open a NEW command prompt
echo   3. Run 2_TEST.bat again
echo ============================================================
pause