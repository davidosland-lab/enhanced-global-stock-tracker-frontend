@echo off
cls
echo ============================================
echo FIX FTSE AND S&P 500 PLOTTING TIMES
echo ============================================
echo.
echo Current issue: FTSE and S&P 500 plot at wrong times
echo This fix will shift them to correct ADST trading hours:
echo   - FTSE: 19:00 - 03:30 ADST
echo   - S&P 500: 01:30 - 08:00 ADST
echo.
pause

cd /D "%~dp0"

echo.
echo Applying time offset fix...
python FIX_FTSE_SP500_TIMES.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Python script failed. Applying manual fix...
    echo.
    echo Please manually edit market_tracker_final.html:
    echo.
    echo Find the processMarketData function and add time offsets:
    echo   For FTSE: Add 11 hours to timestamps
    echo   For S&P 500: Add 16 hours to timestamps
    echo.
)

echo.
echo ============================================
echo After this fix:
echo ============================================
echo.
echo The chart should show:
echo   - ASX (red): 10:00 - 16:00 ADST (correct already)
echo   - FTSE (blue): 19:00 - 03:30 ADST (evening/night)
echo   - S&P 500 (purple): 01:30 - 08:00 ADST (early morning)
echo.
echo Please refresh your browser (F5) to see the changes.
echo.
pause