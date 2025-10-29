@echo off
title FinBERT Ultimate Trading System - Installer
color 0A
cls

echo ================================================================
echo    FINBERT ULTIMATE TRADING SYSTEM - COMPLETE INSTALLER
echo ================================================================
echo.
echo This installer will set up the Ultimate FinBERT Trading System
echo with all fixes for Python 3.12 compatibility and data issues.
echo.
echo FIXED ISSUES:
echo  - Python 3.12 numpy compatibility
echo  - SMA_50 error during predictions
echo  - Insufficient data errors
echo  - Real data only (no synthetic fallbacks)
echo  - Multiple data sources with fallback
echo  - Economic indicators integration
echo ================================================================
echo.

:: Check Python version
echo Checking Python version...
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12 from python.org
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

:: Check if Python 3.12
echo %PYTHON_VERSION% | findstr /C:"3.12" >nul
if errorlevel 1 (
    echo WARNING: Python 3.12 is recommended for best compatibility
    echo Current version: %PYTHON_VERSION%
    echo.
    choice /C YN /M "Continue anyway"
    if errorlevel 2 exit /b 0
)

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
    python -m pip install --no-cache-dir numpy>=1.26.0
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

echo Installing yfinance...
python -m pip install yfinance>=0.2.28

echo Installing technical indicators...
python -m pip install ta>=0.10.2

echo Installing Flask and web components...
python -m pip install Flask>=2.3.0 flask-cors>=4.0.0

echo Installing requests and feedparser...
python -m pip install requests>=2.31.0 feedparser>=6.0.10

echo.
echo ================================================================
echo STEP 4: Installing FinBERT components (optional)
echo ================================================================
echo.

echo FinBERT requires PyTorch and transformers (large download ~2GB)
choice /C YN /M "Install FinBERT components"
if not errorlevel 2 (
    echo Installing PyTorch...
    python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    
    echo Installing transformers...
    python -m pip install transformers>=4.30.0
    
    echo Testing FinBERT...
    python -c "from transformers import AutoTokenizer; print('FinBERT components installed')" 2>nul
    if errorlevel 1 (
        echo WARNING: FinBERT installation incomplete
        echo System will use fallback sentiment analysis
    ) else (
        echo FinBERT installed successfully!
    )
) else (
    echo Skipping FinBERT - using fallback sentiment analysis
)

echo.
echo ================================================================
echo STEP 5: Installing optional data source packages
echo ================================================================
echo.

echo Installing Alpha Vantage support...
python -m pip install alpha-vantage 2>nul

echo Installing Finnhub support...
python -m pip install finnhub-python 2>nul

echo Installing Polygon.io support...
python -m pip install polygon-api-client 2>nul

echo.
echo ================================================================
echo STEP 6: Creating required directories
echo ================================================================
echo.

if not exist cache mkdir cache
if not exist models mkdir models
if not exist logs mkdir logs
if not exist data mkdir data

echo Directories created.

echo.
echo ================================================================
echo STEP 7: Verifying installation
echo ================================================================
echo.

:: Create a test script
echo Creating verification script...
(
echo import sys
echo print(f"Python: {sys.version}"^)
echo import numpy as np
echo print(f"NumPy: {np.__version__}"^)
echo assert tuple(map(int, np.__version__.split('.'^)[:2]^)^) ^>= (1, 26^), "NumPy version too old"
echo import pandas as pd
echo print(f"Pandas: {pd.__version__}"^)
echo import sklearn
echo print(f"Scikit-learn: {sklearn.__version__}"^)
echo import yfinance as yf
echo print(f"yfinance: {yf.__version__}"^)
echo import ta
echo print("Technical Analysis: OK"^)
echo import flask
echo print(f"Flask: {flask.__version__}"^)
echo try:
echo     import torch
echo     import transformers
echo     print("FinBERT: Available"^)
echo except:
echo     print("FinBERT: Not installed (will use fallback^)"^)
echo print("\nAll critical components verified!"^)
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
echo STEP 8: Creating run script
echo ================================================================
echo.

:: Create run script
(
echo @echo off
echo title FinBERT Ultimate Trading System
echo color 0A
echo cls
echo echo ================================================================
echo echo    FINBERT ULTIMATE TRADING SYSTEM
echo echo ================================================================
echo echo.
echo echo Starting server...
echo echo Navigate to: http://localhost:5000
echo echo Press Ctrl+C to stop the server
echo echo.
echo echo ================================================================
echo echo.
echo python app_finbert_ultimate.py
echo pause
) > RUN_ULTIMATE.bat

echo Run script created: RUN_ULTIMATE.bat

echo.
echo ================================================================
echo INSTALLATION COMPLETE!
echo ================================================================
echo.
echo To start the system:
echo   1. Run: RUN_ULTIMATE.bat
echo   2. Open browser to: http://localhost:5000
echo.
echo Optional: Set API keys as environment variables:
echo   - ALPHA_VANTAGE_API_KEY
echo   - IEX_TOKEN
echo   - FINNHUB_API_KEY
echo   - POLYGON_API_KEY
echo   - FRED_API_KEY
echo.
echo Without API keys, the system will use Yahoo Finance (primary)
echo.
echo ================================================================
echo.
pause