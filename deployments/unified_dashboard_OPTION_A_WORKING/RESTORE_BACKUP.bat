@echo off
REM ========================================
REM Restore Original Configuration
REM Undo Option A Changes
REM ========================================

echo ========================================
echo Restore Original Configuration
echo ========================================
echo.
echo This will undo all Option A changes:
echo 1. Restore original swing_signal_generator.py
echo 2. Remove keras.json (Keras will use default backend)
echo.
echo WARNING: Dashboard will revert to broken state!
echo          Only use this if you want to try Option B.
echo.
pause

set "RESTORED=0"
set "ERRORS=0"

REM Step 1: Restore swing_signal_generator.py
echo [1/2] Restoring swing_signal_generator.py...
set "TARGET_FILE=..\unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\ml_pipeline\swing_signal_generator.py"
set "BACKUP_FILE=%TARGET_FILE%.backup_option_a"

if exist "%BACKUP_FILE%" (
    copy "%BACKUP_FILE%" "%TARGET_FILE%" >nul
    if errorlevel 1 (
        echo ✗ Failed to restore file
        set /a ERRORS+=1
    ) else (
        echo ✓ Restored original swing_signal_generator.py
        set /a RESTORED+=1
        
        REM Verify restore
        findstr /C:"import keras" "%TARGET_FILE%" >nul
        if errorlevel 1 (
            echo ✗ WARNING: Restore may have failed (import not found)
            set /a ERRORS+=1
        ) else (
            echo ✓ Verified: Original import restored
        )
    )
) else (
    echo ✗ Backup file not found: %BACKUP_FILE%
    echo Cannot restore original file
    set /a ERRORS+=1
)
echo.

REM Step 2: Remove keras.json
echo [2/2] Removing Keras configuration...
if exist "%USERPROFILE%\.keras\keras.json" (
    del "%USERPROFILE%\.keras\keras.json"
    if errorlevel 1 (
        echo ✗ Failed to delete keras.json
        set /a ERRORS+=1
    ) else (
        echo ✓ Removed keras.json
        set /a RESTORED+=1
    )
) else (
    echo ℹ keras.json not found (already removed)
)
echo.

REM Summary
echo ========================================
echo RESTORE SUMMARY
echo ========================================
echo.
echo Items Restored: %RESTORED%
echo Errors: %ERRORS%
echo.

if %ERRORS% EQU 0 (
    echo ✓ RESTORE COMPLETE!
    echo.
    echo Your system is back to original state.
    echo.
    echo Note: Dashboard will NOT work until you apply a fix.
    echo.
    echo Options:
    echo   A. Re-run FIX_KERAS_IMPORT.bat (Option A)
    echo   B. Try Option B (upgrade PyTorch to 2.6.0)
    echo.
) else (
    echo ✗ RESTORE FAILED
    echo.
    echo Some items could not be restored.
    echo Please check file permissions and paths.
    echo.
)

pause
