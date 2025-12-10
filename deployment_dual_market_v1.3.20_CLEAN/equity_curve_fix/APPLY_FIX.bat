@echo off
REM ====================================================================
REM Equity Curve Chart & Win Rate Fix Installer
REM Fixes: Chart error and Win Rate display bug
REM ====================================================================

echo.
echo ========================================
echo   EQUITY CURVE FIX INSTALLER
echo ========================================
echo.
echo This will fix:
echo  1. Equity curve chart error
echo  2. Win Rate display bug (3111.1%% -^> 62.3%%)
echo.

REM Get FinBERT directory
set /p FINBERT_DIR="Enter FinBERT directory (e.g., C:\Users\david\AATelS): "

REM Check if directory exists
if not exist "%FINBERT_DIR%\finbert_v4.4.4" (
    echo.
    echo [ERROR] Directory not found: %FINBERT_DIR%\finbert_v4.4.4
    echo.
    pause
    exit /b 1
)

REM Create backup
echo.
echo [INFO] Creating backup...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/: " %%a in ('time /t') do (set mytime=%%a%%b)
set BACKUP_FILE=%FINBERT_DIR%\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html.backup.%mydate%_%mytime%

copy "%FINBERT_DIR%\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html" "%BACKUP_FILE%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create backup
    pause
    exit /b 1
)
echo [OK] Backup created: %BACKUP_FILE%

REM Copy fixed file
echo.
echo [INFO] Installing fix...
copy /Y finbert_v4_enhanced_ui.html "%FINBERT_DIR%\finbert_v4.4.4\templates\" >nul 2>&1
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
echo  [v] Equity curve chart now displays
echo  [v] Win Rate shows correct percentage
echo  [v] Total Return displays properly
echo.
echo Next Steps:
echo  1. cd %FINBERT_DIR%
echo  2. python finbert_v4.4.4\app_finbert_v4_dev.py
echo  3. Open: http://localhost:5001
echo  4. Click "Swing Trading" and run backtest
echo.
pause
