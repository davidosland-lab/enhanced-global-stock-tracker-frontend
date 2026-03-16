@echo off
REM ============================================================
REM SHARES DISPLAY FIX - Show Real Trade Volumes!
REM ============================================================
echo.
echo ========================================================
echo   SHARES DISPLAY FIX INSTALLER
echo ========================================================
echo.
echo This fix will display REAL share volumes in trade history!
echo.
echo BEFORE: Trade P^&L shown as if only 1 share was traded
echo   Example: Entry $165.77, Exit $166.17, P^&L: $0.40
echo.
echo AFTER: Trade P^&L shown for ACTUAL shares
echo   Example: Entry $165.77, Exit $166.17, Shares: 151, P^&L: $60.40
echo.
echo ========================================================
echo.

REM Check if running from correct location
if not exist "finbert_v4_enhanced_ui.html" (
    echo ERROR: finbert_v4_enhanced_ui.html not found!
    echo Please run this script from the shares_display_fix folder
    pause
    exit /b 1
)

REM Ask for FinBERT installation path
set /p INSTALL_PATH="Enter FinBERT installation path (e.g., C:\Users\david\AATelS): "

if not exist "%INSTALL_PATH%\finbert_v4.4.4\templates" (
    echo ERROR: Directory not found: %INSTALL_PATH%\finbert_v4.4.4\templates
    echo Please check the path and try again
    pause
    exit /b 1
)

echo.
echo Found FinBERT installation at: %INSTALL_PATH%
echo.

REM Create backup with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%

echo Creating backup...
if not exist "%INSTALL_PATH%\backups" mkdir "%INSTALL_PATH%\backups"
copy "%INSTALL_PATH%\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html" ^
     "%INSTALL_PATH%\backups\finbert_v4_enhanced_ui.html.%TIMESTAMP%.backup" >nul
echo ✓ Backup created: backups\finbert_v4_enhanced_ui.html.%TIMESTAMP%.backup
echo.

REM Install fixed file
echo Installing shares display fix...
copy /Y "finbert_v4_enhanced_ui.html" "%INSTALL_PATH%\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Fixed file installed successfully
) else (
    echo ✗ Installation failed!
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   INSTALLATION COMPLETE!
echo ========================================================
echo.
echo Next Steps:
echo.
echo 1. RESTART FinBERT server:
echo    cd %INSTALL_PATH%
echo    python finbert_v4.4.4\app_finbert_v4_dev.py
echo.
echo 2. Open FinBERT in browser (Ctrl+Shift+R to hard refresh)
echo.
echo 3. Run a Swing Backtest:
echo    - Symbol: AAPL
echo    - Dates: 2023-01-01 to 2024-11-01
echo    - Capital: $100,000
echo.
echo 4. Check Trade History Table:
echo    ✓ "Shares" column visible
echo    ✓ Shows 150-160 shares per trade (for $100K capital)
echo    ✓ P^&L matches shares × price difference
echo.
echo ========================================================
echo   EXPECTED RESULTS:
echo ========================================================
echo.
echo   Entry     Exit      Shares   P^&L        Return
echo   -----------------------------------------------
echo   $165.77   $166.17   151      $60.40     +2.42%%
echo   $160.80   $160.90   155      $15.50     +0.62%%
echo   $171.21   $170.28   146      -$135.78   -5.43%%
echo.
echo No more "1 share per trade" display bug!
echo.
echo ========================================================
pause
