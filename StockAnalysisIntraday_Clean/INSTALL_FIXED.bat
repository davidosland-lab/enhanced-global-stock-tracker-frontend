@echo off
title Stock Analysis Installer
color 0A
cls

echo ============================================================
echo     STOCK ANALYSIS WITH INTRADAY SUPPORT - INSTALLER
echo ============================================================
echo.

REM Check Python installation
echo [Step 1] Checking Python installation...
echo.
python --version 2>nul
if errorlevel 1 (
    color 0C
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://python.org
    echo.
    echo IMPORTANT: During installation, make sure to:
    echo   1. Check "Add Python to PATH"
    echo   2. Restart your computer after Python installation
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

python --version
echo Python is installed successfully!
echo.

REM Upgrade pip first
echo [Step 2] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Warning: Could not upgrade pip, continuing anyway...
)
echo.

REM Install packages one by one with error checking
echo [Step 3] Installing required packages...
echo This may take 3-5 minutes on first installation...
echo ============================================================
echo.

REM Flask
echo Installing Flask (1/7)...
pip install flask==2.3.3 --no-cache-dir
if errorlevel 1 (
    echo Retrying Flask installation...
    pip install flask --no-cache-dir
)
echo.

REM Flask-CORS
echo Installing Flask-CORS (2/7)...
pip install flask-cors==4.0.0 --no-cache-dir
if errorlevel 1 (
    echo Retrying Flask-CORS installation...
    pip install flask-cors --no-cache-dir
)
echo.

REM yfinance
echo Installing yfinance (3/7)...
pip install yfinance==0.2.28 --no-cache-dir
if errorlevel 1 (
    echo Retrying yfinance installation...
    pip install yfinance --no-cache-dir
)
echo.

REM pandas
echo Installing pandas (4/7)...
pip install pandas==2.0.3 --no-cache-dir
if errorlevel 1 (
    echo Retrying pandas installation...
    pip install pandas --no-cache-dir
)
echo.

REM numpy
echo Installing numpy (5/7)...
pip install numpy==1.24.3 --no-cache-dir
if errorlevel 1 (
    echo Retrying numpy installation...
    pip install numpy --no-cache-dir
)
echo.

REM scikit-learn
echo Installing scikit-learn (6/7)...
pip install scikit-learn==1.3.0 --no-cache-dir
if errorlevel 1 (
    echo Retrying scikit-learn installation...
    pip install scikit-learn --no-cache-dir
)
echo.

REM requests
echo Installing requests (7/7)...
pip install requests==2.31.0 --no-cache-dir
if errorlevel 1 (
    echo Retrying requests installation...
    pip install requests --no-cache-dir
)
echo.

REM Optional: ta library
echo Installing optional technical analysis library...
pip install ta --no-cache-dir 2>nul
if errorlevel 1 (
    echo Note: Optional 'ta' library not installed (not critical)
)

echo.
echo ============================================================
echo     VERIFYING INSTALLATION...
echo ============================================================
echo.

REM Test imports
python -c "import flask; print('✓ Flask installed')" 2>nul
if errorlevel 1 echo ✗ Flask NOT installed

python -c "import flask_cors; print('✓ Flask-CORS installed')" 2>nul
if errorlevel 1 echo ✗ Flask-CORS NOT installed

python -c "import yfinance; print('✓ yfinance installed')" 2>nul
if errorlevel 1 echo ✗ yfinance NOT installed

python -c "import pandas; print('✓ pandas installed')" 2>nul
if errorlevel 1 echo ✗ pandas NOT installed

python -c "import numpy; print('✓ numpy installed')" 2>nul
if errorlevel 1 echo ✗ numpy NOT installed

python -c "import sklearn; print('✓ scikit-learn installed')" 2>nul
if errorlevel 1 echo ✗ scikit-learn NOT installed

python -c "import requests; print('✓ requests installed')" 2>nul
if errorlevel 1 echo ✗ requests NOT installed

echo.
echo ============================================================
echo     INSTALLATION COMPLETE!
echo ============================================================
echo.
echo To start the application, run: START_FIXED.bat
echo.
echo Press any key to close this window...
pause >nul