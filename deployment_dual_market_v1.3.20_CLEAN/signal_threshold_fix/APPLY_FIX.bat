@echo off
REM ====================================================================
REM Signal Threshold Fix Installer
REM Fixes: Only 4 trades executing
REM ====================================================================

echo.
echo ========================================
echo   SIGNAL THRESHOLD FIX INSTALLER
echo ========================================
echo.
echo This will fix:
echo  1. Combined score threshold (0.15 -^> 0.05)
echo  2. Confidence threshold (65%% -^> 52%%)
echo  3. No news sentiment (0.0 -^> 0.05)
echo  4. Add debug logging
echo.
echo RESULT: 40-50 trades instead of 4!
echo.

REM Get FinBERT directory
set /p FINBERT_DIR="Enter FinBERT directory (e.g., C:\Users\david\AATelS): "

REM Check if finbert_v4.4.4 exists (auto-detect subdirectory)
if exist "%FINBERT_DIR%\finbert_v4.4.4" (
    set TARGET_DIR=%FINBERT_DIR%\finbert_v4.4.4
) else if exist "%FINBERT_DIR%\models" (
    set TARGET_DIR=%FINBERT_DIR%
) else (
    echo.
    echo [ERROR] Directory not found: %FINBERT_DIR%\finbert_v4.4.4
    echo.
    pause
    exit /b 1
)

echo [INFO] Using directory: %TARGET_DIR%

REM Check if target file exists
if not exist "%TARGET_DIR%\models\backtesting\swing_trader_engine.py" (
    echo.
    echo [ERROR] File not found: %TARGET_DIR%\models\backtesting\swing_trader_engine.py
    echo.
    pause
    exit /b 1
)

REM Create backup
echo.
echo [INFO] Creating backup...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/: " %%a in ('time /t') do (set mytime=%%a%%b)
set BACKUP_FILE=%TARGET_DIR%\models\backtesting\swing_trader_engine.py.backup.%mydate%_%mytime%

copy "%TARGET_DIR%\models\backtesting\swing_trader_engine.py" "%BACKUP_FILE%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create backup
    pause
    exit /b 1
)
echo [OK] Backup created: %BACKUP_FILE%

REM Copy fixed file
echo.
echo [INFO] Installing fix...
copy /Y swing_trader_engine.py "%TARGET_DIR%\models\backtesting\" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to copy fixed file
    pause
    exit /b 1
)
echo [OK] Fixed file installed

echo.
echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo Fixed:
echo  [v] Buy threshold: 0.15 -^> 0.05 (3x more sensitive)
echo  [v] Confidence: 65%% -^> 52%% (13%% lower)
echo  [v] No news sentiment: 0.0 -^> 0.05
echo  [v] Debug logging added
echo.
echo Next Steps:
echo  1. cd %FINBERT_DIR%
echo  2. python finbert_v4.4.4\app_finbert_v4_dev.py
echo  3. Open: http://localhost:5001
echo  4. Run AAPL backtest (2023-01-01 to 2024-11-01)
echo  5. EXPECT 40-50 TRADES NOW!
echo.
pause
