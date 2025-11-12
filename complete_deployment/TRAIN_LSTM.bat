@echo off
REM ===============================================================================
REM   FinBERT v4.4.4 Alpha Vantage - LSTM Training Launcher
REM   Trains LSTM models for stock prediction using Alpha Vantage API
REM ===============================================================================

echo ================================================================================
echo   FinBERT v4.4.4 - LSTM MODEL TRAINING (ALPHA VANTAGE)
echo ================================================================================
echo.
echo This script will train LSTM neural network models for stock prediction.
echo.
echo Training Details:
echo   - Model Type: Long Short-Term Memory (LSTM) Neural Network
echo   - Data Source: Alpha Vantage API (free tier: 500 req/day)
echo   - Training Data: Historical stock prices (up to 20 years)
echo   - Training Time: 10-30 minutes per stock
echo   - Rate Limiting: 12 seconds between stocks (API limit: 5 calls/min)
echo   - Models Saved: finbert_v4.4.4\lstm_models\
echo.
echo WARNING: This is a resource-intensive process!
echo   - High CPU usage expected
echo   - High memory usage (4+ GB RAM recommended)
echo   - Internet connection required for Alpha Vantage API
echo   - API calls count toward daily limit (500/day)
echo.

pause

REM Set the working directory to script location
cd /d "%~dp0"

echo.
echo ================================================================================
echo   System Information
echo ================================================================================
echo.
echo Current Directory: %CD%
echo.
echo Python Version:
python --version 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo   Γ£ù ERROR: Python is not installed!
    echo ================================================================================
    echo.
    echo Python 3.8+ is required to run this script.
    echo.
    echo Installation Steps:
    echo   1. Download Python from: https://www.python.org/downloads/
    echo   2. Install Python (check "Add Python to PATH")
    echo   3. Run INSTALL_DEPENDENCIES.bat
    echo   4. Try again
    echo.
    pause
    exit /b 1
)
echo.

echo ================================================================================
echo   Pre-Flight Check
echo ================================================================================
echo.

REM Check if training script exists
if not exist "finbert_v4.4.4\models\train_lstm.py" (
    echo Γ£ù ERROR: train_lstm.py not found!
    echo Expected location: finbert_v4.4.4\models\train_lstm.py
    echo.
    echo Package may be incomplete. Please re-extract the ZIP file.
    pause
    exit /b 1
)
echo Γ£ô Training script found
echo.

REM Check if Alpha Vantage fetcher exists
if not exist "models\screening\alpha_vantage_fetcher.py" (
    echo Γ£ù ERROR: alpha_vantage_fetcher.py not found!
    echo Expected location: models\screening\alpha_vantage_fetcher.py
    echo.
    echo This file is required for Alpha Vantage API integration.
    echo Please re-extract the complete deployment package.
    pause
    exit /b 1
)
echo Γ£ô Alpha Vantage fetcher found
echo.

REM Check if TensorFlow is installed
python -c "import tensorflow" >nul 2>&1
if %errorlevel% neq 0 (
    echo Γ£ù ERROR: TensorFlow is not installed!
    echo.
    echo TensorFlow is required for LSTM model training.
    echo.
    echo To install:
    echo   1. Run INSTALL_DEPENDENCIES.bat (recommended)
    echo   2. Or manually run: pip install tensorflow
    echo.
    pause
    exit /b 1
)
echo Γ£ô TensorFlow installed
echo.

REM Check if pandas is installed
python -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo Γ£ù ERROR: pandas is not installed!
    echo.
    echo Please run INSTALL_DEPENDENCIES.bat first.
    pause
    exit /b 1
)
echo Γ£ô pandas installed
echo.

REM Check if numpy is installed
python -c "import numpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo Γ£ù ERROR: numpy is not installed!
    echo.
    echo Please run INSTALL_DEPENDENCIES.bat first.
    pause
    exit /b 1
)
echo Γ£ô numpy installed
echo.

REM Create lstm_models directory if not exists
if not exist "finbert_v4.4.4\lstm_models" mkdir finbert_v4.4.4\lstm_models
echo Γ£ô LSTM models directory ready
echo.

REM Create logs directory if not exists
if not exist "logs" mkdir logs
echo Γ£ô Logs directory ready
echo.

REM Create cache directory if not exists
if not exist "cache" mkdir cache
echo Γ£ô Cache directory ready
echo.

echo ================================================================================
echo   Training Options
echo ================================================================================
echo.
echo Select training mode:
echo.
echo   [1] Quick Training (3 stocks, ~30-45 minutes)
echo       - Best for testing the system
echo       - Trains: CBA.AX, BHP.AX, CSL.AX
echo       - Uses: 15-20 API calls (3%% of daily limit)
echo.
echo   [2] Full Training (40 stocks, ~8-12 hours)
echo       - Complete model set for screening
echo       - All stocks from asx_sectors_fast.json
echo       - Uses: 200-250 API calls (40-50%% of daily limit)
echo.
echo   [3] Custom Training (specify your own stocks)
echo       - Enter your own ticker list
echo       - Example: CBA.AX WBC.AX ANZ.AX
echo.
echo   [4] Test Mode (1 stock, 5 epochs, ~5 minutes)
echo       - Ultra-fast test for troubleshooting
echo       - Trains: CBA.AX with minimal epochs
echo.

