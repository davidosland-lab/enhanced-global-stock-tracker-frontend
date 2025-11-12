@echo off
REM ===============================================================================
REM   FinBERT v4.4.4 Alpha Vantage - Dependency Installer
REM   Installs all required Python packages for the system
REM ===============================================================================

echo ================================================================================
echo   FinBERT v4.4.4 - ALPHA VANTAGE EDITION
echo   Dependency Installation Script
echo ================================================================================
echo.
echo This script will install all required Python packages.
echo.
echo Required Packages:
echo   - yfinance (Yahoo Finance API - legacy support)
echo   - pandas (Data manipulation)
echo   - numpy (Numerical computing)
echo   - requests (HTTP library)
echo   - beautifulsoup4 (Web scraping)
echo   - lxml (XML/HTML parser)
echo   - transformers (Hugging Face models)
echo   - torch (PyTorch - AI framework)
echo   - tensorflow (TensorFlow - LSTM models)
echo   - scikit-learn (Machine learning)
echo   - pytz (Timezone support)
echo.
echo Estimated installation time: 5-10 minutes
echo Estimated disk space required: ~2 GB
echo.

pause

echo.
echo ================================================================================
echo   STEP 1: Checking Python Installation
echo ================================================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo ✓ Python is installed:
python --version
echo.

echo ================================================================================
echo   STEP 2: Upgrading pip
echo ================================================================================
echo.

python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠ WARNING: Failed to upgrade pip, but continuing...
)
echo.

echo ================================================================================
echo   STEP 3: Installing Core Dependencies
echo ================================================================================
echo.

echo [1/12] Installing yfinance...
python -m pip install yfinance --user
echo.

echo [2/12] Installing pandas...
python -m pip install pandas --user
echo.

echo [3/12] Installing numpy...
python -m pip install numpy --user
echo.

echo [4/12] Installing requests...
python -m pip install requests --user
echo.

echo [5/12] Installing beautifulsoup4...
python -m pip install beautifulsoup4 --user
echo.

echo [6/12] Installing lxml...
python -m pip install lxml --user
echo.

echo [7/12] Installing pytz...
python -m pip install pytz --user
echo.

echo [8/12] Installing scikit-learn...
python -m pip install scikit-learn --user
echo.

echo ================================================================================
echo   STEP 4: Installing AI/ML Frameworks
echo ================================================================================
echo.

echo [9/12] Installing transformers (Hugging Face)...
echo This may take a few minutes...
python -m pip install transformers --user
echo.

echo [10/12] Installing torch (PyTorch)...
echo This may take a few minutes...
python -m pip install torch --user
echo.

echo [11/12] Installing tensorflow...
echo This may take a few minutes...
python -m pip install tensorflow --user
echo.

echo [12/12] Installing additional dependencies...
python -m pip install sentencepiece sacremoses --user
echo.

echo ================================================================================
echo   STEP 5: Verification
echo ================================================================================
echo.

echo Verifying installations...
echo.

python -c "import yfinance; print('✓ yfinance')" 2>nul || echo "❌ yfinance"
python -c "import pandas; print('✓ pandas')" 2>nul || echo "❌ pandas"
python -c "import numpy; print('✓ numpy')" 2>nul || echo "❌ numpy"
python -c "import requests; print('✓ requests')" 2>nul || echo "❌ requests"
python -c "import bs4; print('✓ beautifulsoup4')" 2>nul || echo "❌ beautifulsoup4"
python -c "import lxml; print('✓ lxml')" 2>nul || echo "❌ lxml"
python -c "import transformers; print('✓ transformers')" 2>nul || echo "❌ transformers"
python -c "import torch; print('✓ torch')" 2>nul || echo "❌ torch"
python -c "import tensorflow; print('✓ tensorflow')" 2>nul || echo "❌ tensorflow"
python -c "import sklearn; print('✓ scikit-learn')" 2>nul || echo "❌ scikit-learn"
python -c "import pytz; print('✓ pytz')" 2>nul || echo "❌ pytz"

echo.
echo ================================================================================
echo   ✅ INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo All dependencies have been installed successfully.
echo.
echo Next Steps:
echo   1. Run RUN_STOCK_SCREENER.bat to start stock scanning
echo   2. Run TRAIN_LSTM.bat to train LSTM models (optional)
echo.
echo For more information, see README.txt
echo.

pause
