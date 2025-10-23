@echo off
cls
echo ============================================================
echo    STOCK ANALYSIS ML SYSTEM - WINDOWS 11
echo    Complete Edition with Machine Learning
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
python --version
echo.

REM Check/Create virtual environment
if not exist "venv\" (
    echo [INFO] First run detected - Installing system...
    echo.
    
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    
    echo Activating environment...
    call venv\Scripts\activate.bat
    
    echo Upgrading pip...
    python -m pip install --upgrade pip --quiet
    
    echo Installing packages (this may take 2-3 minutes)...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Package installation failed
        echo Try running as Administrator or check internet connection
        pause
        exit /b 1
    )
    
    echo.
    echo ============================================================
    echo    INSTALLATION SUCCESSFUL!
    echo ============================================================
    echo.
) else (
    echo [INFO] Virtual environment found
    call venv\Scripts\activate.bat
)

echo.
echo ============================================================
echo Starting Stock Analysis ML System...
echo ============================================================
echo.
echo Features:
echo - Machine Learning price predictions
echo - Yahoo Finance + Alpha Vantage data
echo - All timeframes: 1 day to 5 years
echo - Technical indicators: RSI, MACD, Bollinger Bands
echo - Candlestick, Line, and Area charts
echo.
echo Opening browser at http://localhost:8000
echo.
start http://localhost:8000

set FLASK_SKIP_DOTENV=1
python app.py

pause