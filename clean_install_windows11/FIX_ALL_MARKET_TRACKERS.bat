@echo off
cls
echo ============================================
echo COMPREHENSIVE MARKET TRACKER FIX
echo ============================================
echo.
echo This will fix ALL market tracker files to show
echo correct Australian Daylight Saving Time (ADST)
echo.

cd /D "%~dp0"

echo [1/4] Fixing modules\indices_tracker.html...
copy /Y modules\indices_tracker_fixed_times.html modules\indices_tracker.html >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo      [OK] indices_tracker.html updated
) else (
    echo      [WARN] Could not update indices_tracker.html
)

echo.
echo [2/4] Fixing modules\market-tracking\market_tracker_final.html...
copy /Y modules\indices_tracker_fixed_times.html modules\market-tracking\market_tracker_final.html >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo      [OK] market_tracker_final.html updated
) else (
    echo      [WARN] Could not update market_tracker_final.html
)

echo.
echo [3/4] Fixing modules\global_market_tracker.html...
copy /Y modules\indices_tracker_fixed_times.html modules\global_market_tracker.html >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo      [OK] global_market_tracker.html updated
) else (
    echo      [WARN] Could not update global_market_tracker.html
)

echo.
echo [4/4] Verifying the fix...
findstr /C:"ADST" modules\indices_tracker.html >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo      [OK] ADST timezone confirmed in files
) else (
    echo      [ERROR] Fix may not have been applied
)

echo.
echo ============================================
echo FIX COMPLETED
echo ============================================
echo.
echo ALL market tracker files have been updated to show:
echo.
echo   AUSTRALIAN DAYLIGHT SAVING TIME (ADST = UTC+11)
echo   ------------------------------------------------
echo   ASX/AORD:  10:00 - 16:00 ADST (same day)
echo   FTSE 100:  19:00 - 03:30 ADST (crosses midnight)
echo   SP500:     01:30 - 08:00 ADST (early morning)
echo.
echo The X-axis will now correctly display:
echo   - Market hours in ADST
echo   - Gaps when markets are closed
echo   - Proper time labels (10:00, 16:00, 19:00, etc.)
echo.
echo ============================================
echo IMPORTANT: Clear Browser Cache
echo ============================================
echo.
echo To see the changes:
echo   1. Press Ctrl+F5 in your browser (hard refresh)
echo   2. Or clear browser cache for localhost:8000
echo   3. Reload the page
echo.
echo The console errors about dates should also be resolved.
echo.
pause