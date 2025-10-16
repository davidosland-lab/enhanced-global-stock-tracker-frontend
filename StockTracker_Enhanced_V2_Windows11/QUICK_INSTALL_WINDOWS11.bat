@echo off
title Quick Install - Stock Tracker Enhanced v2.0
cls

echo ================================================================================
echo           STOCK TRACKER ENHANCED v2.0 - QUICK INSTALLATION
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python 3.8 or higher:
    echo 1. Download from: https://www.python.org/downloads/
    echo 2. IMPORTANT: Check "Add Python to PATH" during installation
    echo 3. Run this script again after Python installation
    echo.
    pause
    exit /b 1
)

echo [✓] Python detected
echo.

REM Create virtual environment (optional but recommended)
echo Creating virtual environment...
python -m venv venv >nul 2>&1
if exist venv (
    echo [✓] Virtual environment created
    call venv\Scripts\activate.bat
) else (
    echo [!] Could not create virtual environment, continuing with global install...
)
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet >nul 2>&1
echo [✓] Pip upgraded
echo.

REM Install core requirements
echo Installing core packages (this may take 2-3 minutes)...
pip install fastapi uvicorn pandas numpy yfinance scikit-learn scipy --quiet --no-warn-script-location >nul 2>&1
if errorlevel 1 (
    echo [!] Warning: Some core packages failed to install
) else (
    echo [✓] Core packages installed
)
echo.

REM Install ML packages
echo Installing ML packages...
pip install xgboost --quiet --no-warn-script-location >nul 2>&1
if errorlevel 1 (
    echo [!] XGBoost not installed (will use GradientBoosting as fallback)
) else (
    echo [✓] XGBoost installed
)
echo.

REM Install FinBERT (this is large, ~400MB)
echo Installing FinBERT for sentiment analysis (may take 3-5 minutes)...
pip install transformers torch --quiet --no-warn-script-location >nul 2>&1
if errorlevel 1 (
    echo [!] FinBERT not installed (sentiment analysis will be limited)
) else (
    echo [✓] FinBERT installed
)
echo.

REM Try to install TA-Lib (often fails on Windows without wheel)
echo Attempting TA-Lib installation...
pip install TA-Lib --quiet --no-warn-script-location >nul 2>&1
if errorlevel 1 (
    echo [!] TA-Lib not installed (using basic indicators)
    echo     For full features, download wheel from:
    echo     https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
) else (
    echo [✓] TA-Lib installed
)
echo.

echo ================================================================================
echo                        INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo Next Steps:
echo 1. Run START_ALL_SERVICES.bat to start the system
echo 2. Open http://localhost:8000 in your browser
echo.
echo Or run individual components:
echo - start_enhanced_ml_system.bat : Just ML system
echo.
pause