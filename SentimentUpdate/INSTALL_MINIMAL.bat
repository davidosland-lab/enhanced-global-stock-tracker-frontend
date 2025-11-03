@echo off
title Stock Analysis - Minimal Installation (No sklearn)
echo ========================================================
echo    MINIMAL INSTALLATION - NO SKLEARN REQUIRED
echo ========================================================
echo.
echo This installer will set up the application WITHOUT scikit-learn.
echo All sentiment features will still work!
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

REM Upgrade pip
echo [*] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

echo.
echo [*] Installing required packages...
echo.

REM Install packages one by one with feedback
echo [1/5] Installing Flask...
pip install flask --prefer-binary >nul 2>&1
if errorlevel 1 (
    echo    [!] Failed - trying alternate method...
    python -m pip install flask
)

echo [2/5] Installing Flask-CORS...
pip install flask-cors --prefer-binary >nul 2>&1

echo [3/5] Installing yfinance...
pip install yfinance --prefer-binary >nul 2>&1

echo [4/5] Installing pandas (this may take a moment)...
pip install pandas --only-binary :all: --prefer-binary >nul 2>&1
if errorlevel 1 (
    echo    [!] Pre-compiled not found, installing from source...
    pip install pandas
)

echo [5/5] Installing numpy...
pip install numpy --only-binary :all: --prefer-binary >nul 2>&1
if errorlevel 1 (
    echo    [!] Pre-compiled not found, installing from source...
    pip install numpy
)

echo.
echo [*] Installing additional dependencies...
pip install requests python-dateutil >nul 2>&1

echo.
echo ========================================================
echo    VERIFYING INSTALLATION
echo ========================================================
echo.

REM Test imports
python -c "import flask; print('[+] Flask: OK')" 2>nul || echo [!] Flask: FAILED
python -c "import yfinance; print('[+] yfinance: OK')" 2>nul || echo [!] yfinance: FAILED
python -c "import pandas; print('[+] pandas: OK')" 2>nul || echo [!] pandas: FAILED
python -c "import numpy; print('[+] numpy: OK')" 2>nul || echo [!] numpy: FAILED
python -c "import flask_cors; print('[+] Flask-CORS: OK')" 2>nul || echo [!] Flask-CORS: FAILED

echo.
echo ========================================================
echo    TESTING APPLICATION
echo ========================================================
echo.

REM Quick test of the app
python -c "from app_sentiment_no_sklearn import MarketSentimentAnalyzer; a=MarketSentimentAnalyzer(); print('[+] Sentiment Analyzer: OK')" 2>nul
if errorlevel 1 (
    echo [!] Application test failed
    echo.
    echo Please check error messages above.
) else (
    echo [+] All tests passed!
    echo.
    echo ========================================================
    echo    INSTALLATION COMPLETE!
    echo ========================================================
    echo.
    echo To run the application:
    echo    Double-click: RUN_NO_SKLEARN.bat
    echo    Or run: python app_sentiment_no_sklearn.py
    echo.
    echo The app will be available at http://localhost:5000
)

echo.
pause