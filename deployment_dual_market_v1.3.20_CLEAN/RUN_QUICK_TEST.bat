@echo off
REM ============================================================================
REM Quick Test Script - Windows
REM ============================================================================

echo ================================================================================
echo   QUICK TEST - Dual Market Screening System
echo ================================================================================
echo.
echo IMPORTANT: This tests BOTH ASX and US markets (full suite)
echo.
echo What this does:
echo   - Scans ALL sectors (8 ASX + 8 US = 16 total)
echo   - Validates ~30 stocks per sector (full stock lists)
echo   - Returns TOP 5 stocks per sector for prediction
echo   - Expected duration: 15-25 minutes for both markets
echo.
echo NOTE: Each sector loads 30 stocks for validation, then selects top 5.
echo This is the FULL screening system, not a quick demo.
echo.
echo For a faster test, use:
echo   python run_screening.py --market asx --stocks 5   (ASX only, 5-10 min)
echo   python run_screening.py --market us --stocks 5    (US only, 10-15 min)
echo.
pause
echo.

REM Run quick test
python run_screening.py --market both --stocks 5

echo.
echo ================================================================================
echo   TEST COMPLETE
echo ================================================================================
echo.
echo Check outputs:
echo   - Reports: reports\ and reports\us\
echo   - Data: data\ and data\us\
echo   - Logs: logs\screening\ and logs\screening\us\
echo.
pause
