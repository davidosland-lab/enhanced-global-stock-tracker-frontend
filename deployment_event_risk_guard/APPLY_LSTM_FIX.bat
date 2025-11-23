@echo off
REM ====================================================================
REM Auto-Fix Script for TRAIN_LSTM_OVERNIGHT.bat TensorFlow Detection
REM Fixes the errorlevel check issue on Windows 11
REM ====================================================================

echo.
echo ========================================================================
echo   AUTO-FIX: TRAIN_LSTM_OVERNIGHT.bat TensorFlow Detection
echo ========================================================================
echo.
echo This will fix the TensorFlow detection issue in TRAIN_LSTM_OVERNIGHT.bat
echo.
echo What this does:
echo   1. Creates backup of original file
echo   2. Fixes line 57 (TensorFlow detection check)
echo   3. Verifies the fix was applied
echo.

REM Check if the file exists
if not exist "TRAIN_LSTM_OVERNIGHT.bat" (
    echo [ERROR] TRAIN_LSTM_OVERNIGHT.bat not found in current directory
    echo.
    echo Please run this script from: C:\Users\david\AASS\deployment_event_risk_guard
    echo.
    pause
    exit /b 1
)

echo [INFO] Found TRAIN_LSTM_OVERNIGHT.bat
echo.

REM Create backup
echo Creating backup...
copy /Y "TRAIN_LSTM_OVERNIGHT.bat" "TRAIN_LSTM_OVERNIGHT.bat.backup" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Could not create backup file
    echo Try running this as Administrator
    pause
    exit /b 1
)
echo [OK] Backup created: TRAIN_LSTM_OVERNIGHT.bat.backup
echo.

REM Apply the fix using PowerShell
echo Applying fix...
powershell -Command "(Get-Content 'TRAIN_LSTM_OVERNIGHT.bat') -replace 'python -c \"import tensorflow; print\(f''TensorFlow \{tensorflow\.__version__\} detected''\)\" 2>nul', 'python -c \"import tensorflow\" 2>nul' | Set-Content 'TRAIN_LSTM_OVERNIGHT.bat'"

if errorlevel 1 (
    echo [ERROR] Fix failed
    echo Restoring backup...
    copy /Y "TRAIN_LSTM_OVERNIGHT.bat.backup" "TRAIN_LSTM_OVERNIGHT.bat" >nul
    echo.
    echo Please use Manual Fix method (see QUICK_FIX_GUIDE.txt)
    pause
    exit /b 1
)

echo [OK] Fix applied
echo.

REM Verify the fix
echo Verifying fix...
findstr /C:"python -c \"import tensorflow\" 2>nul" "TRAIN_LSTM_OVERNIGHT.bat" >nul
if errorlevel 1 (
    echo [WARNING] Could not verify fix was applied correctly
    echo.
    echo Please manually check line 57 in TRAIN_LSTM_OVERNIGHT.bat
    echo It should be: python -c "import tensorflow" 2>nul
    echo.
) else (
    echo [OK] Fix verified successfully
    echo.
)

echo ========================================================================
echo   FIX COMPLETED
echo ========================================================================
echo.
echo Changes made:
echo   - Original file backed up to: TRAIN_LSTM_OVERNIGHT.bat.backup
echo   - Fixed TensorFlow detection check (line 57)
echo.
echo Next Steps:
echo   1. Run: TRAIN_LSTM_OVERNIGHT.bat
echo   2. Verify you see: [OK] TensorFlow is installed
echo   3. Training should start automatically
echo.
echo If there are any issues:
echo   - Restore backup: copy TRAIN_LSTM_OVERNIGHT.bat.backup TRAIN_LSTM_OVERNIGHT.bat
echo   - See detailed guide: FIX_WINDOWS_LSTM_OVERNIGHT.md
echo.
echo ========================================================================
echo.
pause
