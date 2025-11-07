@echo off
REM ============================================================================
REM FinBERT v4.4 - Start Server
REM ============================================================================

echo.
echo ================================================================================
echo   Starting FinBERT v4.4 Server
echo ================================================================================
echo   Phase 1 Improvements Active:
echo   - Sentiment Integration (15%% weight in ensemble)
echo   - Volume Analysis (confidence adjustment)
echo   - Technical Indicators (8+ with consensus voting)
echo   - LSTM Neural Networks (if trained)
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

REM Check if TensorFlow is available
python -c "import tensorflow" 2>nul
if errorlevel 1 (
    echo [WARNING] TensorFlow not installed - LSTM predictions disabled
    echo For full AI/ML features, run INSTALL.bat and choose option 1
    echo.
)

REM Check for trained models
if exist "models\lstm_AAPL.keras" (
    echo [INFO] Found trained LSTM models - Neural network predictions enabled
) else (
    echo [INFO] No trained models found - Run TRAIN_LSTM_OVERNIGHT.bat for best accuracy
)

echo.
echo Starting Flask server on http://localhost:5001
echo Press CTRL+C to stop
echo.

python app_finbert_v4_dev.py

if errorlevel 1 (
    echo.
    echo [ERROR] Server failed to start
    echo Check the error messages above
    pause
)
