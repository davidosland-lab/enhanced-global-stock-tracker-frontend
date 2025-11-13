@echo off
REM Event Risk Guard - Test Script
REM Tests the Event Risk Guard module with real ASX stocks

echo ================================================================================
echo Event Risk Guard - Test Mode
echo ================================================================================
echo.
echo This script tests the Event Risk Guard with real ASX stocks.
echo.
echo Testing stocks:
echo   - ANZ.AX (ANZ Group - earnings event)
echo   - NAB.AX (NAB - Basel III event)
echo   - CBA.AX (Commonwealth Bank)
echo.

echo Testing ANZ.AX...
echo ================================================================================
python models/screening/event_risk_guard.py ANZ.AX
echo.
echo.

echo Testing NAB.AX...
echo ================================================================================
python models/screening/event_risk_guard.py NAB.AX
echo.
echo.

echo Testing CBA.AX...
echo ================================================================================
python models/screening/event_risk_guard.py CBA.AX
echo.
echo.

echo ================================================================================
echo Testing Complete!
echo ================================================================================
echo.
echo Check the output above for:
echo   - Event detection (earnings, Basel III, dividends)
echo   - Risk scores (0-1 scale)
echo   - Position haircuts (20%, 45%, 70%)
echo   - Skip trading recommendations
echo.
pause
