@echo off
REM ============================================================================
REM  FinBERT v4.0 Enhanced - Windows 11 Installation Script
REM  Installs all dependencies and sets up the enhanced UI system
REM ============================================================================

echo.
echo ============================================================================
echo   FinBERT v4.0 ENHANCED - Windows 11 Installation
echo ============================================================================
echo.
echo This script will:
echo   1. Check Python installation
echo   2. Create virtual environment
echo   3. Install required packages
echo   4. Verify installation
echo.
pause

REM Check Python installation
echo.
echo [1/4] Checking Python installation...
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
echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
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
echo [3/4] Installing required packages...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install core requirements from requirements file
echo.
echo Installing core packages from requirements-windows.txt...
echo This uses versions with pre-compiled wheels for Python 3.12
echo.
pip install -r requirements-windows.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install required packages
    echo.
    echo This usually means:
    echo   1. Internet connection issue
    echo   2. Incompatible Python version (need 3.8-3.12)
    echo.
    echo Please check your internet connection and Python version
    pause
    exit /b 1
)

echo.
echo All core packages installed successfully!

REM Install optional TensorFlow (for LSTM training)
echo.
echo ============================================================================
echo TensorFlow Installation (Optional - for LSTM training)
echo ============================================================================
echo.
echo TensorFlow is required for training LSTM models but is optional.
echo The system works without it using fallback prediction methods.
echo.
echo TensorFlow package size: ~600MB (or ~200MB for CPU-only version)
echo.
echo Options:
echo   1. Full TensorFlow (GPU + CPU support) - ~600MB
echo   2. TensorFlow CPU-only (no GPU) - ~200MB
echo   3. Skip TensorFlow
echo.
set /p TF_CHOICE="Choose option (1/2/3): "

if "%TF_CHOICE%"=="1" (
    echo.
    echo Installing TensorFlow with GPU support... (this may take several minutes)
    pip install tensorflow>=2.15.0
    if errorlevel 1 (
        echo.
        echo WARNING: TensorFlow installation failed
        echo The system will work without it but LSTM training will be limited
        echo.
    ) else (
        echo TensorFlow installed successfully!
    )
) else if "%TF_CHOICE%"=="2" (
    echo.
    echo Installing TensorFlow CPU-only... (this may take several minutes)
    pip install tensorflow-cpu>=2.15.0
    if errorlevel 1 (
        echo.
        echo WARNING: TensorFlow installation failed
        echo The system will work without it but LSTM training will be limited
        echo.
    ) else (
        echo TensorFlow CPU-only installed successfully!
    )
) else (
    echo.
    echo Skipping TensorFlow installation
    echo You can install it later with:
    echo   - Full: pip install tensorflow
    echo   - CPU: pip install tensorflow-cpu
)

REM Install optional FinBERT/Transformers (for sentiment analysis)
echo.
echo ============================================================================
echo FinBERT Sentiment Model Installation (Optional)
echo ============================================================================
echo.
echo FinBERT (transformers) is used for financial sentiment analysis.
echo This is optional - the system works without it.
echo.
echo Package size: ~500MB (includes PyTorch and transformers)
echo.
set /p INSTALL_FINBERT="Install FinBERT sentiment model? (y/n): "

if /i "%INSTALL_FINBERT%"=="y" (
    echo.
    echo Installing transformers and torch... (this may take several minutes)
    pip install torch>=2.0.0 transformers>=4.30.0
    if errorlevel 1 (
        echo.
        echo WARNING: FinBERT/transformers installation failed
        echo The system will work without it
        echo.
    ) else (
        echo FinBERT dependencies installed successfully!
    )
) else (
    echo.
    echo Skipping FinBERT installation
    echo You can install it later with: pip install torch transformers
)

REM Verify installation
echo.
echo [4/4] Verifying installation...
echo.
python -c "import flask; print(f'Flask {flask.__version__} - OK')"
python -c "import numpy; print(f'NumPy {numpy.__version__} - OK')"
python -c "import pandas; print(f'Pandas {pandas.__version__} - OK')"
python -c "import sklearn; print(f'scikit-learn {sklearn.__version__} - OK')"
python -c "import yfinance; print(f'yfinance {yfinance.__version__} - OK')"
python -c "try: import tensorflow as tf; print(f'TensorFlow {tf.__version__} - OK')\nexcept: print('TensorFlow - NOT INSTALLED (optional)')"
python -c "try: import transformers; print(f'Transformers {transformers.__version__} - OK')\nexcept: print('Transformers - NOT INSTALLED (optional)')"

echo.
echo ============================================================================
echo   Installation Complete!
echo ============================================================================
echo.
echo Next steps:
echo   1. Run START_V4_ENHANCED.bat to start the server
echo   2. Open http://localhost:5001 in your browser
echo   3. Click "Train Model" to train LSTM models (if TensorFlow installed)
echo.
echo Features available:
echo   - Candlestick charts (OHLC visualization)
echo   - Volume chart below main chart
echo   - Training interface in UI
echo   - Extended timeframes (1D to 2Y)
echo   - US and Australian (ASX) stocks
echo.
echo Documentation:
echo   - START_HERE_v4_ENHANCED.txt
echo   - QUICK_ACCESS_GUIDE.md
echo   - README_V4_COMPLETE.md
echo.
pause
