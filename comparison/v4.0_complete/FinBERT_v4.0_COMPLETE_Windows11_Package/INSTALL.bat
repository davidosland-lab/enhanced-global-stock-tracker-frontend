@echo off
echo ================================================================
echo    FINBERT ULTIMATE TRADING SYSTEM - INSTALLER
echo ================================================================
echo.

REM Check Python version
echo Checking Python installation...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.12 or later
    pause
    exit /b 1
)

REM Check if Python 3.12+
python -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Python 3.12+ is recommended for best compatibility
    echo Current version:
    python --version
    echo.
    echo Continue anyway? (Press Ctrl+C to cancel)
    pause
)

echo.
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Removing old one...
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
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel

echo.
echo ================================================================
echo Installing required packages...
echo ================================================================
echo.

REM Install numpy first for Python 3.12 compatibility
echo Installing NumPy (Python 3.12 compatible)...
pip install "numpy>=1.26.0,<2.0.0"

echo.
echo Installing core packages...
pip install pandas yfinance requests flask flask-cors

echo.
echo Installing scikit-learn and dependencies...
pip install scikit-learn

echo.
echo Installing technical analysis library...
pip install ta

echo.
echo Installing additional data sources (optional)...
pip install feedparser

echo.
echo ================================================================
echo Installing FinBERT components (this may take a while)...
echo ================================================================
echo.

REM IMPORTANT: Install PyTorch FIRST (before transformers)
echo Installing PyTorch (CPU version)...
echo This is a ~2GB download, please be patient...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if %errorlevel% neq 0 (
    echo Trying torch-only installation...
    pip install torch --index-url https://download.pytorch.org/whl/cpu
)

echo.
echo Installing transformers library (AFTER PyTorch)...
pip install transformers
if %errorlevel% neq 0 (
    echo WARNING: Transformers installation had issues
    echo The system will use fallback sentiment analysis
)

echo.
echo ================================================================
echo Creating required directories...
echo ================================================================
mkdir cache 2>nul
mkdir models 2>nul
mkdir logs 2>nul
mkdir data 2>nul

echo.
echo ================================================================
echo Installation Summary:
echo ================================================================
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
python -c "import pandas; print(f'Pandas version: {pandas.__version__}')"
python -c "import sklearn; print(f'Scikit-learn version: {sklearn.__version__}')"
python -c "import flask; print(f'Flask version: {flask.__version__}')"
python -c "import ta; print(f'TA-Lib version: {ta.__version__}')"

echo.
python -c "from transformers import AutoTokenizer; print('✓ Transformers installed successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠ Transformers not available - FinBERT will use fallback mode
) else (
    echo ✓ FinBERT components installed successfully
)

echo.
echo ================================================================
echo Installation completed!
echo ================================================================
echo.
echo To run the application:
echo   1. Run: RUN_ULTIMATE.bat
echo   2. Open: http://localhost:5000
echo.
echo To test with CBA.AX:
echo   1. Train model with 6 months or 1 year data
echo   2. Make prediction - SMA_50 error should be fixed!
echo.
pause