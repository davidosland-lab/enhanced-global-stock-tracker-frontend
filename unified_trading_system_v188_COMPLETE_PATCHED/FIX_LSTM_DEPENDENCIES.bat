@echo off
REM ================================================================================
REM FIX LSTM TRAINING - Install Missing Dependencies
REM ================================================================================
REM
REM This fixes LSTM training by ensuring TensorFlow and Keras are installed.
REM Common issue: TensorFlow not installed in FinBERT virtual environment.
REM
REM ================================================================================

echo.
echo ================================================================================
echo   FIX LSTM TRAINING - Install Missing Dependencies
echo ================================================================================
echo.
echo This will install TensorFlow and Keras if they're missing.
echo.

REM Check if we're in the right directory
if not exist "finbert_v4.4.4\venv" (
    echo [ERROR] Cannot find finbert_v4.4.4\venv
    echo.
    echo Please run this from the unified_trading_dashboard_v1.3.15.87_ULTIMATE directory
    echo.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo [OK] Found FinBERT virtual environment
echo.

REM Activate virtual environment
echo Activating FinBERT virtual environment...
call finbert_v4.4.4\venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

REM Check if TensorFlow is installed
echo Checking for TensorFlow...
python -c "import tensorflow" >nul 2>&1

if errorlevel 1 (
    echo [INFO] TensorFlow not found - installing...
    echo.
    echo This may take 5-10 minutes (~500 MB download)
    echo.
    pip install tensorflow keras scikit-learn
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install TensorFlow
        echo.
        echo Try manual installation:
        echo   1. Activate venv: finbert_v4.4.4\venv\Scripts\activate
        echo   2. Install: pip install tensorflow keras scikit-learn
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo [OK] TensorFlow installed successfully
) else (
    echo [OK] TensorFlow already installed
)

echo.

REM Verify installation
echo Verifying installation...
python -c "import tensorflow as tf; import keras; print(f'TensorFlow {tf.__version__}')" 2>nul

if errorlevel 1 (
    echo [WARNING] TensorFlow import test failed
    echo Installation may be incomplete
    echo.
) else (
    echo [OK] TensorFlow verified
)

echo.

REM Check for other dependencies
echo Checking other dependencies...

python -c "import pandas; import numpy; print('OK: pandas, numpy')" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing pandas, numpy...
    pip install pandas numpy
)

python -c "import sklearn; print('OK: scikit-learn')" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing scikit-learn...
    pip install scikit-learn
)

echo.
echo ================================================================================
echo   INSTALLATION COMPLETE
echo ================================================================================
echo.
echo LSTM Training dependencies installed successfully!
echo.
echo Next steps:
echo   1. Restart Flask server if it's running:
echo      - Ctrl+C to stop
echo      - cd finbert_v4.4.4
echo      - python app_finbert_v4_dev.py
echo.
echo   2. Test LSTM training:
echo      - Open: http://localhost:5000
echo      - Click: "Train LSTM Model"
echo      - Enter: AAPL
echo      - Epochs: 30
echo      - Click: "Start Training"
echo.
echo   3. Or test from command line:
echo      - cd finbert_v4.4.4
echo      - python models/train_lstm.py --symbol AAPL --epochs 30
echo.
echo ================================================================================
echo.
pause
