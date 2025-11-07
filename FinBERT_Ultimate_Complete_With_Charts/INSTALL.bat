@echo off
cls
echo ================================================================
echo    FinBERT Ultimate Trading System - Complete Installation
echo    Including: Predictions, Next-Day Prices, and Charts
echo ================================================================
echo.
echo Version: 3.0 Complete Edition
echo Date: October 2024
echo Python: 3.10+ (3.12 recommended)
echo.
echo ================================================================
echo.

:: Check Python installation
echo [Step 1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://python.org
    pause
    exit /b 1
)
python --version
echo.

:: Create virtual environment (optional but recommended)
echo [Step 2/7] Setting up environment...
echo.
echo Do you want to create a virtual environment? (Recommended)
echo This keeps your system Python clean and avoids conflicts.
echo.
set /p create_venv="Create virtual environment? (y/n): "
if /i "%create_venv%"=="y" (
    echo Creating virtual environment...
    python -m venv venv
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo Skipping virtual environment (using system Python)
)
echo.

:: Upgrade pip
echo [Step 3/7] Upgrading pip...
python -m pip install --upgrade pip --no-warn-script-location
echo.

:: Install core dependencies
echo [Step 4/7] Installing core dependencies...
echo.

:: Install numpy first (critical for Python 3.12)
echo Installing numpy (Python 3.12 compatible)...
pip install "numpy>=1.26.0" --no-cache-dir
if errorlevel 1 (
    echo [ERROR] Failed to install numpy
    pause
    exit /b 1
)

:: Install other scientific packages
echo Installing scientific computing packages...
pip install pandas scikit-learn scipy --no-cache-dir

:: Install financial analysis packages
echo Installing financial analysis packages...
pip install yfinance ta alpha-vantage finnhub-python fredapi --no-cache-dir

:: Install web framework
echo Installing Flask and web components...
pip install flask flask-cors requests beautifulsoup4 lxml --no-cache-dir

:: Install additional utilities
echo Installing utilities...
pip install python-dotenv tqdm joblib --no-cache-dir

echo.
echo [Step 5/7] Installing FinBERT components (optional)...
echo.
echo FinBERT provides advanced sentiment analysis but requires ~2GB download.
echo The system works without it using fallback sentiment analysis.
echo.
set /p install_finbert="Install FinBERT? (y/n): "
if /i "%install_finbert%"=="y" (
    echo Installing PyTorch (required for FinBERT)...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
    
    echo Installing transformers...
    pip install transformers --no-cache-dir
    
    echo FinBERT will download on first use (~2GB)
) else (
    echo Skipping FinBERT (using fallback sentiment)
)
echo.

:: Create necessary directories
echo [Step 6/7] Creating required directories...
if not exist "models" mkdir models
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo Directories created: models, cache, logs, data
echo.

:: Create .env file template
echo [Step 7/7] Creating configuration template...
if not exist ".env" (
    echo # FinBERT Ultimate Configuration > .env
    echo # Add your API keys here (optional) >> .env
    echo FLASK_SKIP_DOTENV=1 >> .env
    echo # ALPHA_VANTAGE_API_KEY=your_key_here >> .env
    echo # IEX_TOKEN=your_token_here >> .env
    echo # FINNHUB_API_KEY=your_key_here >> .env
    echo # POLYGON_API_KEY=your_key_here >> .env
    echo # FRED_API_KEY=your_key_here >> .env
    echo Configuration template created (.env)
) else (
    echo Configuration file already exists (.env)
)
echo.

:: Final message
echo ================================================================
echo    Installation Complete!
echo ================================================================
echo.
echo System Features:
echo   ✓ Real-time stock data from Yahoo Finance
echo   ✓ Technical indicators (RSI, MACD, Bollinger Bands, etc.)
echo   ✓ AI predictions with Random Forest
echo   ✓ Next-day price predictions
echo   ✓ 5-10 day price targets
echo   ✓ Sentiment analysis (FinBERT or fallback)
echo   ✓ Professional charting interface
echo   ✓ Economic indicators dashboard
echo   ✓ News sentiment analysis
echo.
echo To start the system:
echo   1. Run: START.bat
echo   2. Charts will open automatically
echo   3. API available at: http://localhost:5000
echo.
echo Optional: Add API keys to .env file for more data sources
echo.
echo ================================================================
pause