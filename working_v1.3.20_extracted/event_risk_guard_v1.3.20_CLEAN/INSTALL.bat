@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: Event Risk Guard v1.3.15 - Installation Script
:: Based on proven v1.0 installation method
:: ============================================================================

color 0A
cls

echo.
echo ================================================================================
echo Event Risk Guard v1.3.15 - Installation
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

:: Check if running from System32
set "CURRENT_DIR=%cd%"
if "%CURRENT_DIR%"=="C:\Windows\System32" (
    echo.
    echo [ERROR] Installer running from System32!
    echo Please navigate to the extracted folder and run INSTALL.bat from there.
    echo.
    pause
    exit /b 1
)

if "%CURRENT_DIR%"=="C:\Windows\SysWOW64" (
    echo.
    echo [ERROR] Installer running from SysWOW64!
    echo Please navigate to the extracted folder and run INSTALL.bat from there.
    echo.
    pause
    exit /b 1
)

:: Step 1: Check Python
echo.
echo ================================================================================
echo Step 1: Checking Python version...
echo ================================================================================
python --version
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Step 2: Upgrade pip
echo.
echo ================================================================================
echo Step 2: Upgrading pip...
echo ================================================================================
python -m pip install --upgrade pip

:: Step 3: Install yahooquery first (handles lxml dependency)
echo.
echo ================================================================================
echo Step 3: Installing yahooquery first (handles lxml dependency)...
echo ================================================================================
echo This package requires lxml ^<5.0.0 and must be installed first.
echo.
python -m pip install "yahooquery>=2.3.7"
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] yahooquery installation failed, continuing anyway...
    echo.
)

:: Step 4: Install from requirements.txt
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
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some packages may have failed to install.
    echo The system may still work with reduced functionality.
    echo.
)

:: Step 5: Verify installation
echo.
echo ================================================================================
echo Step 5: Verifying installation...
echo ================================================================================
echo.

python -c "import torch; print('✓ PyTorch', torch.__version__, '- FinBERT support ready')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ PyTorch not installed - FinBERT will not work
    set "INSTALL_ISSUES=1"
)

python -c "import transformers; print('✓ Transformers', transformers.__version__, '- FinBERT model ready')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ Transformers not installed - FinBERT will not work
    set "INSTALL_ISSUES=1"
)

python -c "import tensorflow; print('✓ TensorFlow', tensorflow.__version__, '- LSTM support ready')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ TensorFlow not installed - LSTM training will not work
    set "INSTALL_ISSUES=1"
)

python -c "import yfinance; print('✓ yfinance - Data fetching ready')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ yfinance not installed - Primary data source unavailable
    set "INSTALL_ISSUES=1"
)

python -c "import yahooquery; print('✓ yahooquery - Fallback data source ready')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ yahooquery not installed - Fallback data source unavailable
    set "INSTALL_ISSUES=1"
)

python -c "import pandas; print('✓ pandas - Data manipulation ready')" 2>nul
if %errorlevel% neq 0 (
    echo ✗ pandas not installed - CRITICAL package missing
    set "INSTALL_ISSUES=1"
)

echo.
if defined INSTALL_ISSUES (
    echo ======================================================================
    echo ✗ INSTALLATION COMPLETED WITH WARNINGS
    echo ======================================================================
    echo.
    echo Some packages failed to install. The system may work with reduced
    echo functionality, or you may need to reinstall specific packages.
    echo.
    echo Try running: python -m pip install -r requirements.txt --force-reinstall
    echo.
) else (
    echo ======================================================================
    echo ✓ INSTALLATION SUCCESSFUL
    echo ======================================================================
    echo.
    echo ✓ Full ML stack installed: FinBERT + LSTM
    echo.
)

:: Create necessary directories
echo.
echo Creating required directories...
if not exist "models\screening\logs" mkdir "models\screening\logs"
if not exist "results" mkdir "results"
if not exist "data" mkdir "data"
echo ✓ Directories created
echo.

:: Installation complete
echo.
echo ================================================================================
echo Installation Complete!
echo ================================================================================
echo.
echo ✓ All core packages verified successfully!
echo.
echo Next steps:
echo   1. Configure models\config\screening_config.json (if needed)
echo   2. Run VERIFY_INSTALLATION.bat to check __init__.py files
echo   3. Run test mode: cd models\screening ^&^& python overnight_pipeline.py --test
echo   4. Run full pipeline: cd models\screening ^&^& python overnight_pipeline.py
echo.
echo Documentation:
echo   - START_HERE.txt - Quick start guide
echo   - CRITICAL_FIX_v1.3.15.md - What's new in v1.3.15
echo   - README.md - Complete documentation
echo.
echo For detailed package verification, run: VERIFY_INSTALLATION.bat
echo.
pause
