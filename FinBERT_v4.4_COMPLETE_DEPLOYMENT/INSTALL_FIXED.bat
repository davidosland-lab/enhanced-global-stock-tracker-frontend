@echo off
REM ===================================================================
REM FinBERT v4.4 - FIXED Installation Script for Windows 11
REM Handles network issues and dependency conflicts
REM ===================================================================

echo ========================================
echo   FinBERT v4.4 Installation (FIXED)
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM Create virtual environment
echo Step 1: Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists
    choice /C YN /M "Do you want to recreate it"
    if errorlevel 2 goto skip_venv
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

:skip_venv

REM Activate virtual environment
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install multitasking separately first (yfinance dependency)
echo Step 4: Installing multitasking (yfinance dependency)...
echo Trying with increased timeout...
pip install --default-timeout=100 multitasking>=0.0.7
if errorlevel 1 (
    echo [WARNING] Failed to install multitasking with timeout, trying without...
    pip install multitasking>=0.0.7
)
echo.

REM Install dependencies from requirements.txt with increased timeout
echo Step 5: Installing dependencies from requirements.txt...
echo This may take several minutes...
echo Using increased timeout for network issues...
echo.
pip install --default-timeout=100 -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Installation with timeout failed, trying without timeout...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        echo.
        echo Troubleshooting:
        echo 1. Check your internet connection
        echo 2. Try using a different network or VPN
        echo 3. Manually install each package:
        echo    pip install flask flask-cors yfinance pandas numpy
        echo 4. Then retry: pip install -r requirements.txt
        pause
        exit /b 1
    )
)
echo [OK] All dependencies installed
echo.

REM Verify critical packages
echo Step 6: Verifying installation...
python -c "import flask; print('[OK] Flask:', flask.__version__)"
python -c "import flask_cors; print('[OK] Flask-CORS: Installed')" 2>nul || echo [WARNING] Flask-CORS not found
python -c "import yfinance; print('[OK] yfinance:', yfinance.__version__)"
python -c "import pandas; print('[OK] pandas:', pandas.__version__)"
python -c "import numpy; print('[OK] numpy:', numpy.__version__)"
python -c "import tensorflow; print('[OK] TensorFlow:', tensorflow.__version__)" 2>nul || echo [INFO] TensorFlow not found (optional)
echo.

REM Create necessary directories
echo Step 7: Creating data directories...
if not exist "data" mkdir data
if not exist "models\saved_models" mkdir models\saved_models
if not exist "models\lstm_models" mkdir models\lstm_models
if not exist "logs" mkdir logs
echo [OK] Directories created
echo.

echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run START_FINBERT.bat to start the server
echo 2. Open browser to http://localhost:5001
echo 3. See QUICK_START.txt for usage instructions
echo.
echo If you encounter issues:
echo - See TROUBLESHOOTING_FLASK_CORS.md
echo - Run FIX_FLASK_CORS.bat
echo - Run VERIFY_INSTALL.bat to check setup
echo.
pause
