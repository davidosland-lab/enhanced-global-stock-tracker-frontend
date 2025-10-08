@echo off
echo ============================================
echo FIXING GLOBAL INDICES TRACKER TIME AXIS
echo ============================================
echo.
echo This will replace the indices tracker with a version that
echo properly displays market hours in Australian Daylight Saving Time (ADST)
echo.

cd /D "%~dp0"

echo Backing up current indices tracker...
copy modules\indices_tracker.html modules\indices_tracker_backup.html 2>nul

echo.
echo Installing fixed version with proper ADST times...
copy /Y modules\indices_tracker_fixed_times.html modules\indices_tracker.html

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Indices tracker has been fixed.
    echo.
    echo WHAT'S FIXED:
    echo - X-axis now shows correct ADST times
    echo - ASX plots from 10:00 - 16:00 ADST
    echo - FTSE plots from 19:00 - 03:30 ADST (crosses midnight)
    echo - S&P 500 plots from 01:30 - 08:00 ADST
    echo - Market gaps properly shown when markets are closed
    echo - Time labels clearly show market open/close times
    echo.
    echo Please refresh your browser to see the changes.
) else (
    echo.
    echo ERROR: Failed to copy fixed version.
    echo Please manually copy indices_tracker_fixed_times.html to indices_tracker.html
)

echo.
pause