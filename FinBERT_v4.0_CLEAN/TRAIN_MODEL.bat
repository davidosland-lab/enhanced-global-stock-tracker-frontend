@echo off
REM ============================================================================
REM  FinBERT v4.0 Enhanced - Model Training Script (Windows 11)
REM  Train LSTM models for specific stock symbols
REM ============================================================================

echo.
echo ============================================================================
echo   FinBERT v4.0 ENHANCED - Model Training
echo ============================================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run INSTALL_WINDOWS11_ENHANCED.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check TensorFlow installation
python -c "import tensorflow" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: TensorFlow is not installed!
    echo.
    echo Training will use lightweight fallback method without TensorFlow.
    echo For full LSTM training, install TensorFlow:
    echo   venv\Scripts\activate
    echo   pip install tensorflow==2.15.0
    echo.
    echo Press any key to continue with fallback training...
    pause >nul
    echo.
)

REM Get symbol from user
echo Enter stock symbol to train:
echo   Examples:
echo     - US stocks: AAPL, MSFT, GOOGL, AMZN, TSLA
echo     - Australian stocks: CBA.AX, BHP.AX, WBC.AX
echo.
set /p SYMBOL="Symbol: "

if "%SYMBOL%"=="" (
    echo ERROR: No symbol entered
    pause
    exit /b 1
)

REM Get epochs from user
echo.
echo Enter number of epochs (10-200, recommended 50):
set /p EPOCHS="Epochs (default 50): "

if "%EPOCHS%"=="" (
    set EPOCHS=50
)

REM Confirm training
echo.
echo ============================================================================
echo   Training Configuration
echo ============================================================================
echo   Symbol:   %SYMBOL%
echo   Epochs:   %EPOCHS%
echo   Sequence: 30 (default)
echo ============================================================================
echo.
set /p CONFIRM="Start training? (y/n): "

if /i not "%CONFIRM%"=="y" (
    echo Training cancelled
    pause
    exit /b 0
)

REM Start training
echo.
echo Starting training for %SYMBOL%...
echo This may take 5-20 minutes depending on epochs and hardware.
echo.
echo ============================================================================
echo.

python models/train_lstm.py --symbol %SYMBOL% --epochs %EPOCHS% --sequence_length 30

REM Check if training was successful
if errorlevel 1 (
    echo.
    echo ============================================================================
    echo   Training Failed or Incomplete
    echo ============================================================================
    echo.
    echo Possible reasons:
    echo   - Invalid symbol
    echo   - Network connection issues
    echo   - Insufficient data for symbol
    echo   - TensorFlow not installed (using fallback)
    echo.
    echo Try:
    echo   - Check symbol is correct (e.g., AAPL not Apple)
    echo   - For ASX stocks, use .AX suffix (e.g., CBA.AX)
    echo   - Ensure internet connection is active
    echo   - Install TensorFlow for full LSTM training
    echo.
) else (
    echo.
    echo ============================================================================
    echo   Training Complete!
    echo ============================================================================
    echo.
    echo Model saved to: models/lstm_%SYMBOL%_metadata.json
    echo.
    echo Next steps:
    echo   1. Restart the server (START_V4_ENHANCED.bat)
    echo   2. Open http://localhost:5001
    echo   3. Analyze %SYMBOL% to see new predictions
    echo.
    echo Or train more symbols by running this script again
    echo.
)

pause
