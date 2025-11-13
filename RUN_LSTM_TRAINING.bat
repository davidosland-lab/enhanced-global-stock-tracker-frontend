@echo off
REM ============================================================================
REM LSTM Model Training Script
REM 
REM Trains LSTM models for stale stocks based on priority queue.
REM Can be run manually or scheduled as part of overnight workflow.
REM 
REM Usage:
REM   RUN_LSTM_TRAINING.bat              - Train priority stocks from pipeline
REM   RUN_LSTM_TRAINING.bat --symbols ANZ.AX CBA.AX - Train specific stocks
REM   RUN_LSTM_TRAINING.bat --max-stocks 10 - Limit training to 10 stocks
REM ============================================================================

echo.
echo ============================================================================
echo LSTM MODEL TRAINING - STARTING
echo ============================================================================
echo Start Time: %date% %time%
echo.

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found - using system Python
)

REM Create logs directory if it doesn't exist
if not exist "logs\lstm_training" mkdir "logs\lstm_training"

REM Run LSTM training
echo.
echo [INFO] Starting LSTM model training...
echo.

python -u models/screening/lstm_trainer.py --mode train %*

REM Check exit code
if errorlevel 1 (
    echo.
    echo ============================================================================
    echo [ERROR] LSTM training failed
    echo ============================================================================
    echo End Time: %date% %time%
    echo.
    
    REM Send error notification if module exists
    if exist "models\screening\send_notification.py" (
        echo [INFO] Sending error notification...
        python models\screening\send_notification.py --type error --error-message "LSTM training failed" --phase "LSTM Training"
    )
    
    exit /b 1
)

REM Success
echo.
echo ============================================================================
echo [SUCCESS] LSTM training completed successfully
echo ============================================================================
echo End Time: %date% %time%
echo.

REM Send success notification if module exists
if exist "models\screening\send_notification.py" (
    echo [INFO] Sending success notification...
    python models\screening\send_notification.py --type success
)

exit /b 0
