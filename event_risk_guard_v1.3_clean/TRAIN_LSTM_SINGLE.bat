@echo off
REM ====================================================================
REM LSTM Single Stock Training - Quick Training for One Stock
REM Fast training for testing or updating a specific stock
REM Expected Time: 10-15 minutes
REM ====================================================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo.
echo ========================================================================
echo   LSTM SINGLE STOCK TRAINING
echo ========================================================================
echo.

REM Get symbol from command line or prompt
if "%~1"=="" (
    echo No stock symbol provided.
    echo.
    echo You can provide a symbol in two ways:
    echo   1. Command line: TRAIN_LSTM_SINGLE.bat CBA.AX
    echo   2. Interactive: Enter symbol when prompted below
    echo.
    echo Examples of valid symbols:
    echo   - CBA.AX  ^(Commonwealth Bank^)
    echo   - ANZ.AX  ^(ANZ Banking Group^)
    echo   - BHP.AX  ^(BHP Group^)
    echo   - AAPL    ^(Apple Inc.^)
    echo   - MSFT    ^(Microsoft^)
    echo.
    set /p SYMBOL="Enter stock symbol (or press Ctrl+C to cancel): "
    
    REM Check if symbol was entered (use a call to a subroutine to handle delayed expansion)
    if not defined SYMBOL (
        echo.
        echo [ERROR] No symbol entered. Exiting.
        echo.
        pause
        exit /b 1
    )
) else (
    set SYMBOL=%~1
)

REM Now enable delayed expansion for the rest of the script
setlocal enabledelayedexpansion

REM Verify we have a symbol
if not defined SYMBOL (
    echo.
    echo [ERROR] Symbol variable not set. Exiting.
    echo.
    pause
    exit /b 1
)

echo Training LSTM model for: !SYMBOL!
echo.
echo Training Parameters:
echo   - Epochs: 50
echo   - Sequence Length: 60 days
echo   - Batch Size: 32
echo   - Validation Split: 20%%
echo   - Training Data: 2 years historical
echo.
echo Expected time: 10-15 minutes
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if TensorFlow is installed
python -c "import tensorflow" 2>nul
if errorlevel 1 (
    echo [ERROR] TensorFlow not installed. Install with:
    echo   pip install tensorflow^>=2.13.0
    pause
    exit /b 1
)

REM Check if models directory exists
if not exist "models" mkdir models

echo Starting training in 3 seconds...
timeout /t 3 /nobreak >nul

REM Train the model
python train_lstm_custom.py --symbols "!SYMBOL!"

if errorlevel 1 (
    echo.
    echo [ERROR] Training failed for !SYMBOL!
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo   TRAINING COMPLETED FOR !SYMBOL!
echo ========================================================================
echo.
echo Model saved to: models\lstm_!SYMBOL!_model.keras
echo Metadata saved to: models\lstm_!SYMBOL!_metadata.json
echo.
echo You can now use this stock in predictions.
echo.
pause
