@echo off
REM FinBERT Trading System - Installation Script for Windows 11
REM This script installs all required dependencies including PyTorch and FinBERT

echo ========================================
echo FinBERT Trading System - Windows Installer
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

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo [✓] Pip upgraded
echo.

REM Install numpy first to avoid conflicts
echo Installing numpy (this is critical for FinBERT)...
pip install numpy==1.24.3 --no-cache-dir
if %errorlevel% neq 0 (
    echo [WARNING] Numpy installation had issues. Trying force reinstall...
    pip install --force-reinstall numpy==1.24.3 --no-cache-dir
)
echo [✓] Numpy installed
echo.

REM Install PyTorch CPU version (smaller and works on all systems)
echo Installing PyTorch (CPU version for compatibility)...
echo This may take a few minutes...
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PyTorch!
    echo Trying alternative installation method...
    pip install torch --index-url https://download.pytorch.org/whl/cpu
)
echo [✓] PyTorch installed
echo.

REM Install transformers and other requirements
echo Installing transformers and other dependencies...
pip install transformers==4.35.2 --no-cache-dir
pip install -r requirements.txt --no-cache-dir
echo [✓] All dependencies installed
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
    echo [ERROR] PyTorch import failed!
    pause
    exit /b 1
)

python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
if %errorlevel% neq 0 (
    echo [ERROR] Transformers import failed!
    pause
    exit /b 1
)

python -c "import numpy; print(f'Numpy version: {numpy.__version__}')"
if %errorlevel% neq 0 (
    echo [ERROR] Numpy import failed!
    pause
    exit /b 1
)

echo [✓] All imports successful
echo.

REM Download FinBERT model (optional - will auto-download on first use)
echo ========================================
echo Do you want to download the FinBERT model now?
echo (This will download ~400MB of model files)
echo Press Y to download now, N to download on first use
echo ========================================
choice /C YN /N /M "Download FinBERT model now? (Y/N): "
if %errorlevel%==1 (
    echo Downloading FinBERT model...
    python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('ProsusAI/finbert', cache_dir='./models'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert', cache_dir='./models'); print('FinBERT model downloaded successfully!')"
    echo [✓] FinBERT model downloaded
) else (
    echo Skipping model download. It will be downloaded on first use.
)
echo.

echo ========================================
echo Installation Complete!
echo ========================================
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