set /p choice="Enter choice (1/2/3/4): "

if "%choice%"=="1" (
    echo.
    echo ================================================================================
    echo   Starting Quick Training (3 stocks)
    echo ================================================================================
    echo.
    echo This will train 3 LSTM models with 50 epochs each.
    echo Estimated time: 30-45 minutes
    echo API calls: ~15-20 (3%% of daily limit)
    echo.
    python finbert_v4.4.4\models\train_lstm.py --tickers CBA.AX BHP.AX CSL.AX --epochs 50
    
) else if "%choice%"=="2" (
    echo.
    echo ================================================================================
    echo   Starting Full Training (40 stocks)
    echo ================================================================================
    echo.
    echo WARNING: This will take 8-12 hours to complete!
    echo.
    echo You can safely:
    echo   - Minimize this window
    echo   - Put computer to sleep (may pause training)
    echo   - Check progress by looking at finbert_v4.4.4\lstm_models\
    echo.
    echo API usage: 200-250 calls (40-50%% of daily limit)
    echo.
    echo Press Ctrl+C to cancel or any key to continue...
    pause
    echo.
    
    REM Load all tickers from asx_sectors_fast.json and train
    python -c "import json; data = json.load(open('models/config/asx_sectors_fast.json')); tickers = [t for s in data['sectors'].values() for t in s['stocks']]; print(' '.join(tickers))" > temp_tickers.txt
    set /p all_tickers=<temp_tickers.txt
    del temp_tickers.txt
    
    python finbert_v4.4.4\models\train_lstm.py --tickers %all_tickers% --epochs 50
    
) else if "%choice%"=="3" (
    echo.
    echo ================================================================================
    echo   Custom Training Mode
    echo ================================================================================
    echo.
    echo Enter stock tickers separated by spaces.
    echo.
    echo Examples:
    echo   - ASX stocks: CBA.AX WBC.AX ANZ.AX BHP.AX
    echo   - US stocks: AAPL MSFT GOOGL TSLA
    echo   - Mixed: CBA.AX AAPL BHP.AX MSFT
    echo.
    set /p custom_tickers="Enter tickers: "
    
    if "%custom_tickers%"=="" (
        echo ERROR: No tickers entered. Exiting.
        pause
        exit /b 1
    )
    
    echo.
    echo Starting Custom Training...
    echo Tickers: %custom_tickers%
    echo.
    python finbert_v4.4.4\models\train_lstm.py --tickers %custom_tickers% --epochs 50
    
) else if "%choice%"=="4" (
    echo.
    echo ================================================================================
    echo   Starting Test Mode (1 stock, 5 epochs)
    echo ================================================================================
    echo.
    echo This will quickly train 1 model for testing purposes.
    echo Estimated time: 5-10 minutes
    echo API calls: ~5 (1%% of daily limit)
    echo.
    python finbert_v4.4.4\models\train_lstm.py --test
    
) else (
    echo.
    echo ================================================================================
    echo   ERROR: Invalid choice
    echo ================================================================================
    echo.
    echo Please enter 1, 2, 3, or 4.
    pause
    exit /b 1
)

REM Check if training succeeded
if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo   Γ£ù TRAINING FAILED
    echo ================================================================================
    echo.
    echo The LSTM training encountered an error.
    echo Check the error messages above for details.
    echo.
    echo Common Issues:
    echo   1. Missing dependencies
    echo      Solution: Run INSTALL_DEPENDENCIES.bat
    echo.
    echo   2. Alpha Vantage API errors
    echo      Solution: Check internet connection, try again later
    echo.
    echo   3. Insufficient historical data for stock
    echo      Solution: Try a different stock with longer history
    echo.
    echo   4. Out of memory
    echo      Solution: Close other applications, restart computer
    echo.
    echo   5. API daily limit reached (500 requests/day)
    echo      Solution: Wait until tomorrow (resets at midnight UTC)
    echo.
    echo Detailed logs saved to: logs\lstm_training_*.log
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   Γ£à TRAINING COMPLETE!
echo ================================================================================
echo.
echo LSTM models have been trained and saved to:
echo   finbert_v4.4.4\lstm_models\
echo.
echo You can now run RUN_STOCK_SCREENER.bat to use these models for predictions.
echo.
echo Trained Model Files:
dir /b finbert_v4.4.4\lstm_models\*_lstm_model.h5 2>nul
dir /b finbert_v4.4.4\lstm_models\*.keras 2>nul
echo.
echo Training Metadata:
dir /b finbert_v4.4.4\lstm_models\*_metadata.json 2>nul
echo.
echo Training Results:
if exist "finbert_v4.4.4\lstm_models\training_results.json" (
    type finbert_v4.4.4\lstm_models\training_results.json
)
echo.

pause
