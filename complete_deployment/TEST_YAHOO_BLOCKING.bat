@echo off
REM ===============================================================================
REM   Quick Yahoo Finance Block Test
REM   Tests if your IP is currently blocked by Yahoo Finance
REM ===============================================================================

echo ================================================================================
echo   YAHOO FINANCE BLOCK TEST
echo ================================================================================
echo.
echo This quick test checks if Yahoo Finance is blocking your IP.
echo.
echo Test will:
echo   1. Import yfinance
echo   2. Fetch CBA.AX price (ASX stock)
echo   3. Fetch ^GSPC price (S&P 500)
echo   4. Fetch BHP.AX historical data
echo.
echo Duration: ~10 seconds
echo.

REM Set working directory
cd /d "%~dp0"

echo ================================================================================
echo   Running Test...
echo ================================================================================
echo.

REM Run the test
python test_yahoo_blocking.py

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo   ✅ NOT BLOCKED - You can run the screener now!
    echo ================================================================================
    echo.
) else (
    echo.
    echo ================================================================================
    echo   ❌ BLOCKED - Wait 1-2 hours and test again
    echo ================================================================================
    echo.
)

pause
