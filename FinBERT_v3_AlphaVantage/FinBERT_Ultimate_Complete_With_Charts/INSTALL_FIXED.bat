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

:: Keep window open on error
if "%1"=="" (
    cmd /k "%~f0" RUN
    exit /b
)

:: Check Python installation
echo [Step 1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://python.org
    echo.
    echo Press any key to exit...
    pause >nul
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
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo Continuing with system Python...
    ) else (
        echo Activating virtual environment...
        call venv\Scripts\activate.bat
        if errorlevel 1 (
            echo [WARNING] Could not activate virtual environment
            echo Continuing with system Python...
        ) else (
            echo Virtual environment activated.
        )
    )
) else (
    echo Skipping virtual environment (using system Python)
)
echo.

:: Upgrade pip
echo [Step 3/7] Upgrading pip...
python -m pip install --upgrade pip --no-warn-script-location 2>&1
if errorlevel 1 (
    echo [WARNING] Could not upgrade pip, continuing with current version...
)
echo.

:: Install core dependencies
echo [Step 4/7] Installing core dependencies...
echo.

:: Install numpy first (critical for Python 3.12)
echo Installing numpy (Python 3.12 compatible)...
python -m pip install "numpy>=1.26.0" --no-cache-dir
if errorlevel 1 (
    echo [ERROR] Failed to install numpy
    echo Trying alternative installation...
    python -m pip install numpy --no-cache-dir
    if errorlevel 1 (
        echo [ERROR] Could not install numpy. Please run:
        echo    pip install numpy
        echo.
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
)
echo NumPy installed successfully.
echo.

:: Install other scientific packages
echo Installing scientific computing packages...
python -m pip install pandas scikit-learn scipy --no-cache-dir
if errorlevel 1 (
    echo [WARNING] Some scientific packages may have failed
    echo Attempting individual installations...
    python -m pip install pandas --no-cache-dir
    python -m pip install scikit-learn --no-cache-dir
    python -m pip install scipy --no-cache-dir
)
echo.

:: Install financial analysis packages
echo Installing financial analysis packages...
python -m pip install yfinance ta --no-cache-dir
if errorlevel 1 (
    echo [WARNING] Some financial packages may have failed
    echo Attempting individual installations...
    python -m pip install yfinance --no-cache-dir
    python -m pip install ta --no-cache-dir
)

:: Optional packages (don't fail if these don't install)
echo Installing optional data source packages...
python -m pip install alpha-vantage finnhub-python fredapi --no-cache-dir 2>nul
echo.

:: Install web framework
echo Installing Flask and web components...
python -m pip install flask flask-cors requests --no-cache-dir
if errorlevel 1 (
    echo [ERROR] Failed to install Flask
    echo Attempting individual installations...
    python -m pip install flask --no-cache-dir
    python -m pip install flask-cors --no-cache-dir
    python -m pip install requests --no-cache-dir
)

python -m pip install beautifulsoup4 lxml --no-cache-dir 2>nul
echo.

:: Install additional utilities
echo Installing utilities...
python -m pip install python-dotenv tqdm joblib --no-cache-dir 2>nul
echo.

echo [Step 5/7] Installing FinBERT components (optional)...
echo.
echo ================================================================
echo FinBERT provides advanced sentiment analysis but requires:
echo   - ~2GB download for the model
echo   - PyTorch installation (~500MB)
echo   - 4GB+ RAM recommended
echo.
echo The system works WITHOUT FinBERT using fallback sentiment.
echo ================================================================
echo.
set /p install_finbert="Install FinBERT? (y/n): "
if /i "%install_finbert%"=="y" (
    echo.
    echo Installing PyTorch (this may take a few minutes)...
    python -m pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
    if errorlevel 1 (
        echo [ERROR] Failed to install PyTorch
        echo Trying alternative installation...
        python -m pip install torch torchvision torchaudio --no-cache-dir
        if errorlevel 1 (
            echo [WARNING] PyTorch installation failed
            echo FinBERT will not be available
            echo System will use fallback sentiment analysis
        )
    ) else (
        echo PyTorch installed successfully.
    )
    
    echo.
    echo Installing transformers library...
    python -m pip install transformers --no-cache-dir
    if errorlevel 1 (
        echo [WARNING] Transformers installation failed
        echo FinBERT will not be available
        echo System will use fallback sentiment analysis
    ) else (
        echo Transformers installed successfully.
        echo FinBERT will download on first use (~2GB)
    )
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
    (
        echo # FinBERT Ultimate Configuration
        echo # Add your API keys here - optional
        echo FLASK_SKIP_DOTENV=1
        echo.
        echo # Optional API Keys for additional data sources:
        echo # ALPHA_VANTAGE_API_KEY=your_key_here
        echo # IEX_TOKEN=your_token_here
        echo # FINNHUB_API_KEY=your_key_here
        echo # POLYGON_API_KEY=your_key_here
        echo # FRED_API_KEY=your_key_here
    ) > .env
    echo Configuration template created (.env)
) else (
    echo Configuration file already exists (.env)
)
echo.

:: Verify installation
echo ================================================================
echo    Verifying Installation...
echo ================================================================
echo.

python -c "import numpy; print(f'✓ NumPy {numpy.__version__}')" 2>nul || echo ✗ NumPy not found
python -c "import pandas; print('✓ Pandas installed')" 2>nul || echo ✗ Pandas not found
python -c "import sklearn; print('✓ Scikit-learn installed')" 2>nul || echo ✗ Scikit-learn not found
python -c "import flask; print('✓ Flask installed')" 2>nul || echo ✗ Flask not found
python -c "import yfinance; print('✓ yfinance installed')" 2>nul || echo ✗ yfinance not found
python -c "import ta; print('✓ Technical Analysis installed')" 2>nul || echo ✗ TA not found
python -c "import transformers; print('✓ FinBERT support enabled')" 2>nul || echo ○ FinBERT disabled (using fallback)

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
echo.
echo Press any key to close this window...
pause >nul