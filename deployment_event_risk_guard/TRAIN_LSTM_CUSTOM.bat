@echo off
REM ====================================================================
REM LSTM Custom Training - Interactive Stock Selection
REM Allows you to select which stocks to train
REM Expected Time: 10-15 minutes per stock
REM ====================================================================

echo.
echo ========================================================================
echo   LSTM CUSTOM TRAINING - Interactive Mode
echo ========================================================================
echo.
echo This script provides flexible stock selection options:
echo.
echo Mode 1: Pre-defined Lists
echo   - Top 10 Global Stocks (US + ASX)
echo   - US Tech Giants (AAPL, MSFT, GOOGL, NVDA, AMD, INTC)
echo   - US Mega Caps (AAPL, MSFT, GOOGL, AMZN, META, TSLA)
echo   - Australian ASX Stocks (CBA.AX, BHP.AX, WBC.AX, etc.)
echo   - UK FTSE Stocks (BP.L, SHEL.L, HSBA.L, etc.)
echo.
echo Mode 2: Manual Entry
echo   - Enter symbols separated by commas
echo   - Example: AAPL,MSFT,GOOGL or CBA.AX,BHP.AX,CSL.AX
echo.
echo Mode 3: Load from File
echo   - Plain text: one symbol per line
echo   - JSON format: [{"symbol": "AAPL", "name": "Apple Inc."}, ...]
echo.
echo Training Parameters:
echo   - Epochs: 50
echo   - Sequence Length: 60 days
echo   - Batch Size: 32
echo   - Validation Split: 20%%
echo   - Training Data: 2 years historical
echo.
echo Command-line Options (skip interactive mode):
echo   --symbols AAPL,MSFT,GOOGL    Train specific symbols
echo   --file stocks.txt            Load from file
echo   --list australian            Use pre-defined list
echo.
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if TensorFlow is installed
echo Checking for TensorFlow installation...
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} detected')" 2>nul
if errorlevel 1 (
    echo.
    echo [WARNING] TensorFlow not detected
    echo.
    echo LSTM training requires TensorFlow. Install with:
    echo   pip install tensorflow^>=2.13.0
    echo.
    echo Or install all ML dependencies:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [OK] TensorFlow is installed
echo.

REM Check if models directory exists
if not exist "models" (
    echo [INFO] Creating models directory...
    mkdir models
)

REM Check if command-line arguments were provided
if "%~1"=="" (
    REM Interactive mode
    echo Starting interactive training...
    echo.
    python train_lstm_custom.py --interactive
) else (
    REM Pass all arguments to the Python script
    echo Starting training with provided arguments...
    echo.
    python train_lstm_custom.py %*
)

if errorlevel 1 (
    echo.
    echo ========================================================================
    echo   TRAINING FAILED
    echo ========================================================================
    echo.
    echo Check the error messages above for details.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo   TRAINING COMPLETED
echo ========================================================================
echo.
echo Trained models saved in: models\
echo.
echo Next Steps:
echo   1. Verify models: dir models\lstm_*_model.keras
echo   2. Run verification: VERIFY_INSTALLATION.bat
echo   3. Run overnight scan: RUN_OVERNIGHT_SCAN.bat
echo.
echo ========================================================================
echo.
pause
