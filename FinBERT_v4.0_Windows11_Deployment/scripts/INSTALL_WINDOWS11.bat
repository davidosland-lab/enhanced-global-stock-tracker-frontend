@echo off
REM =========================================================================
REM FinBERT v4.0 - Windows 11 Installation Script
REM Complete AI/ML Trading System with Real Sentiment Analysis
REM =========================================================================

echo.
echo ========================================================================
echo   FinBERT v4.0 - Windows 11 Installation
echo   Full AI/ML Experience with Real News Sentiment
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8 or higher is required
    echo Your Python version is too old. Please upgrade.
    pause
    exit /b 1
)

echo [OK] Python version is compatible
echo.

REM Navigate to deployment directory
cd /d "%~dp0.."

echo ========================================================================
echo   Step 1: Creating Virtual Environment
echo ========================================================================
echo.

if exist venv (
    echo [INFO] Virtual environment already exists
    echo [INFO] Removing old virtual environment...
    rmdir /s /q venv
)

echo [INFO] Creating new virtual environment...
python -m venv venv

if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

echo ========================================================================
echo   Step 2: Activating Virtual Environment
echo ========================================================================
echo.

call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

echo ========================================================================
echo   Step 3: Upgrading pip
echo ========================================================================
echo.

python -m pip install --upgrade pip

if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)

echo.

echo ========================================================================
echo   Step 4: Installing Dependencies
echo   This may take 10-20 minutes depending on your internet speed
echo ========================================================================
echo.
echo Choose installation type:
echo.
echo [1] FULL INSTALL - Complete AI/ML (TensorFlow + FinBERT + News Scraping)
echo     - Size: ~900MB
echo     - Time: 10-20 minutes
echo     - Features: All features enabled
echo.
echo [2] MINIMAL INSTALL - Basic features only (No AI/ML)
echo     - Size: ~50MB
echo     - Time: 2-3 minutes
echo     - Features: Charts and basic analysis only
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo [INFO] Installing FULL package with AI/ML...
    echo [INFO] This includes:
    echo   - TensorFlow (LSTM neural networks)
    echo   - PyTorch + FinBERT (sentiment analysis)
    echo   - BeautifulSoup + aiohttp (news scraping)
    echo   - All dependencies
    echo.
    
    pip install -r requirements-full.txt
    
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Installation failed!
        echo [INFO] Trying alternative installation method...
        echo.
        pip install Flask Flask-CORS yfinance pandas numpy scikit-learn beautifulsoup4 aiohttp lxml
        
        if %errorlevel% neq 0 (
            echo [ERROR] Alternative installation also failed
            echo [INFO] You can try manual installation later
        )
    )
    
    echo.
    echo [INFO] Attempting to install AI/ML packages...
    pip install tensorflow torch transformers sentencepiece 2>nul
    
    if %errorlevel% neq 0 (
        echo [WARNING] Some AI/ML packages failed to install
        echo [INFO] The system will work with basic features
        echo [INFO] To enable AI/ML later, run:
        echo   pip install tensorflow torch transformers sentencepiece
    )
    
) else if "%choice%"=="2" (
    echo.
    echo [INFO] Installing MINIMAL package...
    pip install -r requirements-minimal.txt
    
    if %errorlevel% neq 0 (
        echo [ERROR] Installation failed!
        pause
        exit /b 1
    )
) else (
    echo [ERROR] Invalid choice. Please run the script again.
    pause
    exit /b 1
)

echo.
echo [OK] Dependencies installed
echo.

echo ========================================================================
echo   Step 5: Verifying Installation
echo ========================================================================
echo.

python -c "import flask; print('[OK] Flask installed:', flask.__version__)"
python -c "import yfinance; print('[OK] yfinance installed')"
python -c "import pandas; print('[OK] pandas installed')"
python -c "import numpy; print('[OK] numpy installed')"

echo.
echo [INFO] Checking AI/ML packages...
python -c "import tensorflow; print('[OK] TensorFlow installed:', tensorflow.__version__)" 2>nul || echo [SKIP] TensorFlow not installed (optional)
python -c "import torch; print('[OK] PyTorch installed:', torch.__version__)" 2>nul || echo [SKIP] PyTorch not installed (optional)
python -c "import transformers; print('[OK] Transformers installed')" 2>nul || echo [SKIP] Transformers not installed (optional)
python -c "from bs4 import BeautifulSoup; print('[OK] BeautifulSoup installed')" 2>nul || echo [SKIP] BeautifulSoup not installed (optional)

echo.

echo ========================================================================
echo   Installation Complete!
echo ========================================================================
echo.
echo [SUCCESS] FinBERT v4.0 is now installed!
echo.
echo To start the application:
echo   1. Double-click "START_FINBERT_V4.bat" in the main directory
echo   2. OR run: python app_finbert_v4_dev.py
echo.
echo The application will be available at:
echo   http://localhost:5001
echo.
echo To train LSTM models:
echo   Use the web interface or run:
echo   python models/train_lstm.py --symbol AAPL --epochs 50
echo.
echo Documentation is available in the "docs" folder.
echo.
pause
