@echo off
echo =====================================
echo FIXING YAHOO FINANCE - DEFINITIVE FIX
echo =====================================
echo.
echo This will:
echo 1. Uninstall current yfinance
echo 2. Install specific working versions
echo 3. Clear all caches
echo 4. Test the connection
echo.
echo This should fix the issue...
echo.

python fix_yahoo_definitive.py

echo.
echo =====================================
echo After this fix, run:
echo 4_quick_test.bat to verify
echo =====================================
pause