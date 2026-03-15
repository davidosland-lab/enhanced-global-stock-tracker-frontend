@echo off
REM ==============================================================================
REM  LSTM Batch Training for Top 10 Stocks
REM  Trains overnight - Expected time: 1-2 hours
REM ==============================================================================

echo.
echo ==============================================================================
echo   LSTM BATCH TRAINING FOR TOP 10 STOCKS
echo ==============================================================================
echo.
echo This will train LSTM models for:
echo   US Stocks:  AAPL, MSFT, GOOGL, TSLA, NVDA, AMZN, META, AMD
echo   AU Stocks:  CBA.AX, BHP.AX
echo.
echo Expected time: 1-2 hours (10-15 minutes per stock)
echo.
echo Recommendation: Run this overnight or during a break
echo.
pause

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if TensorFlow is installed
echo.
echo Checking for TensorFlow...
python -c "import tensorflow; print('✓ TensorFlow version:', tensorflow.__version__)" 2>nul
if errorlevel 1 (
    echo.
    echo ❌ ERROR: TensorFlow not installed!
    echo.
    echo Please install TensorFlow first:
    echo    pip install tensorflow
    echo.
    echo Or run the full installation:
    echo    INSTALL.bat
    echo.
    pause
    exit /b 1
)

REM Run training
echo.
echo ==============================================================================
echo   Starting LSTM Training...
echo ==============================================================================
echo.

python train_lstm_batch.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ Training completed with errors
    echo Check the output above for details
    echo.
) else (
    echo.
    echo ✅ Training completed successfully!
    echo.
    echo All models have been trained and saved.
    echo.
    echo Next: Restart the FinBERT server to use trained models
    echo    START_FINBERT_V4.bat
    echo.
)

pause
