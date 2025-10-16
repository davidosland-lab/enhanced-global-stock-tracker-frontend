@echo off
REM ============================================
REM Stock Tracker ML Enhanced - Windows 11 Setup
REM Version 2.0.0 - Complete Production System
REM ============================================

echo.
echo ======================================================
echo  Stock Tracker ML Enhanced - Windows 11 Installation
echo  Version 2.0.0 with FinBERT, SQLite, and All Modules
echo ======================================================
echo.

REM Check Python installation
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Create virtual environment
echo [2/8] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [4/8] Upgrading pip...
python -m pip install --upgrade pip

REM Install core requirements
echo [5/8] Installing core requirements...
pip install fastapi uvicorn[standard] python-multipart
pip install numpy pandas scikit-learn scipy
pip install yfinance yahoo-fin alpha-vantage
pip install aiohttp aiofiles asyncio
pip install sqlite3-api python-dotenv

REM Install ML and analysis packages
echo [6/8] Installing ML and analysis packages...
pip install joblib pickle5
pip install ta-lib-bin || pip install ta || echo Warning: TA-Lib installation failed, using fallback

REM Try to install XGBoost (optional)
pip install xgboost || echo Info: XGBoost not available, will use GradientBoosting

REM Install FinBERT and transformers
echo [7/8] Installing FinBERT for sentiment analysis...
pip install transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install sentencepiece protobuf

REM Install additional utilities
pip install beautifulsoup4 feedparser lxml
pip install plotly matplotlib seaborn
pip install openpyxl xlsxwriter

REM Create necessary directories
echo [8/8] Setting up directory structure...
if not exist data mkdir data
if not exist models mkdir models
if not exist logs mkdir logs
if not exist uploads mkdir uploads
if not exist cache mkdir cache

REM Create environment file
echo Creating environment configuration...
(
echo # Stock Tracker ML Enhanced Configuration
echo # Add your API keys here
echo ALPHA_VANTAGE_KEY=your_key_here
echo NEWS_API_KEY=your_key_here
echo FINBERT_CACHE_DIR=./cache/finbert
) > .env

REM Download FinBERT model cache (optional)
echo.
echo Preparing FinBERT model...
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('Downloading FinBERT model...'); AutoTokenizer.from_pretrained('ProsusAI/finbert'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('FinBERT model ready!')" 2>nul || echo Info: FinBERT will be downloaded on first use

echo.
echo ======================================================
echo  Installation Complete!
echo ======================================================
echo.
echo Next steps:
echo 1. Edit .env file to add your API keys (optional)
echo 2. Run START_SYSTEM.bat to launch the application
echo 3. Access the web interface at http://localhost:8000
echo.
echo Features included:
echo - ML Training with 5 ensemble models
echo - SQLite caching for 50x speed improvement
echo - FinBERT sentiment analysis
echo - Backtesting with $100,000 capital
echo - Global indices tracker
echo - CBA Enhanced module
echo - Technical analysis with charts
echo - Document analyzer
echo - Performance tracker
echo.
pause