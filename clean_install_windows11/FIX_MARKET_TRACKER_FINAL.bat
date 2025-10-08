@echo off
echo ============================================
echo FIXING MARKET TRACKER FINAL - ADST Times
echo ============================================
echo.

cd /D "%~dp0"

echo Option 1: Replace with fixed indices tracker
echo ------------------------------------------
copy /Y modules\indices_tracker_fixed_times.html modules\market-tracking\market_tracker_final.html
if %ERRORLEVEL% EQU 0 (
    echo [OK] market_tracker_final.html updated with ADST fix
) else (
    echo [ERROR] Could not update market_tracker_final.html
)

echo.
echo Option 2: Update index.html to use fixed tracker
echo ------------------------------------------
echo Please edit index.html and change:
echo   FROM: modules/market-tracking/market_tracker_final.html
echo   TO:   modules/indices_tracker.html
echo.

echo ============================================
echo QUICK FIX COMPLETED
echo ============================================
echo.
echo The market tracker should now show:
echo   - Correct ADST times on X-axis
echo   - ASX: 10:00-16:00 ADST
echo   - FTSE: 19:00-03:30 ADST
echo   - SP500: 01:30-08:00 ADST
echo.
echo Please refresh your browser (Ctrl+F5)
echo.
pause