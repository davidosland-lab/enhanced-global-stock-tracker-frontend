@echo off
REM ============================================================================
REM LSTM Model Training Script - FIXED VERSION
REM 
REM Trains LSTM models for stale stocks based on priority queue.
REM Can be run manually or scheduled as part of overnight workflow.
REM 
REM FIXED: Better error handling, pauses, auto-fix config issues
REM 
REM Usage:
REM   RUN_LSTM_TRAINING_FIXED.bat                - Train priority stocks
REM   RUN_LSTM_TRAINING_FIXED.bat --symbols ANZ.AX CBA.AX - Train specific
REM   RUN_LSTM_TRAINING_FIXED.bat --max-stocks 5 - Limit to 5 stocks
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo LSTM MODEL TRAINING - STARTING
echo ============================================================================
echo Start Time: %date% %time%
echo.

REM Change to script directory
cd /d "%~dp0"
echo Current Directory: %CD%
echo.
timeout /t 1 /nobreak >nul

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
    timeout /t 1 /nobreak >nul
) else (
    echo [WARNING] Virtual environment not found - using system Python
    timeout /t 2 /nobreak >nul
)

echo.
echo [INFO] Checking Python and dependencies...
python --version
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Checking TensorFlow installation...
python -c "import tensorflow; print('TensorFlow version:', tensorflow.__version__)" 2>nul
if errorlevel 1 (
    echo [WARNING] TensorFlow not found!
    echo LSTM training requires TensorFlow.
    echo.
    echo To install: pip install tensorflow>=2.13.0
    echo Or run: INSTALL_DEPENDENCIES.bat
    echo.
    set /p CONTINUE="Continue anyway? (Y/N): "
    if /i not "!CONTINUE!"=="Y" (
        echo Training cancelled.
        pause
        exit /b 1
    )
) else (
    echo [OK] TensorFlow is installed
)

timeout /t 1 /nobreak >nul

echo.
echo [INFO] Verifying configuration files...

REM Check and auto-fix asx_sectors.json
if not exist "models\config\asx_sectors.json" (
    echo [WARNING] asx_sectors.json not found
    echo.
    if exist "finbert_v4.4.4\models\config\asx_sectors.json" (
        echo [FIX] Copying from finbert_v4.4.4...
        if not exist "models\config" mkdir "models\config"
        copy "finbert_v4.4.4\models\config\asx_sectors.json" "models\config\asx_sectors.json" >nul 2>&1
        echo [OK] Configuration copied
    ) else (
        echo [ERROR] Cannot find source configuration
        echo.
        pause
        exit /b 1
    )
) else (
    echo [OK] asx_sectors.json exists
)

timeout /t 1 /nobreak >nul

REM Create logs directory
if not exist "logs\lstm_training" (
    echo [INFO] Creating logs directory...
    mkdir "logs\lstm_training"
)

REM Create models directory for trained models
if not exist "models\trained" (
    echo [INFO] Creating models\trained directory...
    mkdir "models\trained"
)

echo.
echo ============================================================================
echo STARTING LSTM MODEL TRAINING
echo ============================================================================
echo.
echo [INFO] This may take a while (5-15 minutes per stock)
echo [INFO] Progress will be shown below
echo.
timeout /t 2 /nobreak >nul

echo [START] %date% %time%
echo.

REM Run LSTM training with unbuffered output
python -u models/screening/lstm_trainer.py --mode train %*
set TRAIN_EXIT=%ERRORLEVEL%

echo.
echo [END] %date% %time%
echo.

REM Check exit code
if !TRAIN_EXIT! neq 0 (
    echo.
    echo ============================================================================
    echo [ERROR] LSTM training failed (Exit code: !TRAIN_EXIT!)
    echo ============================================================================
    echo End Time: %date% %time%
    echo.
    
    echo Possible issues:
    echo - TensorFlow not installed properly
    echo - Insufficient training data for stocks
    echo - Memory issues (requires 2-4GB RAM)
    echo - Network issues fetching stock data
    echo.
    
    echo Check logs at: logs\lstm_training\lstm_training.log
    echo.
    
    timeout /t 5 /nobreak >nul
    
    REM Send error notification if module exists
    if exist "models\screening\send_notification.py" (
        echo [INFO] Sending error notification...
        python models\screening\send_notification.py --type error --error-message "LSTM training failed" --phase "LSTM Training" 2>nul
    )
    
    pause
    exit /b !TRAIN_EXIT!
)

REM Success
echo.
echo ============================================================================
echo [SUCCESS] LSTM training completed successfully
echo ============================================================================
echo End Time: %date% %time%
echo.

echo Next steps:
echo - Run CHECK_MODEL_STATUS.bat to verify models
echo - Run RUN_OVERNIGHT_SCREENER.bat to use new models
echo.

REM Send success notification if module exists
if exist "models\screening\send_notification.py" (
    echo [INFO] Sending success notification...
    python models\screening\send_notification.py --type success 2>nul
)

echo.
pause
exit /b 0
