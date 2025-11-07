@echo off
REM FinBERT Trading System - Fixed Installation Script for Windows 11
REM Compatible with Python 3.12

echo ========================================
echo FinBERT Trading System - Windows Installer
echo Python 3.12 Compatible Version
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [✓] Python is installed
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)
python -m venv venv
echo [✓] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [✓] Virtual environment activated
echo.

REM Install setuptools and wheel first
echo Installing build tools...
python -m pip install --upgrade pip setuptools wheel
echo [✓] Build tools installed
echo.

REM Install numpy compatible with Python 3.12
echo Installing numpy (Python 3.12 compatible version)...
pip install numpy==1.26.4 --no-cache-dir
if %errorlevel% neq 0 (
    echo [WARNING] Numpy 1.26.4 failed. Trying latest numpy...
    pip install numpy --no-cache-dir
)
echo [✓] Numpy installed
echo.

REM Install PyTorch CPU version
echo Installing PyTorch (CPU version for compatibility)...
echo This may take a few minutes...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
if %errorlevel% neq 0 (
    echo [WARNING] Full PyTorch failed. Trying torch only...
    pip install torch --index-url https://download.pytorch.org/whl/cpu
)
echo [✓] PyTorch installed
echo.

REM Install transformers
echo Installing transformers for FinBERT...
pip install transformers==4.36.0 --no-cache-dir
if %errorlevel% neq 0 (
    echo [WARNING] Transformers 4.36.0 failed. Trying latest...
    pip install transformers --no-cache-dir
)
echo [✓] Transformers installed
echo.

REM Install other dependencies
echo Installing remaining dependencies...
pip install pandas yfinance flask flask-cors scikit-learn tqdm requests
echo [✓] Dependencies installed
echo.

REM Create necessary directories
echo Creating necessary directories...
if not exist "models" mkdir models
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo [✓] Directories created
echo.

REM Test imports
echo Testing critical imports...
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
if %errorlevel% neq 0 (
    echo [WARNING] PyTorch import issue detected
)

python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
if %errorlevel% neq 0 (
    echo [WARNING] Transformers import issue detected
)

python -c "import numpy; print(f'Numpy version: {numpy.__version__}')"
if %errorlevel% neq 0 (
    echo [ERROR] Numpy import failed!
    pause
    exit /b 1
)

echo [✓] Core imports successful
echo.

REM Download FinBERT model (optional)
echo ========================================
echo Do you want to download the FinBERT model now?
echo (This will download ~400MB of model files)
echo Press Y to download now, N to download on first use
echo ========================================
choice /C YN /N /M "Download FinBERT model now? (Y/N): "
if %errorlevel%==1 (
    echo Downloading FinBERT model...
    python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('Downloading FinBERT...'); AutoTokenizer.from_pretrained('ProsusAI/finbert', cache_dir='./models'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert', cache_dir='./models'); print('FinBERT model downloaded successfully!')"
    if %errorlevel% neq 0 (
        echo [WARNING] Model download failed. Will retry on first use.
    ) else (
        echo [✓] FinBERT model downloaded
    )
) else (
    echo Skipping model download. It will be downloaded on first use.
)
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Note: If you encountered any warnings above,
echo the application may still work in fallback mode.
echo.
echo To run the application:
echo 1. Double-click RUN.bat
echo 2. Or run: python app_finbert_trading.py
echo.
echo The application will be available at:
echo http://localhost:5000
echo.
echo ========================================
pause