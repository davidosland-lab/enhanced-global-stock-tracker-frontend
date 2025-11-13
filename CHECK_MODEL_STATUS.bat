@echo off
REM ============================================================================
REM LSTM Model Status Checker
REM 
REM Displays statistics about LSTM model training status.
REM Shows fresh models, stale models, and training recommendations.
REM ============================================================================

echo.
echo ============================================================================
echo LSTM MODEL STATUS
echo ============================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat >nul 2>&1
)

REM Show model statistics
python -u models/screening/lstm_trainer.py --mode stats

echo.
echo ============================================================================
echo CHECKING FOR STALE MODELS
echo ============================================================================
echo.

REM Check for stale models
python -u models/screening/lstm_trainer.py --mode check

echo.
echo ============================================================================
echo To train stale models, run: RUN_LSTM_TRAINING.bat
echo ============================================================================
echo.

pause
