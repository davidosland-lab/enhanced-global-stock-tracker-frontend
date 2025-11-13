@echo off
REM ====================================================================
REM Quick Fix for TRAIN_LSTM_SINGLE.bat Variable Scope Issue
REM This patches your existing TRAIN_LSTM_SINGLE.bat file in-place
REM ====================================================================

echo.
echo ========================================================================
echo   QUICK FIX: TRAIN_LSTM_SINGLE.bat Variable Scope
echo ========================================================================
echo.
echo This will fix the "expected one argument" error when entering symbols
echo interactively.
echo.
echo Backing up original file...

REM Backup original file
copy TRAIN_LSTM_SINGLE.bat TRAIN_LSTM_SINGLE.bat.backup >nul 2>&1

if not errorlevel 1 (
    echo ✓ Backup created: TRAIN_LSTM_SINGLE.bat.backup
) else (
    echo ✗ Failed to create backup. Continuing anyway...
)

echo.
echo Creating fixed version...

REM Create the fixed version
(
echo @echo off
echo setlocal enabledelayedexpansion
echo REM ====================================================================
echo REM LSTM Single Stock Training - Quick Training for One Stock
echo REM Fast training for testing or updating a specific stock
echo REM Expected Time: 10-15 minutes
echo REM ====================================================================
echo.
echo echo.
echo echo ========================================================================
echo echo   LSTM SINGLE STOCK TRAINING
echo echo ========================================================================
echo echo.
echo.
echo if "%%~1"=="" ^(
echo     echo No stock symbol provided.
echo     echo.
echo     echo You can provide a symbol in two ways:
echo     echo   1. Command line: TRAIN_LSTM_SINGLE.bat CBA.AX
echo     echo   2. Interactive: Enter symbol when prompted below
echo     echo.
echo     echo Examples of valid symbols:
echo     echo   - CBA.AX  ^(Commonwealth Bank^)
echo     echo   - ANZ.AX  ^(ANZ Banking Group^)
echo     echo   - BHP.AX  ^(BHP Group^)
echo     echo   - AAPL    ^(Apple Inc.^)
echo     echo   - MSFT    ^(Microsoft^)
echo     echo.
echo     set /p SYMBOL="Enter stock symbol (or press Ctrl+C to cancel): "
echo     
echo     if "!SYMBOL!"=="" ^(
echo         echo.
echo         echo [ERROR] No symbol entered. Exiting.
echo         echo.
echo         pause
echo         exit /b 1
echo     ^)
echo ^) else ^(
echo     set SYMBOL=%%~1
echo ^)
echo.
echo echo Training LSTM model for: !SYMBOL!
echo echo.
echo echo Training Parameters:
echo echo   - Epochs: 50
echo echo   - Sequence Length: 60 days
echo echo   - Batch Size: 32
echo echo   - Validation Split: 20%%%%
echo echo   - Training Data: 2 years historical
echo echo.
echo echo Expected time: 10-15 minutes
echo echo.
echo.
echo REM Check if Python is installed
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo [ERROR] Python is not installed or not in PATH
echo     pause
echo     exit /b 1
echo ^)
echo.
echo REM Check if TensorFlow is installed
echo python -c "import tensorflow" 2^>nul
echo if errorlevel 1 ^(
echo     echo [ERROR] TensorFlow not installed. Install with:
echo     echo   pip install tensorflow^>=2.13.0
echo     pause
echo     exit /b 1
echo ^)
echo.
echo REM Check if models directory exists
echo if not exist "models" mkdir models
echo.
echo echo Starting training in 3 seconds...
echo timeout /t 3 /nobreak ^>nul
echo.
echo REM Train the model
echo python train_lstm_custom.py --symbols !SYMBOL!
echo.
echo if errorlevel 1 ^(
echo     echo.
echo     echo [ERROR] Training failed for !SYMBOL!
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo.
echo echo ========================================================================
echo echo   TRAINING COMPLETED FOR !SYMBOL!
echo echo ========================================================================
echo echo.
echo echo Model saved to: models\lstm_!SYMBOL!_model.keras
echo echo Metadata saved to: models\lstm_!SYMBOL!_metadata.json
echo echo.
echo echo You can now use this stock in predictions.
echo echo.
echo pause
) > TRAIN_LSTM_SINGLE_FIXED.bat

echo ✓ Fixed version created: TRAIN_LSTM_SINGLE_FIXED.bat

echo.
echo Replacing original file...

REM Replace the original file
move /Y TRAIN_LSTM_SINGLE_FIXED.bat TRAIN_LSTM_SINGLE.bat >nul 2>&1

if not errorlevel 1 (
    echo ✓ TRAIN_LSTM_SINGLE.bat has been patched successfully!
) else (
    echo ✗ Failed to replace file. You may need Administrator privileges.
    echo.
    echo Manual fix:
    echo   1. Delete TRAIN_LSTM_SINGLE.bat
    echo   2. Rename TRAIN_LSTM_SINGLE_FIXED.bat to TRAIN_LSTM_SINGLE.bat
)

echo.
echo ========================================================================
echo   FIX APPLIED
echo ========================================================================
echo.
echo The variable scope issue has been fixed.
echo.
echo Test the fix:
echo   TRAIN_LSTM_SINGLE.bat
echo   (Enter CBA.AX when prompted)
echo.
echo If you need to restore the original:
echo   del TRAIN_LSTM_SINGLE.bat
echo   ren TRAIN_LSTM_SINGLE.bat.backup TRAIN_LSTM_SINGLE.bat
echo.
pause
