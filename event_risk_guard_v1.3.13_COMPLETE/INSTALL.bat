@echo off
REM Event Risk Guard v1.3.13 - Dependency Installer
REM Automatically installs all required Python packages

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ================================================================================
echo EVENT RISK GUARD v1.3.13 - DEPENDENCY INSTALLER
echo ================================================================================
echo.
echo This script will install all required Python dependencies including:
echo   - Core packages (yfinance, pandas, numpy, scikit-learn)
echo   - FinBERT (PyTorch + transformers) - ~1-2 GB
echo   - LSTM support (TensorFlow) - ~400-500 MB
echo   - Technical analysis libraries (ta)
echo   - Web framework (Flask)
echo.
echo TOTAL DOWNLOAD: ~2-2.5 GB (if not already installed)
echo INSTALLATION TIME: 5-15 minutes (depending on internet speed)
echo.
echo Requirements:
echo   - Python 3.8 or higher installed
echo   - pip (Python package installer) available
echo   - Internet connection
echo.
echo Regime Engine packages (REQUIRED for best performance):
echo   - hmmlearn (HMM-based regime detection)
echo   - arch (GARCH volatility forecasting)
echo.
echo Optional packages (commented out in requirements.txt):
echo   - xgboost (XGBoost ensemble models)
echo.
pause

echo.
echo ================================================================================
echo CHECKING PYTHON INSTALLATION
echo ================================================================================
echo.

python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Python is installed
echo.

echo ================================================================================
echo CHECKING PIP INSTALLATION
echo ================================================================================
echo.

python -m pip --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip is not available
    echo.
    echo Installing pip...
    python -m ensurepip --upgrade
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install pip
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [SUCCESS] pip is installed
echo.

echo ================================================================================
echo UPGRADING PIP TO LATEST VERSION
echo ================================================================================
echo.

python -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Failed to upgrade pip, continuing with current version...
)

echo.
echo ================================================================================
echo INSTALLING PYTORCH (FinBERT BACKEND)
echo ================================================================================
echo.
echo Installing PyTorch CPU version for compatibility...
echo This works on all systems and is smaller than GPU version (~200MB vs 2GB)
echo.

python -m pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu --no-cache-dir
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] First PyTorch installation method failed, trying alternative...
    python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] PyTorch installation failed!
        echo.
        echo Please install PyTorch manually:
        echo 1. Visit: https://pytorch.org/get-started/locally/
        echo 2. Select your platform (Windows, CPU)
        echo 3. Copy and run the installation command
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [SUCCESS] PyTorch installed
echo.

echo ================================================================================
echo INSTALLING REMAINING PACKAGES
echo ================================================================================
echo.
echo This may take 5-15 minutes depending on your internet connection...
echo.
echo Installing packages:
echo   - flask (web framework)
echo   - pandas, numpy (data manipulation)
echo   - yfinance (stock data download)
echo   - scikit-learn (machine learning)
echo   - tensorflow (deep learning for LSTM)
echo   - transformers (FinBERT sentiment)
echo   - ta (technical analysis)
echo   - and other dependencies...
echo.

