@echo off
echo ========================================================================
echo   FinBERT v4.0 - Prediction Caching System
echo   Complete Installation Script for Windows 11
echo ========================================================================
echo.

REM Check if Python is installed
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher:
    echo 1. Download from: https://www.python.org/downloads/
    echo 2. Run the installer
    echo 3. ✅ CHECK "Add Python to PATH" during installation
    echo 4. Complete the installation
    echo 5. Restart this script
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python found
echo.

REM Check Python version
echo [2/8] Checking Python version compatibility...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: Python 3.8+ is required
    echo Current version:
    python --version
    echo.
    echo Please upgrade Python and try again
    pause
    exit /b 1
)
echo ✅ Python version compatible
echo.

REM Check pip
echo [3/8] Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: pip is not installed
    echo Installing pip...
    python -m ensurepip --upgrade
)
pip --version
echo ✅ pip found
echo.

REM Upgrade pip
echo [4/8] Upgrading pip to latest version...
python -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo ⚠️  WARNING: Could not upgrade pip, continuing with current version
) else (
    echo ✅ pip, setuptools, and wheel upgraded
)
echo.

REM Install core dependencies
echo [5/8] Installing core dependencies...
echo This may take a few minutes...
echo.

echo Installing NumPy (fundamental package)...
pip install "numpy>=1.26.0,<2.0.0"
if %errorlevel% neq 0 (
    echo ⚠️  NumPy installation had issues, trying alternative version...
    pip install numpy
)
echo.

echo Installing Pandas (data analysis)...
pip install pandas
echo.

echo Installing Flask (web framework)...
pip install flask flask-cors
echo.

echo Installing yfinance (stock data)...
pip install yfinance
echo.

echo Installing scikit-learn (machine learning)...
pip install scikit-learn
echo.

echo Installing ta (technical analysis)...
pip install ta
echo.

echo Installing APScheduler (task scheduling)...
pip install apscheduler
echo.

echo Installing requests and other utilities...
pip install requests feedparser
echo.

echo ✅ Core dependencies installed
echo.

REM Install ML/AI packages
echo [6/8] Installing Machine Learning and AI packages...
echo This is a large download (~2-3 GB), please be patient...
echo.

echo Installing PyTorch (CPU version for LSTM)...
echo Note: This download is about 2GB, it may take 5-15 minutes...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if %errorlevel% neq 0 (
    echo ⚠️  PyTorch installation failed, trying alternative method...
    pip install torch --index-url https://download.pytorch.org/whl/cpu
    if %errorlevel% neq 0 (
        echo ⚠️  PyTorch installation failed (optional - LSTM will be limited)
        echo You can install it later with: pip install torch
    ) else (
        echo ✅ PyTorch installed successfully
    )
) else (
    echo ✅ PyTorch installed successfully
)
echo.

echo Installing transformers (for FinBERT sentiment analysis)...
pip install transformers
if %errorlevel% neq 0 (
    echo ⚠️  Transformers installation failed (optional)
    echo FinBERT will use fallback sentiment analysis
    echo You can install it later with: pip install transformers
) else (
    echo ✅ Transformers installed successfully
)
echo.

echo Installing TensorFlow (alternative LSTM backend)...
pip install tensorflow
if %errorlevel% neq 0 (
    echo ⚠️  TensorFlow installation failed (optional)
    echo System will use PyTorch for LSTM if available
    echo You can install it later with: pip install tensorflow
) else (
    echo ✅ TensorFlow installed successfully
)
echo.

REM Create necessary directories
echo [7/8] Creating data directories...
if not exist "trained_models" mkdir trained_models
if not exist "cache" mkdir cache
if not exist "logs" mkdir logs
if not exist "data" mkdir data
echo ✅ Directories created
echo.

REM Verify installation
echo [8/8] Verifying installation...
echo.
echo ========================================================================
echo Installed Packages:
echo ========================================================================

python -c "import numpy; print(f'✓ NumPy version: {numpy.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ NumPy: Not installed
) 

python -c "import pandas; print(f'✓ Pandas version: {pandas.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Pandas: Not installed
)

python -c "import flask; print(f'✓ Flask version: {flask.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Flask: Not installed
)

python -c "import yfinance; print('✓ yfinance: Installed')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ yfinance: Not installed
)

python -c "import sklearn; print(f'✓ scikit-learn version: {sklearn.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ scikit-learn: Not installed
)

python -c "import ta; print(f'✓ TA-Lib version: {ta.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ TA-Lib: Not installed
)

python -c "import apscheduler; print('✓ APScheduler: Installed')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  APScheduler: Not installed (scheduler will be disabled)
)

echo.
echo Machine Learning Packages:
echo.

python -c "import torch; print(f'✓ PyTorch version: {torch.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  PyTorch: Not installed (LSTM features limited)
) else (
    echo   - LSTM neural networks: Available
)

python -c "import tensorflow; print(f'✓ TensorFlow version: {tensorflow.__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  TensorFlow: Not installed (alternative LSTM backend)
)

python -c "from transformers import AutoTokenizer; print('✓ Transformers: Installed')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Transformers: Not installed (FinBERT will use fallback)
) else (
    echo   - FinBERT sentiment analysis: Available
)

echo.
echo ========================================================================
echo   Installation Complete!
echo ========================================================================
echo.
echo ✅ Core system dependencies installed
echo ✅ Machine learning packages configured
echo ✅ Data directories created
echo ✅ System is ready to use
echo.
echo 📊 Features Available:
echo   ✓ Real-time stock data (Yahoo Finance)
echo   ✓ Technical analysis indicators
echo   ✓ Prediction caching system
echo   ✓ Multi-timezone support (US/AU/UK)
echo   ✓ Automated validation scheduler
if exist "venv\Scripts\python.exe" (
    echo   ✓ LSTM neural networks (if PyTorch installed)
    echo   ✓ FinBERT sentiment (if Transformers installed)
) else (
    python -c "import torch; exit(0)" 2>nul
    if %errorlevel% equ 0 (
        echo   ✓ LSTM neural networks
    ) else (
        echo   ⚠ LSTM neural networks (limited - install PyTorch)
    )
    python -c "from transformers import AutoTokenizer; exit(0)" 2>nul
    if %errorlevel% equ 0 (
        echo   ✓ FinBERT sentiment analysis
    ) else (
        echo   ⚠ FinBERT sentiment (fallback mode - install transformers)
    )
)
echo.
echo 🚀 Next Steps:
echo.
echo 1. Start the server:
echo    - Double-click START_SERVER.bat
echo    - Or run: python app_finbert_v4_dev.py
echo.
echo 2. Open your browser:
echo    - Navigate to: http://localhost:5001
echo.
echo 3. Test the system:
echo    - Enter a stock symbol (e.g., AAPL, TSLA, BHP.AX, BP.L)
echo    - Click "Analyze"
echo    - View prediction with status indicator
echo    - Scroll down to see accuracy dashboard
echo.
echo 4. Train LSTM models (optional):
echo    python models/train_lstm.py --symbol AAPL --epochs 50
echo.
echo 📚 Documentation:
echo    - README.txt - Quick start guide
echo    - README_PREDICTION_SYSTEM.md - Complete guide
echo    - INSTALLATION_GUIDE.md - Detailed setup instructions
echo    - QUICK_REFERENCE.txt - Quick reference card
echo.
echo ========================================================================
echo.
pause
