@echo off
REM ============================================
REM ML Core Enhanced Production System
REM Windows 11 Installation Script
REM ============================================

echo.
echo ============================================
echo ML CORE ENHANCED PRODUCTION SYSTEM
echo Windows 11 Installation
echo ============================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from python.org
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo Pip upgraded!
echo.

REM Install required packages
echo Installing required packages...
echo This may take 5-10 minutes...
echo.

REM Install core requirements
pip install scikit-learn pandas numpy scipy --quiet
if %errorlevel% neq 0 goto :error

pip install tensorflow --quiet
if %errorlevel% neq 0 (
    echo Warning: TensorFlow installation failed, continuing...
)

pip install fastapi uvicorn[standard] pydantic --quiet
if %errorlevel% neq 0 goto :error

pip install yfinance python-multipart aiofiles python-dateutil --quiet
if %errorlevel% neq 0 goto :error

REM Try to install optional packages
echo.
echo Installing optional packages...
pip install xgboost --quiet 2>nul
if %errorlevel% neq 0 (
    echo Info: XGBoost not installed, will use GradientBoosting as fallback
)

REM TA-Lib for Windows requires special installation
echo.
echo Note: TA-Lib requires manual installation on Windows
echo Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
echo The system will work without it using fallback calculations
echo.

REM Create necessary directories
echo Creating data directories...
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "logs" mkdir logs
echo Directories created!
echo.

REM Create run script
echo Creating run script...
echo @echo off > run_ml_core.bat
echo echo Starting ML Core Enhanced Production System... >> run_ml_core.bat
echo call venv\Scripts\activate.bat >> run_ml_core.bat
echo python ml_core_enhanced_production.py >> run_ml_core.bat
echo pause >> run_ml_core.bat
echo Run script created!
echo.

REM Success message
echo ============================================
echo INSTALLATION COMPLETE!
echo ============================================
echo.
echo To start the system:
echo   1. Run: run_ml_core.bat
echo   2. Open browser to: http://localhost:8000
echo.
echo To manually start:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: python ml_core_enhanced_production.py
echo.
pause
exit /b 0

:error
echo.
echo ============================================
echo ERROR: Installation failed!
echo ============================================
echo Please check your internet connection and try again
echo Or install packages manually using pip
echo.
pause
exit /b 1