python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================================
    echo [ERROR] INSTALLATION FAILED
    echo ================================================================================
    echo.
    echo Some packages failed to install. Common issues:
    echo.
    echo 1. Internet connection problems
    echo    - Check your internet connection
    echo    - Try using a VPN if packages are blocked
    echo.
    echo 2. Insufficient permissions
    echo    - Run this batch file as Administrator
    echo    - Right-click and select "Run as administrator"
    echo.
    echo 3. TensorFlow installation issues (Windows)
    echo    - Make sure you have Python 3.8-3.11 (TensorFlow doesn't support 3.12 yet)
    echo    - Install Visual C++ Redistributable:
    echo      https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    echo 4. PyTorch installation issues
    echo    - Visit https://pytorch.org/get-started/locally/
    echo    - Follow platform-specific instructions
    echo.
    echo 5. Package conflicts
    echo    - Create a virtual environment:
    echo      python -m venv venv
    echo      venv\Scripts\activate
    echo      pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo VERIFYING INSTALLATION
echo ================================================================================
echo.

echo Checking core packages...
echo.

REM Create temporary verification script
(
echo import sys
echo failed = False
echo.
echo print^("Core Data Libraries:"^)
echo print^(^)
echo try:
echo     import pandas
echo     print^(f"  [OK] pandas: {pandas.__version__}"^)
echo except ImportError:
echo     print^("  [FAIL] pandas not installed"^)
echo     failed = True
echo.
echo try:
echo     import numpy
echo     print^(f"  [OK] numpy: {numpy.__version__}"^)
echo except ImportError:
echo     print^("  [FAIL] numpy not installed"^)
echo     failed = True
echo.
echo try:
echo     import yfinance
echo     print^(f"  [OK] yfinance: {yfinance.__version__}"^)
echo except ImportError:
echo     print^("  [FAIL] yfinance not installed"^)
echo     failed = True
echo.
echo try:
echo     import sklearn
echo     print^(f"  [OK] scikit-learn: {sklearn.__version__}"^)
echo except ImportError:
echo     print^("  [FAIL] scikit-learn not installed"^)
echo     failed = True
echo.
echo print^(^)
echo print^("Machine Learning / Deep Learning:"^)
echo print^(^)
echo.
echo try:
echo     import tensorflow as tf
echo     print^(f"  [OK] tensorflow: {tf.__version__} - LSTM training"^)
echo except ImportError:
echo     print^("  [FAIL] tensorflow not installed - LSTM training will NOT work"^)
echo     failed = True
echo.
echo try:
echo     import transformers
echo     print^(f"  [OK] transformers: {transformers.__version__} - FinBERT sentiment"^)
echo except ImportError:
echo     print^("  [FAIL] transformers not installed - FinBERT will NOT work"^)
echo     failed = True
echo.
echo try:
echo     import torch
echo     print^(f"  [OK] torch: {torch.__version__} - PyTorch (FinBERT backend)"^)
echo except ImportError:
echo     print^("  [FAIL] torch not installed - FinBERT will NOT work"^)
echo     failed = True
echo.
echo print^(^)
echo print^("Web Framework and Technical Analysis:"^)
echo print^(^)
echo.
echo try:
echo     import flask
echo     print^(f"  [OK] flask: {flask.__version__} - Web UI"^)
echo except ImportError:
echo     print^("  [FAIL] flask not installed - Web UI will NOT work"^)
echo     failed = True
echo.
echo try:
echo     import ta
echo     print^(f"  [OK] ta: {ta.__version__} - Technical indicators"^)
echo except ImportError:
echo     print^("  [FAIL] ta not installed - Technical analysis will NOT work"^)
echo     failed = True
echo.
echo print^(^)
echo print^("Checking regime engine packages..."^)
echo print^(^)
echo.
echo try:
echo     import hmmlearn
echo     print^(f"  [OK] hmmlearn: {hmmlearn.__version__} - HMM regime detection"^)
echo except ImportError:
echo     print^("  [WARNING] hmmlearn not installed - using GMM fallback"^)
echo     print^("            Install hmmlearn for better regime detection accuracy"^)
echo.
echo try:
echo     import arch
echo     print^(f"  [OK] arch: {arch.__version__} - GARCH volatility forecasting"^)
echo except ImportError:
echo     print^("  [WARNING] arch not installed - using EWMA fallback"^)
echo     print^("            Install arch for better volatility forecasting"^)
echo.
echo print^(^)
echo print^("Checking optional packages..."^)
echo print^(^)
echo.
echo try:
echo     import xgboost
echo     print^(f"  [OK] xgboost: {xgboost.__version__}"^)
echo except ImportError:
echo     print^("  [OPTIONAL] xgboost not installed (ensemble disabled)"^)
echo.
echo if failed:
echo     sys.exit^(1^)
) > verify_install_temp.py

python verify_install_temp.py
set VERIFY_EXIT_CODE=%errorlevel%

REM Cleanup
del verify_install_temp.py

if %VERIFY_EXIT_CODE% NEQ 0 (
    echo.
    echo ================================================================================
    echo [WARNING] SOME PACKAGES FAILED TO INSTALL
    echo ================================================================================
    echo.
    echo Some required packages could not be verified. The system may not work properly.
    echo Please review the error messages above and try installing failed packages manually:
    echo.
    echo   pip install [package-name]
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo [SUCCESS] INSTALLATION COMPLETE
echo ================================================================================
echo.
echo All required packages have been installed successfully!
echo.
echo Next steps:
echo.
echo 1. Test the installation:
echo    - Run: RUN_DIAGNOSTIC_SAFE.bat
echo    - Expected: Regime detection results (HIGH_VOL, NORMAL, or CALM)
echo.
echo 2. Run the full pipeline:
echo    - Run: RUN_PIPELINE.bat
echo    - Expected: 70-110 minutes for first run (trains 86 LSTM models)
echo.
echo 3. View results in web UI:
echo    - Run: RUN_WEB_UI.bat
echo    - Open browser: http://localhost:5000
echo.
echo Optional: Install xgboost for ensemble models
echo    - Edit requirements.txt (uncomment xgboost)
echo    - Run this INSTALL.bat again
echo.
echo Note: hmmlearn and arch are now REQUIRED for optimal regime engine performance
echo.
pause
