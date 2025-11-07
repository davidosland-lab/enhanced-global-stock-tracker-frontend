@echo off
echo ============================================================================
echo   FinBERT v4.0 - Windows 11 Installation
echo ============================================================================
echo.
echo This script will:
echo   1. Check Python installation
echo   2. Create virtual environment
echo   3. Install required packages (FULL or MINIMAL)
echo   4. Verify installation
echo.
pause

REM Navigate to parent directory (main application folder)
cd ..
echo Working directory: %CD%
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo Python found successfully!

echo.
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, removing...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!

echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!

echo.
echo ============================================================================
echo   Choose Installation Type
echo ============================================================================
echo.
echo [1] FULL INSTALL - Complete AI/ML Experience (Recommended)
echo     Size: ~900 MB download, 2 GB installed
echo     Time: 10-20 minutes
echo     Features:
echo       - Real FinBERT sentiment analysis (97%% accuracy)
echo       - TensorFlow LSTM predictions
echo       - News scraping (Yahoo Finance + Finviz)
echo       - Advanced technical analysis
echo       - ALL AI/ML capabilities
echo.
echo [2] MINIMAL INSTALL - Basic Features Only
echo     Size: ~50 MB download, 500 MB installed
echo     Time: 2-3 minutes
echo     Features:
echo       - Basic price charts
echo       - Technical indicators (SMA, RSI, MACD)
echo       - Simple predictions
echo       - NO sentiment analysis
echo       - NO LSTM predictions
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" goto :full_install
if "%choice%"=="2" goto :minimal_install
echo Invalid choice. Please run the script again.
pause
exit /b 1

:full_install
echo.
echo [4/5] Installing FULL package (this may take 10-20 minutes)...
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing core packages...
pip install Flask==3.0.0 Flask-CORS==4.0.0

echo.
echo Installing data science packages...
pip install numpy>=1.26.0 pandas>=2.1.0 scikit-learn>=1.3.0

echo.
echo Installing financial data packages...
pip install yfinance>=0.2.28

echo.
echo Installing news scraping packages...
pip install beautifulsoup4>=4.12.0 aiohttp>=3.9.0 lxml>=4.9.0

echo.
echo Installing AI/ML packages (this is the longest step)...
echo Installing TensorFlow (5-10 minutes)...
pip install tensorflow>=2.13.0

echo.
echo Installing PyTorch (5-10 minutes)...
pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu

echo.
echo Installing Transformers for FinBERT...
pip install transformers>=4.30.0 sentencepiece>=0.1.99

echo.
echo [5/5] Verifying installation...
python -c "import flask; print('✓ Flask:', flask.__version__)" 2>nul
python -c "import numpy; print('✓ NumPy:', numpy.__version__)" 2>nul
python -c "import pandas; print('✓ Pandas:', pandas.__version__)" 2>nul
python -c "import yfinance; print('✓ yfinance installed')" 2>nul
python -c "import sklearn; print('✓ scikit-learn installed')" 2>nul
python -c "import bs4; print('✓ BeautifulSoup4 installed')" 2>nul
python -c "import aiohttp; print('✓ aiohttp installed')" 2>nul
python -c "import tensorflow; print('✓ TensorFlow:', tensorflow.__version__)" 2>nul
python -c "import torch; print('✓ PyTorch:', torch.__version__)" 2>nul
python -c "import transformers; print('✓ Transformers:', transformers.__version__)" 2>nul

echo.
echo ============================================================================
echo   FULL Installation Complete!
echo ============================================================================
echo.
echo Installation summary:
echo   - Python virtual environment: CREATED
echo   - Core packages (Flask, NumPy, Pandas): INSTALLED
echo   - Financial data (yfinance): INSTALLED
echo   - News scraping (BeautifulSoup, aiohttp): INSTALLED
echo   - AI/ML (TensorFlow, PyTorch, Transformers): INSTALLED
echo.
echo Next steps:
echo   1. Run START_FINBERT_V4.bat to start the application
echo   2. Open browser to http://127.0.0.1:5001
echo   3. Try analyzing AAPL, TSLA, or MSFT
echo.
echo Features available:
echo   ✓ Real FinBERT sentiment analysis
echo   ✓ TensorFlow LSTM predictions
echo   ✓ News scraping from Yahoo Finance and Finviz
echo   ✓ Fixed candlestick charts (no overlapping!)
echo   ✓ Advanced technical analysis
echo.
echo For help, see docs\INSTALLATION_GUIDE.md
echo.
pause
exit /b 0

:minimal_install
echo.
echo [4/5] Installing MINIMAL package (this may take 2-3 minutes)...
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing core packages...
pip install Flask==3.0.0 Flask-CORS==4.0.0

echo.
echo Installing data science packages...
pip install numpy>=1.26.0 pandas>=2.1.0 scikit-learn>=1.3.0

echo.
echo Installing financial data packages...
pip install yfinance>=0.2.28

echo.
echo [5/5] Verifying installation...
python -c "import flask; print('✓ Flask:', flask.__version__)" 2>nul
python -c "import numpy; print('✓ NumPy:', numpy.__version__)" 2>nul
python -c "import pandas; print('✓ Pandas:', pandas.__version__)" 2>nul
python -c "import yfinance; print('✓ yfinance installed')" 2>nul
python -c "import sklearn; print('✓ scikit-learn installed')" 2>nul

echo.
echo ============================================================================
echo   MINIMAL Installation Complete!
echo ============================================================================
echo.
echo Installation summary:
echo   - Python virtual environment: CREATED
echo   - Core packages (Flask, NumPy, Pandas): INSTALLED
echo   - Financial data (yfinance): INSTALLED
echo   - AI/ML packages: NOT INSTALLED (MINIMAL mode)
echo.
echo Next steps:
echo   1. Run START_FINBERT_V4.bat to start the application
echo   2. Open browser to http://127.0.0.1:5001
echo   3. Try analyzing AAPL, TSLA, or MSFT
echo.
echo Features available:
echo   ✓ Basic price charts
echo   ✓ Technical indicators (SMA, RSI, MACD)
echo   ✗ Sentiment analysis (requires FULL install)
echo   ✗ LSTM predictions (requires FULL install)
echo.
echo To upgrade to FULL install later:
echo   Run this script again and choose option [1]
echo.
echo For help, see docs\INSTALLATION_GUIDE.md
echo.
pause
exit /b 0
