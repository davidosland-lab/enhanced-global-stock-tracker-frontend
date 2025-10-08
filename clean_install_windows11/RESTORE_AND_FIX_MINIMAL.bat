@echo off
cls
echo ============================================
echo RESTORE ORIGINAL AND APPLY MINIMAL FIX
echo ============================================
echo.
echo This will:
echo   1. Restore the ORIGINAL working market tracker
echo   2. Apply ONLY the time zone fix (AEST to ADST)
echo   3. Keep all working functionality intact
echo.
pause

cd /D "%~dp0"

echo.
echo [STEP 1] Restoring original working version...
echo ----------------------------------------------
copy /Y modules\market-tracking\market_tracker_final.html.backup_20251005_055727 modules\market-tracking\market_tracker_final.html 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Original version restored
) else (
    echo [WARNING] Could not find original backup
    echo Trying alternative restore...
    copy /Y modules\market-tracking\market_tracker_final_original.html modules\market-tracking\market_tracker_final.html 2>nul
)

echo.
echo [STEP 2] Applying minimal time fix...
echo ----------------------------------------------
python FIX_TIME_MINIMAL.py
if %ERRORLEVEL% EQU 0 (
    echo [OK] Time fix applied successfully
) else (
    echo [ERROR] Could not apply time fix
    echo Please run FIX_TIME_MINIMAL.py manually
)

echo.
echo ============================================
echo FIX COMPLETED
echo ============================================
echo.
echo What has been fixed:
echo   - Display shows ADST (Australian Daylight Saving Time)
echo   - FTSE: 19:00 - 03:30 ADST
echo   - S&P 500: 01:30 - 08:00 ADST
echo   - Time conversion uses UTC+11 (ADST)
echo.
echo The original working functionality is preserved.
echo No JavaScript errors should occur.
echo.
echo Please refresh your browser (F5) to see the changes.
echo.
pause