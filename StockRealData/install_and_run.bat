@echo off
setlocal enabledelayedexpansion
cls
echo ============================================================
echo    STOCK ANALYSIS SYSTEM - REAL DATA ONLY
echo    No synthetic/test data - Only real market data
echo ============================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org
    echo During installation, make sure to:
    echo   1. Check "Add Python to PATH"
    echo   2. Choose "Install for all users" if prompted
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
python --version
echo.

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found!
    echo Please ensure all files are extracted properly.
    echo.
    pause
    exit /b 1
)

REM Check if app.py exists
if not exist "app.py" (
    echo [ERROR] app.py not found!
    echo Please ensure all files are extracted properly.
    echo.
    pause
    exit /b 1
)

REM Check/Create virtual environment
if not exist "venv\" (
    echo [INFO] First run - Installing system...
    echo This will take 2-3 minutes...
    echo.
    
    echo Step 1: Creating virtual environment...
    python -m venv venv 2>&1
    if !errorlevel! neq 0 (
        echo.
        echo [ERROR] Failed to create virtual environment
        echo.
        echo Possible fixes:
        echo   1. Run as Administrator
        echo   2. Ensure you have write permissions in this folder
        echo   3. Try: python -m pip install --user virtualenv
        echo.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
    
    echo.
    echo Step 2: Activating environment...
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo [OK] Environment activated
    ) else (
        echo [ERROR] Cannot find venv\Scripts\activate.bat
        pause
        exit /b 1
    )
    
    echo.
    echo Step 3: Upgrading pip...
    python -m pip install --upgrade pip 2>&1 | find /v "Requirement already satisfied"
    
    echo.
    echo Step 4: Installing packages...
    echo This may take 2-3 minutes...
    pip install -r requirements.txt --no-warn-script-location 2>&1 | find /v "Requirement already satisfied"
    if !errorlevel! neq 0 (
        echo.
        echo [WARNING] Some packages may have failed to install
        echo Attempting to continue...
    )
    
    echo.
    echo ============================================================
    echo    INSTALLATION COMPLETE!
    echo ============================================================
    echo.
    timeout /t 2 /nobreak >nul
) else (
    echo [INFO] Virtual environment found
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo [OK] Environment activated
    ) else (
        echo [ERROR] Cannot activate virtual environment
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo Starting Stock Analysis System...
echo ============================================================
echo.
echo IMPORTANT: This version uses ONLY real market data
echo - NO test data
echo - NO synthetic data  
echo - NO random generation
echo.
echo Features:
echo - Yahoo Finance primary source
echo - Alpha Vantage fallback
echo - Machine Learning predictions
echo - All timeframes working
echo - Real-time accurate prices
echo.
echo Server will start at: http://localhost:8000
echo.

REM Set environment variable
set FLASK_SKIP_DOTENV=1

REM Wait a moment before opening browser
timeout /t 2 /nobreak >nul

REM Open browser
echo Opening browser...
start "" "http://localhost:8000"

echo.
echo Starting server...
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python app.py

echo.
echo Server stopped.
echo.
pause