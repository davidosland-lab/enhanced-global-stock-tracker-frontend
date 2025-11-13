@echo off
REM ============================================================================
REM FinBERT v4.4 - Windows 11 Installation Script
REM Phase 1 Accuracy Improvements: Sentiment, Volume, Technical Indicators, LSTM
REM ============================================================================

echo.
echo ================================================================================
echo   FinBERT v4.4 - Windows 11 Installation
echo ================================================================================
echo   Phase 1 Accuracy Improvements (85-95%% accuracy target):
echo   - Sentiment Integration (v4.1) - Independent weighted model
echo   - Volume Analysis (v4.2) - Confidence adjustment
echo   - Technical Indicators (v4.3) - 8+ indicators with consensus
echo   - LSTM Batch Training (v4.4) - Overnight training ready
echo ================================================================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/5] Python found
python --version

REM Check for pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found!
    echo Installing pip...
    python -m ensurepip --default-pip
)

echo [2/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [4/5] Upgrading pip...
python -m pip install --upgrade pip

echo [5/5] Installing dependencies...
echo.
echo Choose installation type:
echo   1) FULL - All AI/ML features (RECOMMENDED)
echo      - TensorFlow for LSTM neural networks
echo      - Transformers for FinBERT sentiment
echo      - Technical Analysis library (ta)
echo      - ~2GB download, ~5 minutes install
echo.
echo   2) MINIMAL - Basic functionality only
echo      - No deep learning (LSTM disabled)
echo      - Fallback sentiment analysis
echo      - Basic technical indicators
echo      - ~100MB download, ~1 minute install
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Installing FULL AI/ML dependencies...
    echo This may take 5-10 minutes...
    python -m pip install -r requirements-full.txt
    if errorlevel 1 (
        echo [ERROR] Installation failed
        pause
        exit /b 1
    )
    echo.
    echo ================================================================================
    echo   FULL INSTALLATION COMPLETE!
    echo ================================================================================
    echo   Available Features:
    echo   - LSTM Neural Networks for prediction
    echo   - FinBERT sentiment analysis with real news
    echo   - 8+ Technical Indicators (SMA, EMA, RSI, MACD, BB, Stochastic, ADX, ATR)
    echo   - Volume analysis and trend detection
    echo   - Batch LSTM training for top stocks
    echo.
    echo   Next Steps:
    echo   1. Train LSTM models: TRAIN_LSTM_OVERNIGHT.bat (1-2 hours)
    echo   2. Start server: START_FINBERT.bat
    echo   3. Open browser: http://localhost:5001
    echo ================================================================================
) else (
    echo.
    echo Installing MINIMAL dependencies...
    echo Creating minimal requirements...
    echo flask>nul 2>&1 > requirements-minimal.txt
    echo flask-cors>>requirements-minimal.txt
    echo yfinance>>requirements-minimal.txt
    echo numpy>>requirements-minimal.txt
    echo pandas>>requirements-minimal.txt
    python -m pip install -r requirements-minimal.txt
    if errorlevel 1 (
        echo [ERROR] Installation failed
        pause
        exit /b 1
    )
    echo.
    echo ================================================================================
    echo   MINIMAL INSTALLATION COMPLETE!
    echo ================================================================================
    echo   Available Features:
    echo   - Basic stock data retrieval
    echo   - Simple trend analysis
    echo   - Fallback sentiment (no deep learning)
    echo   - Basic technical indicators
    echo.
    echo   Note: For 85-95%% accuracy, use FULL installation
    echo.
    echo   Next Steps:
    echo   1. Start server: START_FINBERT.bat
    echo   2. Open browser: http://localhost:5001
    echo ================================================================================
)

echo.
echo Installation complete!
pause
