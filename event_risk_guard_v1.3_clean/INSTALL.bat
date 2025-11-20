@echo off
REM Event Risk Guard - Installation Script
REM Installs all required dependencies for the Event Risk Guard system

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ================================================================================
echo Event Risk Guard - Installation
echo ================================================================================
echo.
echo This script will install all required Python dependencies including:
echo   - Core packages (yfinance, yahooquery, pandas, numpy)
echo   - FinBERT (PyTorch + transformers) - ~1-2 GB
echo   - LSTM support (TensorFlow + Keras) - ~400-500 MB
echo   - Technical analysis libraries
echo.
echo TOTAL DOWNLOAD: ~2-2.5 GB (if not already installed)
echo INSTALLATION TIME: 5-15 minutes (depending on internet speed)
echo.
echo Please ensure Python 3.8+ is installed and added to PATH.
echo.
pause

echo.
echo ================================================================================
echo Step 1: Checking Python version...
echo ================================================================================
python --version
if %errorlevel% neq 0 (
    echo.
    echo ✗ ERROR: Python not found in PATH
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Step 2: Upgrading pip...
echo ================================================================================
python -m pip install --upgrade pip

echo.
echo ================================================================================
echo Step 3: Installing yahooquery first (handles lxml dependency)...
echo ================================================================================
echo This package requires lxml ^<5.0.0 and must be installed first.
echo.
python -m pip install "yahooquery>=2.3.7"

echo.
echo ================================================================================
echo Step 4: Installing remaining dependencies from requirements.txt...
echo ================================================================================
echo.
echo This will install:
echo   - PyTorch (FinBERT support)
echo   - Transformers (FinBERT model)
echo   - TensorFlow (LSTM support)
echo   - Keras (LSTM API)
echo   - All supporting packages
echo.
echo Please wait, this may take 5-15 minutes...
echo.

python -m pip install -r requirements.txt

echo.
echo ================================================================================
echo Step 5: Verifying installation...
echo ================================================================================
echo.

REM Create verification script
(
echo import sys
echo try:
echo     import torch
echo     print^(f"✓ PyTorch {torch.__version__} - FinBERT support ready"^)
echo except ImportError:
echo     print^("✗ PyTorch NOT installed - FinBERT will NOT work"^)
echo     sys.exit^(1^)
echo.
echo try:
echo     import transformers
echo     print^(f"✓ Transformers {transformers.__version__} - FinBERT model ready"^)
echo except ImportError:
echo     print^("✗ Transformers NOT installed - FinBERT will NOT work"^)
echo     sys.exit^(1^)
echo.
echo try:
echo     import tensorflow as tf
echo     print^(f"✓ TensorFlow {tf.__version__} - LSTM support ready"^)
echo     lstm_available = True
echo except ImportError:
echo     print^("⚠ TensorFlow NOT installed - LSTM predictions will NOT be available"^)
echo     print^("  System will work with FinBERT-only predictions"^)
echo     lstm_available = False
echo.
echo try:
echo     import yfinance
echo     print^(f"✓ yfinance - Data fetching ready"^)
echo except ImportError:
echo     print^("✗ yfinance NOT installed - Data fetching will fail"^)
echo     sys.exit^(1^)
echo.
echo try:
echo     import yahooquery
echo     print^(f"✓ yahooquery - Fallback data source ready"^)
echo except ImportError:
echo     print^("✗ yahooquery NOT installed - No fallback data source"^)
echo     sys.exit^(1^)
echo.
echo try:
echo     import pandas
echo     print^(f"✓ pandas - Data manipulation ready"^)
echo except ImportError:
echo     print^("✗ pandas NOT installed - System will NOT work"^)
echo     sys.exit^(1^)
echo.
echo print^(^)
echo print^("="*70^)
echo print^("✓ INSTALLATION SUCCESSFUL"^)
echo print^("="*70^)
echo print^(^)
echo if lstm_available:
echo     print^("✓ Full ML stack installed: FinBERT + LSTM"^)
echo else:
echo     print^("✓ FinBERT installed: System ready ^(LSTM optional^)"^)
echo print^(^)
) > verify_install.py

python verify_install.py
set VERIFY_EXIT_CODE=%errorlevel%

REM Cleanup
del verify_install.py

echo.
echo ================================================================================
echo Installation Complete!
echo ================================================================================
echo.

if %VERIFY_EXIT_CODE% equ 0 (
    echo ✓ All core packages verified successfully!
    echo.
    echo Next steps:
    echo   1. Configure models/config/screening_config.json ^(if needed^)
    echo   2. Review models/config/event_calendar.csv ^(add ASX event dates^)
    echo   3. Run TEST_EVENT_RISK_GUARD.bat to verify system
    echo   4. Run RUN_OVERNIGHT_PIPELINE.bat to start screening
    echo.
    echo Documentation:
    echo   - docs/ML_DEPENDENCIES_GUIDE.md - ML packages explained
    echo   - docs/EVENT_RISK_GUARD_IMPLEMENTATION.md - Technical details
    echo   - docs/README_DEPLOYMENT.md - Complete deployment guide
) else (
    echo.
    echo ⚠ WARNING: Some packages may not have installed correctly
    echo.
    echo Please review the errors above and:
    echo   1. Ensure Python 3.8-3.11 is installed ^(NOT 3.12+^)
    echo   2. Check internet connection
    echo   3. Try running INSTALL.bat again
    echo   4. Refer to docs/ML_DEPENDENCIES_GUIDE.md for troubleshooting
)

echo.
echo For detailed package verification, run: VERIFY_INSTALLATION.bat
echo.
pause
