@echo off
title Stock Analysis Sentiment - Windows Installer
echo ========================================================
echo    STOCK ANALYSIS WITH SENTIMENT - WINDOWS INSTALLER
echo ========================================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    pause
    exit /b 1
)

echo [*] Python detected
echo.

REM Upgrade pip and essential build tools
echo [*] Upgrading pip and installing build tools...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

REM Create virtual environment (optional but recommended)
echo [*] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [+] Virtual environment created
) else (
    echo [!] Virtual environment already exists
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Try installing pre-compiled wheels first (fast method)
echo.
echo ========================================================
echo    ATTEMPTING FAST INSTALLATION (Pre-compiled wheels)
echo ========================================================
echo.

REM Install critical packages one by one with pre-compiled wheels
echo [1/6] Installing Flask...
pip install flask==2.3.3 --only-binary :all: --prefer-binary 2>nul || pip install flask==2.3.3

echo [2/6] Installing Flask-CORS...
pip install flask-cors==4.0.0 --only-binary :all: --prefer-binary 2>nul || pip install flask-cors==4.0.0

echo [3/6] Installing yfinance...
pip install yfinance==0.2.28 --only-binary :all: --prefer-binary 2>nul || pip install yfinance==0.2.28

echo [4/6] Installing pandas (this may take a moment)...
REM Try pre-compiled first, then fall back
pip install pandas --only-binary :all: --prefer-binary 2>nul
if errorlevel 1 (
    echo    [!] Pre-compiled pandas not found, trying alternate versions...
    pip install pandas>=1.5.0 --prefer-binary 2>nul || pip install pandas
)

echo [5/6] Installing numpy...
pip install numpy --only-binary :all: --prefer-binary 2>nul
if errorlevel 1 (
    echo    [!] Pre-compiled numpy not found, trying alternate versions...
    pip install numpy>=1.20.0 --prefer-binary 2>nul || pip install numpy
)

echo [6/6] Installing scikit-learn...
pip install scikit-learn --only-binary :all: --prefer-binary 2>nul
if errorlevel 1 (
    echo    [!] Pre-compiled scikit-learn not found, trying alternate versions...
    pip install scikit-learn>=1.0.0 --prefer-binary 2>nul || pip install scikit-learn
)

echo.
echo [*] Installing remaining dependencies...
pip install requests python-dateutil werkzeug --prefer-binary >nul 2>&1

echo.
echo ========================================================
echo    VERIFYING INSTALLATION
echo ========================================================
echo.

REM Verify critical imports
python -c "import flask; print('[+] Flask OK')" 2>nul || echo [!] Flask FAILED
python -c "import yfinance; print('[+] yfinance OK')" 2>nul || echo [!] yfinance FAILED
python -c "import pandas; print('[+] pandas OK')" 2>nul || echo [!] pandas FAILED
python -c "import numpy; print('[+] numpy OK')" 2>nul || echo [!] numpy FAILED
python -c "import sklearn; print('[+] scikit-learn OK')" 2>nul || echo [!] scikit-learn FAILED

echo.
echo ========================================================
echo    TESTING SENTIMENT ANALYZER
echo ========================================================
echo.

REM Test the sentiment analyzer
python test_sentiment.py 2>nul
if errorlevel 1 (
    echo [!] Sentiment analyzer test failed
    echo     Some features may not work correctly
) else (
    echo [+] Sentiment analyzer test passed!
)

echo.
echo ========================================================
echo    INSTALLATION COMPLETE
echo ========================================================
echo.
echo To run the application:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run: python app_enhanced_sentiment_fixed.py
echo.
echo Or simply double-click: RUN_SENTIMENT_FINAL.bat
echo.
pause