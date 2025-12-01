@echo off
REM ============================================================================
REM Keras 3 Model Saving Fix - Automatic Installation
REM ============================================================================
REM
REM PROBLEM: Keras 3.11.3 requires save_format='h5' parameter
REM SYMPTOM: Models train but don't save (only JSON metadata created)
REM IMPACT:  Pipeline retrains all 139 models every run (~2 hours wasted)
REM
REM This script automatically applies the fix to lstm_predictor.py
REM ============================================================================

echo.
echo ============================================================================
echo KERAS 3 MODEL SAVING FIX - AUTOMATIC INSTALLER
echo ============================================================================
echo.

REM Check if we're in the right directory
if not exist "finbert_v4.4.4\models\lstm_predictor.py" (
    echo [ERROR] Cannot find finbert_v4.4.4\models\lstm_predictor.py
    echo.
    echo Please run this script from C:\Users\david\AATelS directory
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo [STEP 1] Checking Python environment...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please ensure Python is installed and in PATH
    pause
    exit /b 1
)

python --version

echo.
echo [STEP 2] Checking TensorFlow and Keras versions...
echo.

python -c "import tensorflow as tf; import keras; print(f'TensorFlow: {tf.__version__}'); print(f'Keras: {keras.__version__}')" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] TensorFlow or Keras not installed!
    echo Please run: pip install tensorflow keras
    pause
    exit /b 1
)

python -c "import tensorflow as tf; import keras; print(f'TensorFlow: {tf.__version__}'); print(f'Keras: {keras.__version__}')"

echo.
echo [STEP 3] Creating backup of original file...
echo.

set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

set BACKUP_FILE=finbert_v4.4.4\models\lstm_predictor.py.backup_%TIMESTAMP%

copy "finbert_v4.4.4\models\lstm_predictor.py" "%BACKUP_FILE%" >nul

if exist "%BACKUP_FILE%" (
    echo [OK] Backup created: %BACKUP_FILE%
) else (
    echo [ERROR] Failed to create backup!
    pause
    exit /b 1
)

echo.
echo [STEP 4] Applying Keras 3 fix...
echo.

python apply_keras_fix.py

if errorlevel 1 (
    echo.
    echo [ERROR] Fix application failed!
    echo Restoring backup...
    copy "%BACKUP_FILE%" "finbert_v4.4.4\models\lstm_predictor.py" >nul
    echo Backup restored.
    pause
    exit /b 1
)

echo.
echo [STEP 5] Verifying fix...
echo.

python verify_keras_fix.py

if errorlevel 1 (
    echo.
    echo [ERROR] Verification failed!
    echo Restoring backup...
    copy "%BACKUP_FILE%" "finbert_v4.4.4\models\lstm_predictor.py" >nul
    echo Backup restored.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo FIX APPLIED SUCCESSFULLY!
echo ============================================================================
echo.
echo What was fixed:
echo   - Added save_format='h5' parameter to model.save() call
echo   - Added Keras 3 compatibility check
echo   - Added fallback for Keras 2.x
echo   - Added detailed error logging
echo.
echo Backup saved to:
echo   %BACKUP_FILE%
echo.
echo ============================================================================
echo NEXT STEPS
echo ============================================================================
echo.
echo 1. TEST WITH ONE MODEL (5 minutes):
echo    python finbert_v4.4.4\models\train_lstm.py --symbol BHP.AX --epochs 5
echo.
echo    Expected: File created: models\BHP.AX_lstm_model.h5 (~500KB)
echo.
echo 2. RUN FULL PIPELINE:
echo    RUN_PIPELINE_TEST.bat
echo.
echo    With this fix:
echo    - Models save correctly as .h5 files
echo    - Next run loads existing models (fast!)
echo    - Pipeline time: 30-45 min (instead of 2+ hours)
echo.
echo 3. VERIFY MODELS ARE SAVED:
echo    dir /b models\screening\models\*.h5
echo.
echo    You should see: A2M.AX_lstm_model.h5, BHP.AX_lstm_model.h5, etc.
echo.
echo ============================================================================
echo.

pause
