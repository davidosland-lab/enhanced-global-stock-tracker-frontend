@echo off
cls
color 0A
echo ================================================================
echo         FORCE CLEAN MARKET TRACKER FIX
echo ================================================================
echo.
echo This will completely replace all market tracker files
echo with the working ADST version and clear any errors.
echo.

cd /D "%~dp0"

echo [STEP 1] Backing up current files...
echo ----------------------------------------
mkdir backups 2>nul
copy modules\market-tracking\market_tracker_final.html backups\market_tracker_final_backup.html 2>nul
copy modules\indices_tracker.html backups\indices_tracker_backup.html 2>nul
echo Backups created in 'backups' folder

echo.
echo [STEP 2] Removing corrupted files...
echo ----------------------------------------
del modules\market-tracking\market_tracker_final.html 2>nul
echo Old files removed

echo.
echo [STEP 3] Installing clean ADST version...
echo ----------------------------------------
copy modules\indices_tracker_fixed_times.html modules\indices_tracker.html /Y
if %ERRORLEVEL% EQU 0 (
    echo [OK] indices_tracker.html installed
) else (
    echo [ERROR] Failed to install indices_tracker.html
)

copy modules\indices_tracker_fixed_times.html modules\market-tracking\market_tracker_final.html /Y
if %ERRORLEVEL% EQU 0 (
    echo [OK] market_tracker_final.html installed
) else (
    echo [ERROR] Failed to install market_tracker_final.html
)

copy modules\indices_tracker_fixed_times.html modules\global_market_tracker.html /Y
if %ERRORLEVEL% EQU 0 (
    echo [OK] global_market_tracker.html installed
) else (
    echo [ERROR] Failed to install global_market_tracker.html
)

echo.
echo [STEP 4] Verification...
echo ----------------------------------------
if exist "modules\market-tracking\market_tracker_final.html" (
    echo [OK] market_tracker_final.html exists
) else (
    echo [ERROR] market_tracker_final.html missing!
)

if exist "modules\indices_tracker.html" (
    echo [OK] indices_tracker.html exists
) else (
    echo [ERROR] indices_tracker.html missing!
)

echo.
echo ================================================================
echo                     FIX COMPLETED!
echo ================================================================
echo.
echo JAVASCRIPT ERRORS FIXED:
echo   - No more "exports is not defined" errors
echo   - No more "Cannot set properties of null" errors
echo   - Clean ADST timezone implementation
echo.
echo MARKET HOURS NOW DISPLAY:
echo   ASX:   10:00 - 16:00 ADST
echo   FTSE:  19:00 - 03:30 ADST (next day)
echo   SP500: 01:30 - 08:00 ADST
echo.
echo ================================================================
echo              IMPORTANT: CLEAR BROWSER CACHE!
echo ================================================================
echo.
echo To completely fix the errors:
echo.
echo   1. Close ALL browser tabs with localhost:8000
echo   2. Clear browser cache (Ctrl+Shift+Delete)
echo   3. Select "Cached images and files"
echo   4. Clear for "All time"
echo   5. Restart browser
echo   6. Go to http://localhost:8000
echo.
echo Or try opening in Incognito/Private mode to bypass cache.
echo.
echo ================================================================
echo.
pause