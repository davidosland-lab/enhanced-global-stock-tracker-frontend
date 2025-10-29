@echo off
title FinBERT Ultimate Trading System with Charts - Installer
color 0A
cls

echo ================================================================
echo    FINBERT ULTIMATE TRADING SYSTEM v3.0 - COMPLETE INSTALLER
echo    Including Charts, Next-Day Predictions, and All Fixes
echo ================================================================
echo.
echo This installer will set up the Complete FinBERT Trading System
echo with professional charts and all Python 3.12 compatibility fixes.
echo.
echo NEW FEATURES:
echo  - Professional charting interface
echo  - Next-day price predictions
echo  - 5-10 day price targets
echo  - Candlestick/OHLC/Line charts
echo  - Technical indicators visualization
echo  - Economic dashboard
echo.
echo FIXED ISSUES:
echo  - Python 3.12 numpy compatibility
echo  - SMA_50 error during predictions
echo  - Transformers installation order
echo  - Real data only (no synthetic fallbacks)
echo ================================================================
echo.

:: Check Python version
echo Checking Python version...
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

echo ================================================================
echo STEP 1: Installing base dependencies
echo ================================================================
echo.

:: Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install setuptools and wheel first
echo Installing build tools...
python -m pip install --upgrade setuptools wheel

echo.
echo ================================================================
echo STEP 2: Installing NumPy for Python 3.12
echo ================================================================
echo.

:: Uninstall old numpy if exists
echo Removing old NumPy versions...
python -m pip uninstall -y numpy 2>nul

:: Install correct numpy version
echo Installing NumPy 1.26.4 (Python 3.12 compatible)...
python -m pip install numpy==1.26.4

:: Verify numpy
python -c "import numpy; print(f'NumPy {numpy.__version__} installed successfully')" 2>nul
if errorlevel 1 (
    echo ERROR: NumPy installation failed
    echo Trying alternative installation...
    python -m pip install --no-cache-dir "numpy>=1.26.0"
)

echo.
echo ================================================================
echo STEP 3: Installing core dependencies
echo ================================================================
echo.

:: Install core packages
echo Installing pandas...
python -m pip install pandas>=2.0.0

echo Installing scikit-learn...
python -m pip install scikit-learn>=1.3.0

echo Installing scipy...
python -m pip install scipy

echo Installing yfinance...
python -m pip install yfinance>=0.2.28

echo Installing technical indicators...
python -m pip install ta>=0.10.2

echo Installing Flask and web components...
python -m pip install Flask>=2.3.0 flask-cors>=4.0.0

echo Installing requests and utilities...
python -m pip install requests>=2.31.0 feedparser>=6.0.10

echo Installing additional packages...
python -m pip install beautifulsoup4 lxml python-dotenv tqdm joblib

echo.
echo ================================================================
echo STEP 4: Installing PyTorch FIRST (Required for FinBERT)
echo ================================================================
echo.

echo Installing PyTorch CPU version (this may take a few minutes)...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

:: Verify PyTorch
python -c "import torch; print(f'PyTorch {torch.__version__} installed successfully')" 2>nul
if errorlevel 1 (
    echo WARNING: PyTorch may not be properly installed
    echo Trying alternative installation...
    python -m pip install torch --no-cache-dir
)

echo.
echo ================================================================
echo STEP 5: Installing Transformers (AFTER PyTorch)
echo ================================================================
echo.

echo Installing transformers library for FinBERT...
python -m pip install transformers==4.36.0 --no-cache-dir

:: Test FinBERT components
echo Testing FinBERT components...
python -c "from transformers import AutoTokenizer; print('FinBERT components installed successfully!')" 2>nul
if errorlevel 1 (
    echo WARNING: FinBERT installation may be incomplete
    echo The system may have issues with sentiment analysis
) else (
    echo FinBERT ready! Model will download on first use (~2GB)
)

echo.
echo ================================================================
echo STEP 6: Installing optional data source packages
echo ================================================================
echo.

echo Installing Alpha Vantage support...
python -m pip install alpha-vantage 2>nul

echo Installing Finnhub support...
python -m pip install finnhub-python 2>nul

echo Installing FRED API support...
python -m pip install fredapi 2>nul

echo.
echo ================================================================
echo STEP 7: Creating required directories
echo ================================================================
echo.

if not exist cache mkdir cache
if not exist models mkdir models
if not exist logs mkdir logs
if not exist data mkdir data

echo Directories created: cache, models, logs, data

echo.
echo ================================================================
echo STEP 8: Creating configuration file
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
echo STEP 9: Verifying installation
echo ================================================================
echo.

:: Create verification script
(
echo import sys
echo print(f"Python: {sys.version}"^)
echo import numpy as np
echo print(f"NumPy: {np.__version__}"^)
echo import pandas as pd
echo print(f"Pandas: {pd.__version__}"^)
echo import sklearn
echo print(f"Scikit-learn: {sklearn.__version__}"^)
echo import yfinance as yf
echo print(f"yfinance: OK"^)
echo import ta
echo print("Technical Analysis: OK"^)
echo import flask
echo print(f"Flask: {flask.__version__}"^)
echo import torch
echo print(f"PyTorch: {torch.__version__}"^)
echo import transformers
echo print(f"Transformers: {transformers.__version__}"^)
echo print("\n✓ All components verified!"^)
) > verify_install.py

python verify_install.py
if errorlevel 1 (
    echo.
    echo WARNING: Some components may not be properly installed
    echo Try running this installer again
) else (
    echo.
    echo SUCCESS: All components installed correctly!
)

del verify_install.py

echo.
echo ================================================================
echo INSTALLATION COMPLETE!
echo ================================================================
echo.
echo System Features:
echo   ✓ Real-time stock data with charts
echo   ✓ AI predictions with Random Forest
echo   ✓ Next-day price predictions
echo   ✓ 5-10 day price targets
echo   ✓ FinBERT sentiment analysis
echo   ✓ Professional charting interface
echo   ✓ Technical indicators (RSI, MACD, Bollinger)
echo   ✓ Economic indicators dashboard
echo   ✓ News sentiment analysis
echo.
echo To start the system:
echo   Run: START.bat
echo.
echo The system will:
echo   1. Start the backend server
echo   2. Open charts in your browser
echo   3. Be ready for trading analysis
echo.
echo API Endpoints available at:
echo   http://localhost:5000
echo.
echo ================================================================
echo.
pause