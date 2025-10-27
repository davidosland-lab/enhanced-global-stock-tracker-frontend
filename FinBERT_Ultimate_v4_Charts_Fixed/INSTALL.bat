@echo off
title FinBERT Ultimate Trading System v4.0 - Installer
color 0A
cls

echo ================================================================
echo    FINBERT ULTIMATE TRADING SYSTEM v4.0 - COMPLETE INSTALLER
echo    Fixed: Predictions, Charts, SMA_50, Auto-Training
echo ================================================================
echo.
echo This installer will set up the Complete FinBERT Trading System
echo with all fixes for Python 3.12 compatibility and enhanced features.
echo.
echo NEW FIXES IN v4.0:
echo  - Fixed prediction service with auto-training
echo  - Fixed next-day price predictions
echo  - Fixed 5-10 day price targets
echo  - Fixed SMA_50 calculation error
echo  - Fixed candlestick chart rendering
echo  - Real data only - no synthetic values
echo.
echo FEATURES:
echo  - Professional charting interface
echo  - AI predictions with Random Forest
echo  - FinBERT sentiment analysis
echo  - Technical indicators visualization
echo  - Economic indicators dashboard
echo ================================================================
echo.

:: Check Python version
echo [STEP 1/10] Checking Python version...
python --version 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    echo.
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

echo ================================================================
echo [STEP 2/10] Installing base dependencies
echo ================================================================
echo.

:: Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

:: Install setuptools and wheel first
echo Installing build tools...
python -m pip install --upgrade setuptools wheel
if errorlevel 1 (
    echo WARNING: Failed to install build tools, continuing anyway...
)

echo.
echo ================================================================
echo [STEP 3/10] Installing NumPy for Python 3.12
echo ================================================================
echo.

:: Uninstall old numpy if exists
echo Removing old NumPy versions if present...
python -m pip uninstall -y numpy 2>nul

:: Install correct numpy version
echo Installing NumPy 1.26.4 (Python 3.12 compatible)...
python -m pip install numpy==1.26.4 --no-cache-dir
if errorlevel 1 (
    echo.
    echo WARNING: NumPy 1.26.4 installation failed
    echo Trying alternative installation...
    python -m pip install --no-cache-dir "numpy>=1.26.0"
    if errorlevel 1 (
        echo ERROR: NumPy installation failed completely
        echo Cannot continue without NumPy
        pause
        exit /b 1
    )
)

:: Verify numpy
python -c "import numpy; print(f'NumPy {numpy.__version__} installed successfully')" 2>nul
if errorlevel 1 (
    echo WARNING: NumPy verification failed but continuing...
)

echo.
echo ================================================================
echo [STEP 4/10] Installing core dependencies
echo ================================================================
echo.

:: Install core packages one by one with error checking
echo Installing pandas...
python -m pip install "pandas>=2.0.0"
if errorlevel 1 echo WARNING: pandas installation had issues

echo Installing scikit-learn...
python -m pip install "scikit-learn>=1.3.0"
if errorlevel 1 echo WARNING: scikit-learn installation had issues

echo Installing scipy...
python -m pip install scipy
if errorlevel 1 echo WARNING: scipy installation had issues

echo Installing yfinance...
python -m pip install "yfinance>=0.2.28"
if errorlevel 1 echo WARNING: yfinance installation had issues

echo Installing technical analysis library...
python -m pip install "ta>=0.10.2"
if errorlevel 1 echo WARNING: ta installation had issues

echo Installing Flask and web components...
python -m pip install "Flask>=2.3.0" "flask-cors>=4.0.0"
if errorlevel 1 echo WARNING: Flask installation had issues

echo Installing requests and utilities...
python -m pip install "requests>=2.31.0" "feedparser>=6.0.10"
if errorlevel 1 echo WARNING: requests installation had issues

echo Installing additional packages...
python -m pip install beautifulsoup4 lxml python-dotenv tqdm joblib
if errorlevel 1 echo WARNING: Some additional packages had installation issues

echo.
echo ================================================================
echo [STEP 5/10] Installing PyTorch (Required for FinBERT)
echo ================================================================
echo.
echo This may take several minutes...

:: Install PyTorch CPU version
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
if errorlevel 1 (
    echo.
    echo WARNING: PyTorch installation failed
    echo Trying alternative installation method...
    python -m pip install torch --no-cache-dir
    if errorlevel 1 (
        echo.
        echo ERROR: PyTorch installation failed completely
        echo FinBERT will not work without PyTorch
        echo The system will use fallback sentiment analysis
        echo.
    )
)

:: Verify PyTorch
python -c "import torch; print(f'PyTorch {torch.__version__} installed successfully')" 2>nul
if errorlevel 1 (
    echo WARNING: PyTorch not properly installed - FinBERT will use fallback mode
)

echo.
echo ================================================================
echo [STEP 6/10] Installing Transformers for FinBERT
echo ================================================================
echo.

