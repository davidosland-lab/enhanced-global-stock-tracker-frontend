@echo off
REM ============================================================================
REM Quick Test Script - Windows
REM ============================================================================

echo ================================================================================
echo   QUICK TEST - Dual Market Screening System
echo ================================================================================
echo.
echo This will test the system with 5 stocks per sector
echo Expected duration: 2-3 minutes
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
