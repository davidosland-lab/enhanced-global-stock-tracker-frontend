@echo off
cls
echo ==============================================================
echo    STOCK ANALYSIS - REAL DATA ONLY
echo    No Synthetic Data - Only Real Market Information
echo ==============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not installed
    echo Download from: https://www.python.org
    echo Check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Setup virtual environment
if not exist "venv\" (
    echo Installing system (first run)...
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt
    echo Installation complete!
    echo.
) else (
    call venv\Scripts\activate.bat
)

echo ==============================================================
echo Starting Real Data Stock Analysis System...
echo ==============================================================
echo.
echo This system uses ONLY:
echo - Real market data from Yahoo Finance
echo - Real market data from Alpha Vantage
echo - ML predictions based on real historical patterns
echo - NO synthetic/test/simulated data
echo.
echo Opening browser: http://localhost:8000
echo.
start http://localhost:8000

set FLASK_SKIP_DOTENV=1
python app.py

pause