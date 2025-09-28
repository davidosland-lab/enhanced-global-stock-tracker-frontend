@echo off
:: Troubleshooting Script for GSMT Stock Tracker

color 0E
cls

echo ============================================================
echo  GSMT Stock Tracker - Troubleshooting Tool
echo ============================================================
echo.

echo Checking system configuration...
echo.

:: Check Python
echo [1] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    [ERROR] Python is not installed or not in PATH
    echo    Solution: Install Python from https://python.org
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo    [OK] Python !PYTHON_VERSION! found
)

:: Check virtual environment
echo.
echo [2] Checking virtual environment...
if exist venv (
    echo    [OK] Virtual environment exists
    if exist venv\Scripts\python.exe (
        echo    [OK] Python executable found in venv
    ) else (
        echo    [ERROR] Virtual environment is corrupted
        echo    Solution: Delete venv folder and run INSTALL.bat again
    )
) else (
    echo    [ERROR] Virtual environment not found
    echo    Solution: Run INSTALL.bat first
)

:: Check required packages
echo.
echo [3] Checking installed packages...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python -c "import fastapi" 2>nul
    if %errorlevel% neq 0 (
        echo    [ERROR] FastAPI not installed
    ) else (
        echo    [OK] FastAPI installed
    )
    
    python -c "import uvicorn" 2>nul
    if %errorlevel% neq 0 (
        echo    [ERROR] Uvicorn not installed
    ) else (
        echo    [OK] Uvicorn installed
    )
    
    python -c "import yfinance" 2>nul
    if %errorlevel% neq 0 (
        echo    [ERROR] yfinance not installed
    ) else (
        echo    [OK] yfinance installed
    )
    
    python -c "import pandas" 2>nul
    if %errorlevel% neq 0 (
        echo    [ERROR] pandas not installed
    ) else (
        echo    [OK] pandas installed
    )
    
    python -c "import numpy" 2>nul
    if %errorlevel% neq 0 (
        echo    [ERROR] numpy not installed
    ) else (
        echo    [OK] numpy installed
    )
    
    python -c "import sklearn" 2>nul
    if %errorlevel% neq 0 (
        echo    [ERROR] scikit-learn not installed
    ) else (
        echo    [OK] scikit-learn installed
    )
)

:: Check port availability
echo.
echo [4] Checking port 8000...
netstat -an | findstr :8000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo    [WARNING] Port 8000 is already in use
    echo    Solution: Run STOP_SERVER.bat or close the application using port 8000
) else (
    echo    [OK] Port 8000 is available
)

:: Check backend file
echo.
echo [5] Checking backend files...
if exist backend\enhanced_ml_backend.py (
    echo    [OK] Backend file found
) else (
    echo    [ERROR] Backend file missing
    echo    Solution: Re-extract the package or download again
)

:: Check frontend files
echo.
echo [6] Checking frontend files...
if exist frontend\dashboard.html (
    echo    [OK] Dashboard file found
) else (
    echo    [ERROR] Dashboard file missing
)

if exist frontend\tracker.html (
    echo    [OK] Tracker file found
) else (
    echo    [ERROR] Tracker file missing
)

:: Check internet connection
echo.
echo [7] Checking internet connection...
ping -n 1 google.com >nul 2>&1
if %errorlevel% neq 0 (
    echo    [WARNING] No internet connection
    echo    Note: Internet is required for real-time stock data
) else (
    echo    [OK] Internet connection available
)

:: Summary
echo.
echo ============================================================
echo  Troubleshooting Complete
echo ============================================================
echo.

:: Check if there were any errors
findstr /C:"[ERROR]" "%~f0" >nul
if %errorlevel% equ 0 (
    echo  Issues were found. Please address them and try again.
    echo.
    echo  Common fixes:
    echo  1. Run INSTALL.bat to set up the environment
    echo  2. Make sure Python is installed and in PATH
    echo  3. Check your internet connection
    echo  4. Run as administrator if permission issues
) else (
    echo  No critical issues found!
    echo  The application should work correctly.
    echo.
    echo  Try running RUN_QUICK_START.bat to start the application.
)

echo.
pause