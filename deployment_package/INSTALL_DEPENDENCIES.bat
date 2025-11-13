@echo off
REM ============================================================
REM ASX Stock Scanner v4.4.4 - Dependency Installer
REM Automatically installs all required Python packages
REM ============================================================

echo.
echo ============================================================
echo ASX STOCK SCANNER v4.4.4 - DEPENDENCY INSTALLER
echo ============================================================
echo.
echo This script will install Python packages required for:
echo   [1] Quick Technical Scanner (30 MB, 1-2 min)
echo   [2] Full System with LSTM + FinBERT (4 GB, 10-30 min)
echo.
echo ============================================================
echo.

REM Check Python installation
echo [Step 1/5] Checking Python installation...
python --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

python --version
echo OK - Python is installed
echo.

REM Check pip
echo [Step 2/5] Checking pip installation...
pip --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: pip is not available!
    echo Attempting to install pip...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo Failed to install pip. Please install it manually.
        pause
        exit /b 1
    )
)

pip --version
echo OK - pip is installed
echo.

REM Upgrade pip
echo [Step 3/5] Upgrading pip to latest version...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Could not upgrade pip, continuing with current version...
)
echo.

REM Ask user which mode to install
echo [Step 4/5] Choose installation mode:
echo.
echo   [1] Quick Scanner Only (Recommended to start)
echo       - Packages: yahooquery, pandas, numpy, yfinance, pytz, schedule
echo       - Download: ~50 MB
echo       - Time: 1-2 minutes
echo       - Features: Technical screening + Email notifications
echo.
echo   [2] Full System (LSTM + FinBERT + Quick Scanner)
echo       - Packages: All packages including TensorFlow, PyTorch
echo       - Download: ~4 GB
echo       - Time: 10-30 minutes
echo       - Features: Neural network predictions + Sentiment analysis
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" goto install_quick
if "%choice%"=="2" goto install_full
echo Invalid choice, defaulting to Quick Scanner...
goto install_quick

:install_quick
echo.
echo ============================================================
echo Installing QUICK SCANNER dependencies...
echo ============================================================
echo.
echo Installing: yahooquery pandas numpy yfinance pytz schedule
echo.
pip install yahooquery>=2.3.0 pandas>=1.5.0 numpy>=1.24.0 yfinance>=0.2.30 pytz>=2023.3 schedule>=1.2.0
if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Troubleshooting:
    echo   1. Check internet connection
    echo   2. Try: python -m pip install yahooquery pandas numpy yfinance pytz schedule
    echo   3. Check if antivirus is blocking pip
    echo.
    pause
    exit /b 1
)
echo.
echo ============================================================
echo QUICK SCANNER installation complete!
echo ============================================================
goto verify_installation

:install_full
echo.
echo ============================================================
echo Installing FULL SYSTEM dependencies...
echo This will take 10-30 minutes and download ~4 GB
echo ============================================================
echo.
set /p confirm="Are you sure? This is a large download. (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

echo.
echo [Phase 1/4] Installing core packages (yahooquery, pandas, numpy)...
pip install yahooquery>=2.3.0 pandas>=1.5.0 numpy>=1.24.0
if errorlevel 1 goto install_error

echo.
echo [Phase 2/4] Installing data and technical analysis packages...
pip install yfinance>=0.2.30 requests>=2.31.0 python-dateutil>=2.8.2 pytz>=2023.3 schedule>=1.2.0
if errorlevel 1 goto install_error

echo.
echo [Phase 3/4] Installing LSTM packages (TensorFlow, Keras, scikit-learn)...
echo This is a large download (~500 MB for TensorFlow)...
pip install tensorflow>=2.13.0 keras>=2.13.0 scikit-learn>=1.3.0
if errorlevel 1 (
    echo.
    echo WARNING: TensorFlow installation failed!
    echo.
    echo Trying alternative installation method...
    pip install tensorflow-cpu>=2.13.0 keras>=2.13.0 scikit-learn>=1.3.0
    if errorlevel 1 goto install_error
)

echo.
echo [Phase 4/4] Installing FinBERT packages (Transformers, PyTorch)...
echo This is a VERY large download (~2 GB for PyTorch)...
pip install transformers>=4.30.0 torch>=2.0.0
if errorlevel 1 (
    echo.
    echo WARNING: PyTorch installation failed!
    echo.
    echo Please install PyTorch manually from: https://pytorch.org
    echo For Windows CPU-only: pip install torch --index-url https://download.pytorch.org/whl/cpu
    echo.
    set /p skip_torch="Continue without PyTorch? (Y/N): "
    if /i not "%skip_torch%"=="Y" goto install_error
    echo Continuing without PyTorch - FinBERT sentiment will not be available.
)

echo.
echo ============================================================
echo FULL SYSTEM installation complete!
echo ============================================================
goto verify_installation

:install_error
echo.
echo ============================================================
echo ERROR: Installation failed!
echo ============================================================
echo.
echo Troubleshooting steps:
echo   1. Check your internet connection
echo   2. Try running as Administrator
echo   3. Check if antivirus is blocking pip
echo   4. Try manual installation:
echo      python -m pip install [package_name]
echo.
pause
exit /b 1

:verify_installation
echo.
echo [Step 5/5] Verifying installation...
echo.

REM Verify core packages
echo Checking core packages...
python -c "import yahooquery; print('  OK - yahooquery')" 2>nul
if errorlevel 1 (
    echo   ERROR - yahooquery not found
    set install_status=ERROR
)

python -c "import pandas; print('  OK - pandas')" 2>nul
if errorlevel 1 (
    echo   ERROR - pandas not found
    set install_status=ERROR
)

python -c "import numpy; print('  OK - numpy')" 2>nul
if errorlevel 1 (
    echo   ERROR - numpy not found
    set install_status=ERROR
)

python -c "import yfinance; print('  OK - yfinance')" 2>nul
if errorlevel 1 (
    echo   ERROR - yfinance not found
    set install_status=ERROR
)

python -c "import pytz; print('  OK - pytz')" 2>nul
if errorlevel 1 (
    echo   ERROR - pytz not found
    set install_status=ERROR
)

python -c "import schedule; print('  OK - schedule')" 2>nul
if errorlevel 1 (
    echo   ERROR - schedule not found
    set install_status=ERROR
)

REM Check optional packages
if "%choice%"=="2" (
    echo.
    echo Checking LSTM packages...
    python -c "import tensorflow; print('  OK - tensorflow')" 2>nul
    if errorlevel 1 (
        echo   WARNING - tensorflow not found
    )
    
    echo.
    echo Checking FinBERT packages...
    python -c "import transformers; print('  OK - transformers')" 2>nul
    if errorlevel 1 (
        echo   WARNING - transformers not found
    )
    
    python -c "import torch; print('  OK - torch')" 2>nul
    if errorlevel 1 (
        echo   WARNING - torch not found
    )
)

echo.
echo ============================================================
echo INSTALLATION SUMMARY
echo ============================================================
echo.

if "%install_status%"=="ERROR" (
    echo Status: INCOMPLETE - Some core packages failed to install
    echo.
    echo Please check the errors above and try installing manually.
) else (
    echo Status: SUCCESS - All core packages installed!
    echo.
    echo Next steps:
    echo   1. Read GMAIL_APP_PASSWORD_SETUP.md
    echo   2. Generate Gmail App Password
    echo   3. Update models\config\screening_config.json (line 90)
    echo   4. Test: python test_email_quick.py
    echo   5. Start: python schedule_pipeline.py
)

echo.
echo ============================================================
echo.
pause
