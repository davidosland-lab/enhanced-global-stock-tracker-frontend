@echo off
cls
echo ================================================================
echo    FinBERT Ultimate Trading System - Complete Installation
echo    Version 3.0 with Charts and Predictions
echo ================================================================
echo.

:: Set error handling to keep window open
setlocal enabledelayedexpansion

:: Check Python
echo [Step 1] Checking Python installation...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://python.org
    pause
    exit /b 1
)
python --version
echo.

:: Create virtual environment
echo [Step 2] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo Virtual environment created.
)
echo.

:: Activate virtual environment
echo [Step 3] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated.
echo.

:: Upgrade pip
echo [Step 4] Upgrading pip...
python -m pip install --upgrade pip
echo.

:: Install numpy FIRST (critical for Python 3.12)
echo [Step 5] Installing NumPy (Python 3.12 compatible)...
pip install "numpy>=1.26.0" --no-cache-dir
echo.

:: Install core dependencies
echo [Step 6] Installing core packages...
pip install pandas scikit-learn scipy --no-cache-dir
echo.

:: Install financial packages
echo [Step 7] Installing financial analysis packages...
pip install yfinance ta alpha-vantage finnhub-python fredapi --no-cache-dir
echo.

:: Install Flask
echo [Step 8] Installing Flask web framework...
pip install flask flask-cors requests beautifulsoup4 lxml --no-cache-dir
echo.

:: Install utilities
echo [Step 9] Installing utilities...
pip install python-dotenv tqdm joblib --no-cache-dir
echo.

:: Install PyTorch FIRST (required for transformers)
echo ================================================================
echo [Step 10] Installing PyTorch for FinBERT...
echo This is REQUIRED and may take a few minutes...
echo ================================================================
echo.

echo Installing PyTorch CPU version...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

:: Check if PyTorch installed successfully
python -c "import torch; print(f'PyTorch {torch.__version__} installed successfully')" >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo [RETRY] PyTorch installation may have issues, trying alternative...
    pip install torch --no-cache-dir
)
echo.

:: Install transformers AFTER PyTorch
echo [Step 11] Installing Transformers for FinBERT...
pip install transformers==4.36.0 --no-cache-dir
echo.

:: Verify FinBERT components
echo [Step 12] Verifying FinBERT installation...
python -c "import torch; import transformers; print('FinBERT components installed successfully!')"
if !errorlevel! neq 0 (
    echo [WARNING] FinBERT components may not be properly installed
    echo The system may have issues with sentiment analysis
)
echo.

:: Create directories
echo [Step 13] Creating required directories...
if not exist "models" mkdir models
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo Directories created.
echo.

:: Create .env file
echo [Step 14] Creating configuration file...
if not exist ".env" (
    echo FLASK_SKIP_DOTENV=1 > .env
    echo # Add optional API keys below: >> .env
    echo # ALPHA_VANTAGE_API_KEY=your_key >> .env
    echo # IEX_TOKEN=your_token >> .env
    echo # FINNHUB_API_KEY=your_key >> .env
    echo Configuration file created.
) else (
    echo Configuration file already exists.
)
echo.

:: Final verification
echo ================================================================
echo    VERIFICATION
echo ================================================================
echo.
echo Checking installations:
python -c "import numpy; print(f'  [OK] NumPy {numpy.__version__}')" 2>nul
python -c "import pandas; print('  [OK] Pandas')" 2>nul
python -c "import sklearn; print('  [OK] Scikit-learn')" 2>nul
python -c "import flask; print('  [OK] Flask')" 2>nul
python -c "import yfinance; print('  [OK] yfinance')" 2>nul
python -c "import torch; print(f'  [OK] PyTorch {torch.__version__}')" 2>nul
python -c "import transformers; print(f'  [OK] Transformers {transformers.__version__}')" 2>nul
echo.

echo ================================================================
echo    INSTALLATION COMPLETE!
echo ================================================================
echo.
echo FinBERT will download on first use (~2GB).
echo This is a one-time download that will be cached.
echo.
echo To start the system:
echo   Run: START.bat
echo.
echo ================================================================
echo.
pause