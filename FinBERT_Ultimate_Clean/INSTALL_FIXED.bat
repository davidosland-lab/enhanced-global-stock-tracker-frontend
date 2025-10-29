@echo off
echo ================================================================
echo    FINBERT ULTIMATE TRADING SYSTEM - INSTALLER (FIXED)
echo ================================================================
echo.

REM Check Python version
echo Checking Python installation...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or later
    pause
    exit /b 1
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
echo Installing core packages (Phase 1)...
echo ================================================================
echo.

REM Install numpy first for Python 3.12 compatibility
echo Installing NumPy (Python 3.12 compatible)...
pip install "numpy>=1.26.0,<2.0.0"
if %errorlevel% neq 0 (
    echo Trying alternative numpy installation...
    pip install numpy --upgrade
)

echo.
echo Installing pandas and data packages...
pip install pandas yfinance requests

echo.
echo Installing Flask web framework...
pip install flask flask-cors

echo.
echo Installing scikit-learn for ML...
pip install scikit-learn

echo.
echo Installing technical analysis library...
pip install ta

echo.
echo Installing feedparser for RSS feeds...
pip install feedparser

echo.
echo ================================================================
echo Core packages installed successfully!
echo ================================================================
echo.
echo ================================================================
echo FinBERT/Transformers Installation (OPTIONAL)
echo ================================================================
echo.
echo NOTE: FinBERT is optional. The system will work without it
echo using fallback sentiment analysis.
echo.
echo Do you want to install FinBERT components? (Y/N)
echo (This requires ~2GB download and may take 10-15 minutes)
echo.
set /p install_finbert="Install FinBERT? (Y/N): "

if /i "%install_finbert%"=="Y" (
    echo.
    echo Installing PyTorch first (required for transformers)...
    echo This may take several minutes...
    
    REM Install CPU-only torch to avoid CUDA issues
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    
    if %errorlevel% neq 0 (
        echo.
        echo WARNING: PyTorch installation failed.
        echo Trying alternative installation method...
        pip install torch --no-cache-dir
    )
    
    echo.
    echo Installing transformers library...
    pip install transformers --no-deps
    pip install transformers
    
    if %errorlevel% neq 0 (
        echo.
        echo WARNING: Transformers installation had issues.
        echo The system will use fallback sentiment analysis.
    ) else (
        echo ✓ FinBERT components installed!
    )
) else (
    echo.
    echo Skipping FinBERT installation.
    echo The system will use rule-based sentiment analysis.
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
echo Verifying Installation...
echo ================================================================
python -c "import numpy; print(f'✓ NumPy {numpy.__version__}')" 2>nul || echo ✗ NumPy not installed
python -c "import pandas; print(f'✓ Pandas {pandas.__version__}')" 2>nul || echo ✗ Pandas not installed
python -c "import sklearn; print(f'✓ Scikit-learn {sklearn.__version__}')" 2>nul || echo ✗ Scikit-learn not installed
python -c "import flask; print(f'✓ Flask {flask.__version__}')" 2>nul || echo ✗ Flask not installed
python -c "import yfinance; print(f'✓ yfinance {yfinance.__version__}')" 2>nul || echo ✗ yfinance not installed
python -c "import ta; print(f'✓ TA-lib {ta.__version__}')" 2>nul || echo ✗ TA-lib not installed

echo.
python -c "import torch; print(f'✓ PyTorch {torch.__version__}')" 2>nul || echo ℹ PyTorch not installed (optional)
python -c "import transformers; print(f'✓ Transformers {transformers.__version__}')" 2>nul || echo ℹ Transformers not installed (optional)

echo.
echo ================================================================
echo INSTALLATION COMPLETE!
echo ================================================================
echo.
echo The system is ready to use with or without FinBERT.
echo.
echo To run the application:
echo   1. Run: RUN_ULTIMATE.bat
echo   2. Open: http://localhost:5000
echo.
echo To test the SMA_50 fix with CBA.AX:
echo   1. Train with 6 months or 1 year data
echo   2. Make predictions - no more errors!
echo.
pause