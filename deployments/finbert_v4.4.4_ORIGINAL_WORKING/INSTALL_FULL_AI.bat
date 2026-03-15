@echo off
REM ============================================================================
REM  FinBERT v4.0 Enhanced - FULL AI/ML Installation
REM  Installs ALL components: TensorFlow, FinBERT, LSTM, Sentiment Analysis
REM ============================================================================

echo.
echo ============================================================================
echo   FinBERT v4.0 ENHANCED - FULL AI/ML Installation
echo ============================================================================
echo.
echo This script installs the COMPLETE system with:
echo   ✓ TensorFlow (LSTM Neural Networks)
echo   ✓ FinBERT (Financial Sentiment Analysis)
echo   ✓ All ML prediction models
echo   ✓ Complete UI with sentiment display
echo.
echo Total download: ~700MB
echo Installation time: 10-20 minutes
echo.
pause

REM Check Python installation
echo.
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo Python found successfully!

REM Create virtual environment
echo.
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists.
    set /p RECREATE="Delete and recreate? (y/n): "
    if /i "%RECREATE%"=="y" (
        echo Deleting existing virtual environment...
        rmdir /s /q venv
        python -m venv venv
        echo New virtual environment created!
    ) else (
        echo Using existing virtual environment.
    )
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip

REM Install ALL packages from requirements-full.txt
echo.
echo [5/5] Installing FULL AI/ML system...
echo.
echo ============================================================================
echo   Installing Complete Package (~700MB)
echo ============================================================================
echo.
echo This includes:
echo   - Flask, NumPy, Pandas, scikit-learn (core packages)
echo   - TensorFlow CPU (~200MB) for LSTM neural networks
echo   - PyTorch and Transformers (~500MB) for FinBERT sentiment
echo   - yfinance for real-time market data
echo.
echo Please be patient - this may take 10-20 minutes...
echo.

pip install -r requirements-full.txt

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo   WARNING: Some packages failed to install
    echo ============================================================================
    echo.
    echo This usually means:
    echo   1. Internet connection issue
    echo   2. Incompatible Python version (need 3.8-3.12)
    echo   3. Insufficient disk space
    echo.
    echo The system may still work with reduced functionality.
    echo.
    pause
) else (
    echo.
    echo ============================================================================
    echo   All packages installed successfully!
    echo ============================================================================
)

REM Verify installation
echo.
echo ============================================================================
echo   Verifying Installation
echo ============================================================================
echo.

python -c "import flask; print(f'✓ Flask {flask.__version__}')"
python -c "import numpy; print(f'✓ NumPy {numpy.__version__}')"
python -c "import pandas; print(f'✓ Pandas {pandas.__version__}')"
python -c "import sklearn; print(f'✓ scikit-learn {sklearn.__version__}')"
python -c "import yfinance; print(f'✓ yfinance {yfinance.__version__}')"

echo.
echo Verifying AI/ML components...
python -c "try: import tensorflow as tf; print(f'✓ TensorFlow {tf.__version__} - INSTALLED')\nexcept Exception as e: print(f'✗ TensorFlow - FAILED: {e}')"
python -c "try: import torch; print(f'✓ PyTorch {torch.__version__} - INSTALLED')\nexcept Exception as e: print(f'✗ PyTorch - FAILED: {e}')"
python -c "try: import transformers; print(f'✓ Transformers {transformers.__version__} - INSTALLED')\nexcept Exception as e: print(f'✗ Transformers - FAILED: {e}')"

echo.
echo ============================================================================
echo   Installation Complete!
echo ============================================================================
echo.
echo FULL AI/ML System Status:
echo   ✓ Core packages installed
echo   ✓ TensorFlow installed (LSTM neural networks)
echo   ✓ FinBERT installed (sentiment analysis)
echo   ✓ All prediction models available
echo.
echo Next steps:
echo   1. Run START_V4_ENHANCED.bat to start the server
echo   2. Open http://localhost:5001 in your browser
echo   3. Enjoy FULL AI/ML predictions with sentiment analysis!
echo.
echo Features now available:
echo   ✓ LSTM neural network predictions (50%% weight)
echo   ✓ Technical analysis (30%% weight)
echo   ✓ Trend analysis (20%% weight)
echo   ✓ Financial sentiment analysis
echo   ✓ Model training from UI
echo   ✓ Candlestick charts with all intervals
echo   ✓ Current price display
echo   ✓ Sentiment scores in UI
echo.
echo Documentation:
echo   - README_V4_COMPLETE.md (complete guide)
echo   - WINDOWS11_QUICK_START.txt (quick start)
echo.
pause
