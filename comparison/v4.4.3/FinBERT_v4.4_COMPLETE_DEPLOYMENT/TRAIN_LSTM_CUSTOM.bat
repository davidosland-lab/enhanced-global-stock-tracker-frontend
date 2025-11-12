@echo off
REM ==============================================================================
REM  Custom LSTM Training - User-Defined Stock Selection
REM  Choose your own stocks to train
REM ==============================================================================

echo.
echo ==============================================================================
echo   CUSTOM LSTM TRAINING
echo ==============================================================================
echo.
echo This tool allows you to choose which stocks to train:
echo.
echo   Option 1: Use pre-defined lists (Top 10, US Tech, Australian, etc.)
echo   Option 2: Enter stock symbols manually
echo   Option 3: Load from a text file
echo.
echo Expected time: 10-15 minutes per stock
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

REM Run custom training
echo.
echo ==============================================================================
echo   Starting Custom LSTM Training...
echo ==============================================================================
echo.

python train_lstm_custom.py --interactive

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
    echo    START_FINBERT.bat
    echo.
)

pause
