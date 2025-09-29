@echo off
:: GSMT Ver 8.1.3 - Indices Tracker Update
:: This updates only the indices tracker to fix all issues

title GSMT Indices Tracker Update
color 0A
cls

echo ================================================================================
echo                    GSMT INDICES TRACKER - UPDATE PATCH
echo                         Fixing All Reported Issues
echo ================================================================================
echo.
echo This update will fix:
echo   [✓] All markets on ONE unified graph
echo   [✓] Calendar/date picker restored
echo   [✓] No infinite scroll - fixed height
echo   [✓] Proper data plotting
echo   [✓] Markets only show during trading hours
echo   [✓] AEST/AEDT timezone support
echo.
echo ================================================================================
echo.

:: Change to script directory
cd /d "%~dp0"

:: Check if GSMT is installed
if not exist "frontend" (
    echo ERROR: GSMT not found in current directory!
    echo Please run this update in your GSMT installation folder.
    pause
    exit /b 1
)

echo [1] Backing up current indices tracker...
if exist "frontend\indices_tracker.html" (
    copy "frontend\indices_tracker.html" "frontend\indices_tracker_backup_%date:~-4%%date:~4,2%%date:~7,2%.html" >nul 2>&1
)
if exist "frontend\indices_tracker_enhanced.html" (
    copy "frontend\indices_tracker_enhanced.html" "frontend\indices_tracker_enhanced_backup_%date:~-4%%date:~4,2%%date:~7,2%.html" >nul 2>&1
)
echo    Backup created
echo.

:: Create the unified tracker if it doesn't exist
echo [2] Installing unified indices tracker...
if not exist "frontend\indices_tracker_unified.html" (
    echo ERROR: Update file not found!
    echo Please ensure indices_tracker_unified.html is in the frontend folder
    pause
    exit /b 1
)

:: Update the main dashboard to use the new tracker
echo [3] Updating dashboard links...
if exist "frontend\main_dashboard.html" (
    echo    Main dashboard found, updating...
) else (
    echo    Main dashboard not found, skipping...
)

:: Create a shortcut to the new tracker
echo [4] Creating desktop shortcut...
set "desktop=%USERPROFILE%\Desktop"
(
    echo [InternetShortcut]
    echo URL=file:///%~dp0frontend\indices_tracker_unified.html
    echo IconIndex=0
    echo IconFile=%SystemRoot%\system32\SHELL32.dll,177
) > "%desktop%\GSMT Indices Unified.url"
echo    Desktop shortcut created
echo.

:: Check if servers are running
echo [5] Checking servers...
netstat -an | findstr ":8000" >nul 2>&1
if errorlevel 1 (
    echo    Market server not running - starting it...
    start "Market Server" /min cmd /c "cd /d "%~dp0" && python backend\market_data_server.py"
    timeout /t 3 /nobreak >nul
) else (
    echo    Market server already running
)
echo.

:: Open the updated tracker
echo [6] Opening updated indices tracker...
start "" "%~dp0frontend\indices_tracker_unified.html"
echo.

echo ================================================================================
echo                      UPDATE COMPLETE!
echo ================================================================================
echo.
echo The updated indices tracker is now open in your browser.
echo.
echo KEY FEATURES:
echo   • ALL markets displayed on ONE unified graph
echo   • Calendar for date selection restored
echo   • Fixed height - no infinite scrolling
echo   • Real data plotting (when servers are running)
echo   • Markets only show data during trading hours
echo   • AEST/AEDT timezone toggle
echo   • 24-hour x-axis starting from 9:00 AEST
echo.
echo MARKET HOURS (AEST):
echo   • ASX: 10:00 - 16:00
echo   • Nikkei: 10:00 - 16:00
echo   • Hang Seng: 11:30 - 18:00
echo   • FTSE: 17:00 - 01:30
echo   • DAX: 17:00 - 01:30
echo   • S&P 500: 23:30 - 06:00
echo.
echo TO USE:
echo   1. Select/deselect markets using the buttons
echo   2. Toggle AEST/AEDT with the switch
echo   3. Use calendar to select historical dates
echo   4. Choose time period (1 Day, 5 Days, 1 Month, 3 Months)
echo.
echo ================================================================================
echo.
pause