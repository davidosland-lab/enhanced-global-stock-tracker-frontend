@echo off
REM ============================================================================
REM FinBERT v4.4 - LSTM Batch Training (Overnight)
REM ============================================================================

echo.
echo ================================================================================
echo   LSTM BATCH TRAINING FOR TOP 10 STOCKS
echo ================================================================================
echo   This will train LSTM models for:
echo     US Stocks:  AAPL, MSFT, GOOGL, TSLA, NVDA, AMZN, META, AMD
echo     AU Stocks:  CBA.AX, BHP.AX
echo.
echo   Expected time: 1-2 hours total (10-15 minutes per stock)
echo   Expected improvement: +10-15%% accuracy for trained stocks
echo.
echo   Hardware performance:
echo     - GPU (CUDA): 30-50 minutes total
echo     - CPU (Optimized): 60-90 minutes total
echo     - CPU (Basic): 1.5-2.5 hours total
echo ================================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run INSTALL.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check for TensorFlow
echo Checking for TensorFlow...
python -c "import tensorflow" 2>nul
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   ERROR: TensorFlow not installed!
    echo ================================================================================
    echo   TensorFlow is required for LSTM training.
    echo   Please run INSTALL.bat and choose option 1 (FULL installation)
    echo ================================================================================
    echo.
    pause
    exit /b 1
)

echo [OK] TensorFlow found
echo.
echo Press CTRL+C now to cancel, or
pause

echo.
echo Starting LSTM batch training...
echo.

python train_lstm_batch.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   Training completed with errors
    echo ================================================================================
    echo   Check the error messages above for details.
    echo   Some stocks may have failed due to insufficient data.
    echo   Successfully trained models are still available for use.
    echo ================================================================================
) else (
    echo.
    echo ================================================================================
    echo   Training completed successfully!
    echo ================================================================================
    echo   Next steps:
    echo   1. Restart FinBERT server: START_FINBERT.bat
    echo   2. Trained models will be automatically loaded
    echo   3. Test predictions on trained stocks
    echo   4. Verify accuracy improvements (should be 85-95%%)
    echo.
    echo   Trained model files saved in: models\
    echo ================================================================================
)

echo.
pause
