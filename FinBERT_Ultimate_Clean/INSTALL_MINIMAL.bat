@echo off
echo ================================================================
echo    FINBERT TRADING SYSTEM - MINIMAL INSTALLER
echo ================================================================
echo.
echo This installer skips FinBERT/Transformers for faster setup.
echo The system will use fallback sentiment analysis.
echo.

REM Check Python
echo Checking Python installation...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

python -m venv venv
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo ================================================================
echo Installing required packages...
echo ================================================================
echo.

REM Core packages only - no transformers
pip install "numpy>=1.26.0,<2.0.0"
pip install pandas
pip install yfinance
pip install requests
pip install flask
pip install flask-cors
pip install scikit-learn
pip install ta
pip install feedparser

echo.
echo Creating directories...
mkdir cache 2>nul
mkdir models 2>nul
mkdir logs 2>nul
mkdir data 2>nul

echo.
echo ================================================================
echo INSTALLATION COMPLETE!
echo ================================================================
echo.
echo System installed WITHOUT FinBERT (using fallback sentiment)
echo.
echo To run: RUN_ULTIMATE.bat
echo.
pause