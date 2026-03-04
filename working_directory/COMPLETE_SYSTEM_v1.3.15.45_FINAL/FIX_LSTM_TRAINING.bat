@echo off
setlocal enabledelayedexpansion

echo ========================================
echo LSTM TRAINING FIX TOOL
echo ========================================
echo System: v1.3.15.45 FINAL
echo Issue: No module named 'models.train_lstm'
echo ========================================
echo.

REM Check 1: Source file
echo [1] Checking source file (local FinBERT)...
set SOURCE=finbert_v4.4.4\models\train_lstm.py

if exist "%SOURCE%" (
    echo [OK] Source file found
    for %%A in ("%SOURCE%") do set SIZE=%%~zA
    echo     Size: !SIZE! bytes
) else (
    echo [ERROR] Source file NOT found: %SOURCE%
    echo.
    echo Please run this script from:
    echo   C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\
    echo.
    pause
    exit /b 1
)
echo.

REM Check 2: Destination directory
echo [2] Checking destination (AATelS FinBERT)...
set DEST=C:\Users\david\AATelS\finbert_v4.4.4\models\

if exist "%DEST%" (
    echo [OK] AATelS FinBERT models directory found
) else (
    echo [WARN] AATelS models directory doesn't exist
    echo.
    echo Creating directory...
    mkdir "%DEST%" 2>nul
    if !errorlevel! equ 0 (
        echo [OK] Directory created
    ) else (
        echo [ERROR] Failed to create directory
        echo         Try running as Administrator
        pause
        exit /b 1
    )
)

REM Check if file already exists
if exist "%DEST%train_lstm.py" (
    echo [INFO] train_lstm.py already exists in AATelS
    echo.
    set /p OVERWRITE="Overwrite existing file? (y/n): "
    if /i "!OVERWRITE!" neq "y" (
        echo.
        echo Copy cancelled.
        goto :end
    )
)
echo.

REM Perform the copy
echo [3] Copying train_lstm.py to AATelS...
xcopy /Y "%SOURCE%" "%DEST%"

if %errorlevel% equ 0 (
    echo [OK] File copied successfully!
    echo.
    echo [4] Verifying installation...
    if exist "%DEST%train_lstm.py" (
        echo [OK] File verified at destination
        for %%A in ("%DEST%train_lstm.py") do set DESTSIZE=%%~zA
        echo     Size: !DESTSIZE! bytes
        echo.
        echo ========================================
        echo FIX COMPLETE
        echo ========================================
        echo.
        echo LSTM training should now work!
        echo.
        echo Next time you run UK pipeline:
        echo   - LSTM training will succeed
        echo   - Models will be created/updated
        echo   - No more "No module named" errors
        echo.
    ) else (
        echo [ERROR] File not found at destination after copy
        echo         Something went wrong
    )
) else (
    echo [ERROR] Copy failed!
    echo.
    echo Possible causes:
    echo   - Permission denied (run as Administrator)
    echo   - Destination path doesn't exist
    echo   - Source file in use
    echo.
    echo Manual copy command:
    echo   xcopy /Y "%CD%\%SOURCE%" "%DEST%"
)

:end
echo.
echo ========================================
echo ADDITIONAL INFORMATION
echo ========================================
echo.
echo Source: %CD%\%SOURCE%
echo Destination: %DEST%train_lstm.py
echo.
echo If copy failed, you can also:
echo   1. Temporarily disable LSTM training:
echo      Edit config\screening_config.json
echo      Set "lstm_training": {"enabled": false}
echo.
echo   2. Rename AATelS folder to use local FinBERT:
echo      rename C:\Users\david\AATelS\finbert_v4.4.4 finbert_v4.4.4.disabled
echo.
pause
