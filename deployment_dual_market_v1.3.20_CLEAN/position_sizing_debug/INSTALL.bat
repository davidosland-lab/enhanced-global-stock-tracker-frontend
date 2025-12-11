@echo off
REM ====================================================================
REM Position Sizing Debug Installer
REM Fixes: Only 1 share per trade bug
REM ====================================================================

echo.
echo ========================================
echo   POSITION SIZING DEBUG INSTALLER
echo ========================================
echo.
echo This installs DEBUG version to find why only 1 share per trade!
echo.

REM Get FinBERT directory
set /p FINBERT_DIR="Enter FinBERT base directory (e.g., C:\Users\david\AATelS): "

REM Auto-detect finbert_v4.4.4 subdirectory
if exist "%FINBERT_DIR%\finbert_v4.4.4" (
    set TARGET_DIR=%FINBERT_DIR%\finbert_v4.4.4
) else (
    echo.
    echo [ERROR] Directory not found: %FINBERT_DIR%\finbert_v4.4.4
    pause
    exit /b 1
)

echo [INFO] Using directory: %TARGET_DIR%

REM Create backups
echo.
echo [INFO] Creating backups...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/: " %%a in ('time /t') do (set mytime=%%a%%b)

copy "%TARGET_DIR%\app_finbert_v4_dev.py" "%TARGET_DIR%\app_finbert_v4_dev.py.backup.%mydate%_%mytime%" >nul 2>&1
copy "%TARGET_DIR%\models\backtesting\swing_trader_engine.py" "%TARGET_DIR%\models\backtesting\swing_trader_engine.py.backup.%mydate%_%mytime%" >nul 2>&1

echo [OK] Backups created

REM Install files
echo.
echo [INFO] Installing debug version...
copy /Y app_finbert_v4_dev.py "%TARGET_DIR%\" >nul 2>&1
copy /Y swing_trader_engine.py "%TARGET_DIR%\models\backtesting\" >nul 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to copy files
    pause
    exit /b 1
)
echo [OK] Debug files installed

echo.
echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo Installed:
echo  [v] API confidence fix (65%% -^> 52%%)
echo  [v] Position sizing DEBUG logging
echo  [v] Engine initialization logging
echo.
echo Next Steps:
echo  1. cd %FINBERT_DIR%
echo  2. python finbert_v4.4.4\app_finbert_v4_dev.py
echo  3. Watch console output carefully!
echo  4. Run backtest (AAPL 2023-01-01 to 2024-11-01)
echo  5. Look for "POSITION SIZING DEBUG:" in logs
echo  6. Copy ALL console output and share it!
echo.
echo Expected Log Output:
echo  [INFO] Engine initialized with:
echo  [INFO]   Initial Capital: $100,000.00
echo  [INFO]   Max Position Size: 25.0%% = $25,000.00 per trade
echo.
echo  [INFO] POSITION SIZING DEBUG:
echo  [INFO]   Current Capital: $XXX.XX
echo  [INFO]   Calculated Shares: XXX
echo.
pause
