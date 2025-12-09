@echo off
REM UI Update - Swing Trading Backtest Button
REM Adds Swing Trading button and modal to FinBERT v4.0 UI

echo.
echo ============================================================
echo   Swing Trading UI Update Installer
echo   Adds NEW button to FinBERT v4.0 interface
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "templates\finbert_v4_enhanced_ui.html" (
    echo [ERROR] Please run this from the ui_update_swing_trading directory
    echo.
    pause
    exit /b 1
)

REM Ask for FinBERT directory
set /p FINBERT_DIR="Enter path to FinBERT v4.4.4 directory (e.g., C:\Users\david\AATelS): "

REM Remove quotes if present
set FINBERT_DIR=%FINBERT_DIR:"=%

REM Check if directory exists
if not exist "%FINBERT_DIR%" (
    echo [ERROR] Directory not found: %FINBERT_DIR%
    pause
    exit /b 1
)

REM Auto-detect finbert_v4.4.4 subdirectory
if exist "%FINBERT_DIR%\finbert_v4.4.4\templates" (
    set TARGET_DIR=%FINBERT_DIR%\finbert_v4.4.4
    echo [INFO] Found FinBERT in subdirectory: finbert_v4.4.4
) else if exist "%FINBERT_DIR%\templates" (
    set TARGET_DIR=%FINBERT_DIR%
    echo [INFO] Using directory: %FINBERT_DIR%
) else (
    echo [ERROR] Cannot find templates directory
    echo Searched in:
    echo   - %FINBERT_DIR%\finbert_v4.4.4\templates
    echo   - %FINBERT_DIR%\templates
    pause
    exit /b 1
)

echo [INFO] Target directory: %TARGET_DIR%
echo.

REM Create backup
echo [INFO] Creating backup...
set TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
copy "%TARGET_DIR%\templates\finbert_v4_enhanced_ui.html" "%TARGET_DIR%\templates\finbert_v4_enhanced_ui.html.backup.%TIMESTAMP%" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to create backup
    pause
    exit /b 1
)
echo [OK] Backup created: finbert_v4_enhanced_ui.html.backup.%TIMESTAMP%
echo.

REM Copy updated file
echo [INFO] Installing updated UI file...
copy /Y "templates\finbert_v4_enhanced_ui.html" "%TARGET_DIR%\templates\finbert_v4_enhanced_ui.html" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to copy UI file
    pause
    exit /b 1
)
echo [OK] UI file updated successfully
echo.

REM Verify the button was added
findstr /C:"Swing Trading" "%TARGET_DIR%\templates\finbert_v4_enhanced_ui.html" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Verification failed - Swing Trading button not found in file
    echo [INFO] Restoring backup...
    copy /Y "%TARGET_DIR%\templates\finbert_v4_enhanced_ui.html.backup.%TIMESTAMP%" "%TARGET_DIR%\templates\finbert_v4_enhanced_ui.html" >nul 2>&1
    pause
    exit /b 1
)
echo [OK] Swing Trading button verified in UI
echo.

echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo WHAT WAS ADDED:
echo   - New "Swing Trading" button (rose/pink color)
echo   - Complete modal with configuration form
echo   - Results display with charts and metrics
echo   - JavaScript functions for API integration
echo.
echo WHERE TO FIND IT:
echo   Top Navigation Bar -^> After "Portfolio Backtest"
echo   Color: Rose/Pink
echo   Icon: Chart Area
echo.
echo NEXT STEPS:
echo   1. Restart the FinBERT server:
echo      cd %TARGET_DIR%
echo      python app_finbert_v4_dev.py
echo.
echo   2. Open browser: http://localhost:5001
echo.
echo   3. Look for the NEW rose/pink "Swing Trading" button
echo.
echo   4. Click it and configure your backtest!
echo.
echo BACKUP LOCATION:
echo   %TARGET_DIR%\templates\finbert_v4_enhanced_ui.html.backup.%TIMESTAMP%
echo.
pause
