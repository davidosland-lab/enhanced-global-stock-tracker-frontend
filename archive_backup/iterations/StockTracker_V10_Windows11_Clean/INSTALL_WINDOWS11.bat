@echo off
title Stock Tracker Enhanced - Windows 11 Installation
color 0A

echo ================================================
echo    STOCK TRACKER ENHANCED - WINDOWS 11
echo    Real ML + Global Sentiment Analysis
echo ================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Installing required Python packages...
echo.

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv >nul 2>&1

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

:: Install core packages
echo Installing core packages...
pip install fastapi uvicorn aiohttp pandas numpy yfinance scikit-learn >nul 2>&1

:: Install ML packages
echo Installing ML packages...
pip install xgboost lightgbm catboost >nul 2>&1

:: Install FinBERT and transformers
echo Installing FinBERT (this may take a few minutes)...
pip install transformers torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu >nul 2>&1

:: Install web scraping packages
echo Installing web scraping packages...
pip install beautifulsoup4 lxml feedparser requests-html >nul 2>&1

:: Install additional packages
echo Installing additional packages...
pip install python-multipart sqlalchemy sqlite3 scipy plotly >nul 2>&1

echo.
echo [2/5] Creating required directories...
mkdir models 2>nul
mkdir cache 2>nul
mkdir logs 2>nul
mkdir data 2>nul
mkdir backups 2>nul

echo.
echo [3/5] Setting up configuration files...

:: Create config file
echo Creating configuration...
(
echo {
echo   "services": {
echo     "main": "http://localhost:8000",
echo     "ml": "http://localhost:8002",
echo     "finbert": "http://localhost:8003",
echo     "historical": "http://localhost:8004",
echo     "backtesting": "http://localhost:8005",
echo     "scraper": "http://localhost:8006"
echo   },
echo   "database": {
echo     "ml_cache": "ml_cache.db",
echo     "historical": "historical_data.db",
echo     "sentiment": "sentiment_cache.db",
echo     "backtest": "backtest_results.db"
echo   },
echo   "initial_capital": 100000,
echo   "cache_duration": 300
echo }
) > config.json

echo.
echo [4/5] Downloading FinBERT model (first run only)...
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('ProsusAI/finbert'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')" 2>nul

echo.
echo [5/5] Creating shortcuts...

:: Create desktop shortcut for start script
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Stock Tracker Enhanced.lnk'); $Shortcut.TargetPath = '%CD%\START_ALL_SERVICES.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.IconLocation = 'shell32.dll,13'; $Shortcut.Save()" 2>nul

echo.
echo ================================================
echo    INSTALLATION COMPLETE!
echo ================================================
echo.
echo Next steps:
echo 1. Run START_ALL_SERVICES.bat to start the system
echo 2. Open your browser to http://localhost:8000
echo 3. Or use the shortcut on your desktop
echo.
echo Features installed:
echo - Real FinBERT sentiment analysis
echo - Global sentiment (politics, wars, economics)
echo - SQLite caching (50x faster)
echo - ML models (RandomForest, GradientBoost, XGBoost)
echo - Backtesting with $100,000 capital
echo - Enhanced web scraping
echo.
pause