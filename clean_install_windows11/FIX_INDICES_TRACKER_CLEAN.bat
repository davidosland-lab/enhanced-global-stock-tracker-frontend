@echo off
echo ============================================
echo FIXING GLOBAL INDICES TRACKER TIME AXIS
echo ============================================
echo.
echo This will fix the time display to show correct
echo Australian Daylight Saving Time (ADST)
echo.

cd /D "%~dp0"

echo Backing up current indices tracker...
copy modules\indices_tracker.html modules\indices_tracker_backup_%date:~-4%%date:~4,2%%date:~7,2%.html 2>nul

echo.
echo Installing fixed version...
copy /Y modules\indices_tracker_fixed_times.html modules\indices_tracker.html

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo SUCCESS! Indices tracker has been fixed
    echo ============================================
    echo.
    echo WHAT HAS BEEN FIXED:
    echo   - X-axis now shows correct ADST times
    echo   - ASX plots from 10:00 to 16:00 ADST
    echo   - FTSE plots from 19:00 to 03:30 ADST
    echo   - SP500 plots from 01:30 to 08:00 ADST
    echo   - Market gaps shown when closed
    echo   - Time labels show open/close times
    echo.
    echo Please refresh your browser to see changes
    echo.
) else (
    echo.
    echo ============================================
    echo MANUAL FIX NEEDED
    echo ============================================
    echo.
    echo Please copy the file manually:
    echo   FROM: modules\indices_tracker_fixed_times.html
    echo   TO:   modules\indices_tracker.html
    echo.
)

pause