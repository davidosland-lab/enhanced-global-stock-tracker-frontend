@echo off
REM ============================================================================
REM FAST TEST - Dual Market Screening System
REM Tests only 1-2 sectors for quick validation
REM ============================================================================

echo ================================================================================
echo   FAST TEST - Quick Validation (1-2 Minutes)
echo ================================================================================
echo.
echo This is a FAST validation test:
echo   - ASX: Financials sector only (5 stocks)
echo   - US: Technology sector only (5 stocks)
echo   - Expected duration: 1-2 minutes
echo.
echo Use this to quickly verify:
echo   - System is installed correctly
echo   - Dependencies are working
echo   - Pipelines can execute
echo.
pause
echo.

echo ================================================================================
echo TESTING ASX MARKET (Financials only)...
echo ================================================================================
python run_screening.py --market asx --sectors Financials --stocks 5

echo.
echo ================================================================================
echo TESTING US MARKET (Technology only)...
echo ================================================================================
python run_screening.py --market us --sectors Technology --stocks 5

echo.
echo ================================================================================
echo   FAST TEST COMPLETE
echo ================================================================================
echo.
echo Results:
echo   - ASX Reports: reports\morning_reports\
echo   - US Reports: reports\us\
echo   - ASX Data: data\asx\
echo   - US Data: data\us\
echo.
echo For FULL screening of all sectors:
echo   - Run: RUN_QUICK_TEST.bat (both markets, all sectors, ~20 min)
echo   - Or: RUN_BOTH_MARKETS.bat (production run, ~30 min)
echo.
pause
