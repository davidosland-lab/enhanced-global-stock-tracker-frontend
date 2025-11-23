@echo off
REM ====================================================================
REM LSTM Overnight Training for Event Risk Guard System
REM Trains LSTM models for top ASX stocks (Event Calendar focus)
REM Expected Time: 1.5-2 hours for 10 stocks
REM 
REM FIXED VERSION: Uses Python to check TensorFlow instead of batch
REM ====================================================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

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

REM Check if TensorFlow is installed using Python script (more reliable)
echo Checking for TensorFlow installation...

REM Create temporary Python check script
echo import sys > _check_tf.py
echo try: >> _check_tf.py
echo     import tensorflow >> _check_tf.py
echo     print("[OK] TensorFlow is installed") >> _check_tf.py
echo     sys.exit(0) >> _check_tf.py
echo except ImportError as e: >> _check_tf.py
echo     print("[WARNING] TensorFlow not detected") >> _check_tf.py
echo     print() >> _check_tf.py
echo     print("LSTM training requires TensorFlow. You have two options:") >> _check_tf.py
echo     print() >> _check_tf.py
echo     print("Option 1: Install TensorFlow now") >> _check_tf.py
echo     print("  Run: pip install tensorflow^>=2.13.0") >> _check_tf.py
echo     print("  Time: ~5 minutes") >> _check_tf.py
echo     print() >> _check_tf.py
echo     print("Option 2: Install from requirements.txt (includes all ML packages)") >> _check_tf.py
echo     print("  Run: pip install -r requirements.txt") >> _check_tf.py
echo     print("  Time: ~15 minutes (downloads ~2.5 GB)") >> _check_tf.py
echo     print() >> _check_tf.py
echo     print("After installing, run this script again.") >> _check_tf.py
echo     sys.exit(1) >> _check_tf.py

REM Run the check
python _check_tf.py
set TF_CHECK=%ERRORLEVEL%

REM Clean up
del _check_tf.py >nul 2>&1

REM Exit if TensorFlow not found
if %TF_CHECK% neq 0 (
    echo.
    pause
    exit /b 1
)

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
echo Press any key to close...
pause
