@echo off
cls
echo ============================================================
echo    STOCK ANALYSIS - WORKING VERSION
echo ============================================================
echo.

REM Keep window open on error
if "%1"=="" (
    cmd /k "%~f0" nested
    exit /b
)

REM Change to script directory
cd /d "%~dp0"
echo Working Directory: %CD%
echo.

REM Check if app_WORKING.py exists
if not exist "app_WORKING.py" (
    echo [ERROR] app_WORKING.py not found!
    echo Please ensure all files are extracted.
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://www.python.org
    echo Make sure to check "Add Python to PATH"
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Display Python version
echo Python Version:
python --version
echo.

REM Check and install required packages
echo Checking required packages...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo Installing Flask...
    pip install flask
)

python -c "import yfinance" 2>nul
if %errorlevel% neq 0 (
    echo Installing yfinance...
    pip install yfinance
)

python -c "import plotly" 2>nul
if %errorlevel% neq 0 (
    echo Installing plotly...
    pip install plotly
)

python -c "import sklearn" 2>nul
if %errorlevel% neq 0 (
    echo Installing scikit-learn...
    pip install scikit-learn
)

python -c "import pandas" 2>nul
if %errorlevel% neq 0 (
    echo Installing pandas...
    pip install pandas
)

echo.
echo ============================================================
echo Starting server at http://localhost:8000
echo ============================================================
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set PYTHONUNBUFFERED=1

REM Open browser
start "" "http://localhost:8000"

REM Run the application and capture any errors
echo Running application...
echo.
python app_WORKING.py 2>&1

echo.
echo ============================================================
if %errorlevel% neq 0 (
    echo [ERROR] Application failed with error code %errorlevel%
) else (
    echo Application stopped normally
)
echo ============================================================
echo.
echo Press any key to close this window...
pause >nul