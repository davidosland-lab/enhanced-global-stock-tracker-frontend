@echo off
cls
echo ============================================
echo QUICK MARKET TRACKER FIX
echo ============================================
echo.

REM Make sure we're in the right directory
cd /D "%~dp0"

REM Run the standalone Python fix
echo Running time zone fix...
echo.
python fix_market_tracker_standalone.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================
    echo Python not working. Here's a manual fix:
    echo ============================================
    echo.
    echo 1. Find your market tracker HTML file
    echo    Usually in: modules\market-tracking\
    echo.
    echo 2. Open in Notepad
    echo.
    echo 3. Find and Replace (Ctrl+H):
    echo.
    echo    FIND:         REPLACE WITH:
    echo    -----         -------------
    echo    AEST          ADST
    echo    18:00 - 02:30 19:00 - 03:30
    echo    00:30 - 07:00 01:30 - 08:00
    echo.
    echo 4. Save and refresh browser
)

pause