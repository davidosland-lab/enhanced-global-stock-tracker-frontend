@echo off
cls
echo ============================================
echo WINDOWS MARKET TRACKER FIX
echo ============================================
echo.
echo Looking for your StockTrack installation...
echo.

REM Try to find where we are
cd /D "%~dp0"
echo Current directory: %CD%
echo.

REM Check if we have the Python fix script
if not exist "FIX_TIME_MINIMAL.py" (
    echo ERROR: FIX_TIME_MINIMAL.py not found in current directory
    echo.
    echo Creating the fix script now...
    goto CREATE_FIX_SCRIPT
) else (
    goto APPLY_FIX
)

:CREATE_FIX_SCRIPT
echo Creating FIX_TIME_MINIMAL.py...
(
echo import os
echo import shutil
echo from datetime import datetime
echo.
echo print("=" * 60^)
echo print("MINIMAL TIME FIX FOR MARKET TRACKER"^)
echo print("=" * 60^)
echo print(^)
echo.
echo # Find the market tracker file
echo possible_paths = [
echo     "modules/market-tracking/market_tracker_final.html",
echo     "modules/indices_tracker.html",
echo     "market_tracker_final.html"
echo ]
echo.
echo tracker_file = None
echo for path in possible_paths:
echo     if os.path.exists(path^):
echo         tracker_file = path
echo         print(f"Found tracker at: {path}"^)
echo         break
echo.
echo if not tracker_file:
echo     print("ERROR: Could not find market tracker file"^)
echo     exit(1^)
echo.
echo # Read the file
echo with open(tracker_file, 'r', encoding='utf-8'^) as f:
echo     content = f.read(^)
echo.
echo # Apply minimal fixes
echo content = content.replace('AEST', 'ADST'^)
echo content = content.replace('Trading: 18:00 - 02:30 ADST', 'Trading: 19:00 - 03:30 ADST'^)
echo content = content.replace('Trading: 00:30 - 07:00 ADST', 'Trading: 01:30 - 08:00 ADST'^)
echo content = content.replace('hours ^>= 18 ^|^| hours ^< 2.5', 'hours ^>= 19 ^|^| hours ^< 3.5'^)
echo content = content.replace('hours ^>= 0.5 ^&^& hours ^< 7', 'hours ^>= 1.5 ^&^& hours ^< 8'^)
echo.
echo # Write the fixed content
echo with open(tracker_file, 'w', encoding='utf-8'^) as f:
echo     f.write(content^)
echo.
echo print("Fix applied successfully!"^)
) > FIX_TIME_MINIMAL.py

echo.
echo Fix script created.
echo.

:APPLY_FIX
echo Applying the time zone fix...
echo ----------------------------------------------
python FIX_TIME_MINIMAL.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Time fix applied!
) else (
    echo.
    echo WARNING: Python fix failed. Trying manual fix...
    goto MANUAL_FIX
)
goto END

:MANUAL_FIX
echo.
echo ============================================
echo MANUAL FIX INSTRUCTIONS
echo ============================================
echo.
echo Please manually edit your market tracker file:
echo.
echo 1. Find the file:
echo    - modules/market-tracking/market_tracker_final.html
echo    OR
echo    - modules/indices_tracker.html
echo.
echo 2. Open it in Notepad
echo.
echo 3. Press Ctrl+H (Find and Replace)
echo.
echo 4. Make these replacements:
echo    Find: AEST
echo    Replace with: ADST
echo.
echo    Find: Trading: 18:00 - 02:30 ADST
echo    Replace with: Trading: 19:00 - 03:30 ADST
echo.
echo    Find: Trading: 00:30 - 07:00 ADST
echo    Replace with: Trading: 01:30 - 08:00 ADST
echo.
echo 5. Save the file
echo.

:END
echo.
echo ============================================
echo EXPECTED RESULTS
echo ============================================
echo.
echo After fixing, the market hours should show:
echo   ASX:   10:00 - 16:00 ADST
echo   FTSE:  19:00 - 03:30 ADST
echo   SP500: 01:30 - 08:00 ADST
echo.
echo Time zone: ADST (UTC+11)
echo.
pause