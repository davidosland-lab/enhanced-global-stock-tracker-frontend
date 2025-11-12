@echo off
REM ====================================================================
REM LSTM Overnight Training for Event Risk Guard System
REM Trains LSTM models for top ASX stocks (Event Calendar focus)
REM Expected Time: 1.5-2 hours for 10 stocks
REM ====================================================================

echo.
echo ========================================================================
echo   LSTM OVERNIGHT TRAINING - Event Risk Guard ASX Stocks
echo ========================================================================
echo.
echo This script will train LSTM models for 10 priority ASX stocks
echo Focus: Stocks from event_calendar.csv (Basel III, Earnings, Dividends)
echo.
echo Training Parameters:
echo   - Epochs: 50
echo   - Sequence Length: 60 days
echo   - Batch Size: 32
echo   - Validation Split: 20%%
echo   - Training Data: 2 years historical
echo.
echo Expected Time: ~10-15 minutes per stock (Total: 1.5-2 hours)
echo.
echo Priority Stocks:
echo   1. CBA.AX  - Commonwealth Bank (Basel III)
echo   2. ANZ.AX  - ANZ Banking Group (Earnings)
echo   3. NAB.AX  - NAB (Basel III)
echo   4. WBC.AX  - Westpac (Earnings)
echo   5. MQG.AX  - Macquarie Group (Earnings)
echo   6. BHP.AX  - BHP Group (Dividend)
echo   7. RIO.AX  - Rio Tinto (Dividend)
echo   8. CSL.AX  - CSL Limited (Earnings)
echo   9. WES.AX  - Wesfarmers (Earnings)
echo  10. BOQ.AX  - Bank of Queensland (Basel III)
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
    echo LSTM training requires TensorFlow. You have two options:
    echo.
    echo Option 1: Install TensorFlow now
    echo   Run: pip install tensorflow^>=2.13.0
    echo   Time: ~5 minutes
    echo.
    echo Option 2: Install from requirements.txt (includes all ML packages)
    echo   Run: pip install -r requirements.txt
    echo   Time: ~15 minutes (downloads ~2.5 GB)
    echo.
    echo After installing, run this script again.
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

echo ========================================================================
echo   STARTING LSTM TRAINING
echo ========================================================================
echo.
echo Training will begin in 5 seconds...
echo Press Ctrl+C to cancel
echo.
timeout /t 5 /nobreak >nul

REM Run the training script
python train_lstm_batch.py

if errorlevel 1 (
    echo.
    echo ========================================================================
    echo   TRAINING FAILED
    echo ========================================================================
    echo.
    echo Check the error messages above for details.
    echo.
    echo Common issues:
    echo   1. Missing TensorFlow: pip install tensorflow^>=2.13.0
    echo   2. Insufficient memory: Close other programs or train fewer stocks
    echo   3. Network issues: Check internet connection for data download
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo   TRAINING COMPLETED SUCCESSFULLY
echo ========================================================================
echo.
echo Trained models are saved in: models\
echo Model format: lstm_SYMBOL_model.keras
echo Metadata format: lstm_SYMBOL_metadata.json
echo.
echo Next Steps:
echo   1. Verify models: Check models\ directory
echo   2. Run verification: VERIFY_INSTALLATION.bat
echo   3. Run overnight scan: RUN_OVERNIGHT_SCAN.bat
echo.
echo The system will now use LSTM predictions for trained stocks.
echo Prediction weights: LSTM 45%%, Trend 25%%, Technical 15%%, FinBERT 15%%
echo.
echo ========================================================================
echo.
pause
