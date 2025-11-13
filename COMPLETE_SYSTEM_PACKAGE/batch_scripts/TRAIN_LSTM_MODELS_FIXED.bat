@echo off
REM ============================================================================
REM LSTM Model Training Script - FIXED VERSION
REM 
REM Trains LSTM models for stocks using the screening system.
REM Works from batch_scripts directory with correct paths.
REM 
REM Usage:
REM   TRAIN_LSTM_MODELS_FIXED.bat                    - Train with fallback config
REM   TRAIN_LSTM_MODELS_FIXED.bat --max-stocks 5    - Train max 5 stocks
REM   TRAIN_LSTM_MODELS_FIXED.bat --symbols CBA.AX  - Train specific stocks
REM ============================================================================

echo.
echo ============================================================================
echo LSTM MODEL TRAINING - STARTING
echo ============================================================================
echo Start Time: %date% %time%
echo.
echo Current Directory: %CD%
echo.

REM Get the batch script directory
set BATCH_DIR=%~dp0
echo Batch Script Directory: %BATCH_DIR%

REM Change to parent directory (COMPLETE_SYSTEM_PACKAGE)
cd /d "%BATCH_DIR%\.."
echo Package Root Directory: %CD%
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found - using system Python
)
echo.

REM Check Python and dependencies
echo [INFO] Checking Python and dependencies...
python --version
echo.

REM Check TensorFlow
echo [INFO] Checking TensorFlow installation...
python -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__)" 2>nul
if errorlevel 1 (
    echo [ERROR] TensorFlow not installed
    echo [INFO] Install with: pip install tensorflow keras
    echo.
    pause
    exit /b 1
) else (
    echo [OK] TensorFlow is installed
)
echo.

REM Verify configuration files exist
echo [INFO] Verifying configuration files...
if not exist "models\config\asx_sectors.json" (
    echo [ERROR] Configuration file not found: models\config\asx_sectors.json
    echo [INFO] Current directory: %CD%
    echo [INFO] Please ensure you're running from the package root or batch_scripts folder
    echo.
    pause
    exit /b 1
)
echo [OK] Configuration files found
echo.

REM Create necessary directories
if not exist "logs" mkdir "logs"
if not exist "logs\lstm_training" mkdir "logs\lstm_training"
if not exist "models\lstm" mkdir "models\lstm"
if not exist "reports" mkdir "reports"
if not exist "reports\pipeline_state" mkdir "reports\pipeline_state"

REM Run LSTM training
echo [INFO] Starting LSTM model training...
echo [INFO] Using smart fallback: Will use pipeline state if available, else ASX sectors config
echo.

python -u models\screening\lstm_trainer.py --mode train %*

REM Check exit code
if errorlevel 1 (
    echo.
    echo ============================================================================
    echo [ERROR] LSTM training failed
    echo ============================================================================
    echo End Time: %date% %time%
    echo.
    echo [INFO] Check logs in: logs\lstm_training\
    echo [INFO] Try running with fewer stocks: TRAIN_LSTM_MODELS_FIXED.bat --max-stocks 2
    echo.
    pause
    exit /b 1
)

REM Success
echo.
echo ============================================================================
echo [SUCCESS] LSTM training completed successfully
echo ============================================================================
echo End Time: %date% %time%
echo.
echo [INFO] Trained models saved to: models\lstm\
echo [INFO] Training logs saved to: logs\lstm_training\
echo.

REM Send success notification if module exists
if exist "models\screening\send_notification.py" (
    echo [INFO] Sending success notification...
    python models\screening\send_notification.py --type success
)

pause
exit /b 0
