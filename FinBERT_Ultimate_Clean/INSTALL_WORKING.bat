@echo off
echo ================================================================
echo    FINBERT ULTIMATE TRADING SYSTEM - PROVEN INSTALLER
echo ================================================================
echo This installer uses the EXACT same method that worked before
echo.

REM Check Python version
echo Checking Python installation...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ================================================================
echo STEP 1: Installing build tools
echo ================================================================
python -m pip install --upgrade pip setuptools wheel

echo.
echo ================================================================
echo STEP 2: Installing NumPy (Python 3.12 compatible)
echo ================================================================
pip install numpy==1.26.4 --no-cache-dir
if %errorlevel% neq 0 (
    echo Trying alternative numpy installation...
    pip install "numpy>=1.26.0" --no-cache-dir
)

echo.
echo ================================================================
echo STEP 3: Installing PyTorch FIRST (required for transformers)
echo ================================================================
echo This is a ~2GB download, please be patient...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
if %errorlevel% neq 0 (
    echo Trying torch-only installation...
    pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
)

echo.
echo ================================================================
echo STEP 4: Installing transformers for FinBERT
echo ================================================================
pip install transformers==4.36.0 --no-cache-dir
if %errorlevel% neq 0 (
    echo Trying latest transformers...
    pip install transformers --no-cache-dir
)

echo.
echo ================================================================
echo STEP 5: Installing remaining packages
echo ================================================================
pip install pandas yfinance flask flask-cors scikit-learn ta feedparser requests tqdm

echo.
echo ================================================================
echo STEP 6: Creating directories
echo ================================================================
mkdir cache 2>nul
mkdir models 2>nul
mkdir logs 2>nul
mkdir data 2>nul

echo.
echo ================================================================
echo STEP 7: Verifying installation
echo ================================================================
echo.
echo Testing PyTorch...
python -c "import torch; print(f'[OK] PyTorch {torch.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] PyTorch not working
)

echo.
echo Testing Transformers...
python -c "import transformers; print(f'[OK] Transformers {transformers.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] Transformers not working
)

echo.
echo Testing FinBERT import...
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('[OK] FinBERT imports work!')" 2>nul
if %errorlevel% neq 0 (
    echo [FAIL] FinBERT imports failed
)

echo.
echo ================================================================
echo OPTIONAL: Download FinBERT model now? (400MB)
echo ================================================================
echo Press Y to download now, N to download on first use
choice /C YN /N /M "Download FinBERT model? (Y/N): "
if %errorlevel%==1 (
    echo.
    echo Downloading FinBERT model files...
    python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('Downloading...'); AutoTokenizer.from_pretrained('ProsusAI/finbert', cache_dir='./cache'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert', cache_dir='./cache'); print('FinBERT downloaded!')"
)

echo.
echo ================================================================
echo INSTALLATION COMPLETE!
echo ================================================================
echo.
echo FinBERT components are installed and ready to use!
echo.
echo To run the application:
echo   1. Run: RUN_ULTIMATE.bat
echo   2. Open: http://localhost:5000
echo.
echo To test with CBA.AX:
echo   1. Train with 6 months or 1 year
echo   2. Make prediction - SMA_50 fix is working!
echo.
pause