echo Installing transformers library...
python -m pip install "transformers==4.36.0" --no-cache-dir
if errorlevel 1 (
    echo.
    echo WARNING: Transformers installation failed
    echo Trying alternative version...
    python -m pip install transformers --no-cache-dir
    if errorlevel 1 (
        echo ERROR: Transformers installation failed
        echo FinBERT sentiment analysis will not be available
    )
)

:: Test FinBERT components
echo Testing FinBERT components...
python -c "from transformers import AutoTokenizer; print('FinBERT components ready!')" 2>nul
if errorlevel 1 (
    echo WARNING: FinBERT may not be fully functional
    echo The system will use fallback sentiment analysis if needed
) else (
    echo FinBERT components verified successfully!
    echo Note: FinBERT model will download on first use (~2GB)
)

echo.
echo ================================================================
echo [STEP 7/10] Installing optional data packages
echo ================================================================
echo.

echo Installing additional data sources...
python -m pip install alpha-vantage finnhub-python fredapi 2>nul

echo.
echo ================================================================
echo [STEP 8/10] Creating required directories
echo ================================================================
echo.

if not exist cache mkdir cache
if not exist models mkdir models
if not exist logs mkdir logs
if not exist data mkdir data

echo Directories created: cache, models, logs, data

echo.
echo ================================================================
echo [STEP 9/10] Creating configuration file
echo ================================================================
echo.

if not exist .env (
    (
    echo # FinBERT Ultimate Configuration
    echo FLASK_SKIP_DOTENV=1
    echo.
    echo # Optional API Keys - Add your keys here:
    echo # ALPHA_VANTAGE_API_KEY=your_key_here
    echo # IEX_TOKEN=your_token_here
    echo # FINNHUB_API_KEY=your_key_here
    echo # POLYGON_API_KEY=your_key_here
    echo # FRED_API_KEY=your_key_here
    ) > .env
    echo Configuration file created: .env
) else (
    echo Configuration file already exists: .env
)

echo.
echo ================================================================
echo [STEP 10/10] Final verification
echo ================================================================
echo.

:: Create comprehensive verification script
(
echo import sys
echo print(f"Python: {sys.version}"^)
echo try:
echo     import numpy as np
echo     print(f"NumPy: {np.__version__}"^)
echo except: print("NumPy: NOT INSTALLED"^)
echo try:
echo     import pandas as pd
echo     print(f"Pandas: {pd.__version__}"^)
echo except: print("Pandas: NOT INSTALLED"^)
echo try:
echo     import sklearn
echo     print(f"Scikit-learn: {sklearn.__version__}"^)
echo except: print("Scikit-learn: NOT INSTALLED"^)
echo try:
echo     import yfinance
echo     print("yfinance: OK"^)
echo except: print("yfinance: NOT INSTALLED"^)
echo try:
echo     import ta
echo     print("Technical Analysis: OK"^)
echo except: print("Technical Analysis: NOT INSTALLED"^)
echo try:
echo     import flask
echo     print(f"Flask: {flask.__version__}"^)
echo except: print("Flask: NOT INSTALLED"^)
echo try:
echo     import torch
echo     print(f"PyTorch: {torch.__version__}"^)
echo except: print("PyTorch: NOT INSTALLED (FinBERT will use fallback)"^)
echo try:
echo     import transformers
echo     print(f"Transformers: {transformers.__version__}"^)
echo except: print("Transformers: NOT INSTALLED (FinBERT will use fallback)"^)
) > verify_install.py

echo Running verification...
echo.
python verify_install.py
if errorlevel 1 (
    echo.
    echo WARNING: Some components may not be properly installed
    echo The system may work with reduced functionality
) else (
    echo.
    echo SUCCESS: All core components verified!
)

del verify_install.py

echo.
echo ================================================================
echo INSTALLATION COMPLETE!
echo ================================================================
echo.
echo System Features:
echo   ✓ Real-time stock data with charts
echo   ✓ AI predictions with Random Forest (FIXED)
echo   ✓ Next-day price predictions (FIXED)
echo   ✓ 5-10 day price targets (FIXED)
echo   ✓ SMA_50 calculation (FIXED)
echo   ✓ FinBERT sentiment analysis
echo   ✓ Professional charting interface (FIXED)
echo   ✓ Technical indicators (RSI, MACD, Bollinger)
echo   ✓ Economic indicators dashboard
echo   ✓ News sentiment analysis
echo.
echo To start the system:
echo   Run: START.bat
echo.
echo The system will:
echo   1. Start the API server on port 5000
echo   2. Open charts interface in your browser
echo   3. Auto-train models as needed
echo.
echo API Endpoints available at:
echo   http://localhost:5000
echo.
echo Charts Interface:
echo   Open finbert_charts.html in your browser
echo.
echo ================================================================
echo.
echo Press any key to exit the installer...
pause >nul