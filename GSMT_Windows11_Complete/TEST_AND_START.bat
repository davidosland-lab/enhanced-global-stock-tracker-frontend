@echo off
:: Quick Test and Start Script for GSMT Stock Tracker
:: Tests installation and starts the server

color 0A
cls

echo ============================================================
echo  GSMT STOCK TRACKER - TEST AND START
echo ============================================================
echo.

:: Set directory
set "INSTALL_DIR=%cd%"
echo Working Directory: %INSTALL_DIR%
echo.

:: Check if venv exists
if not exist "%INSTALL_DIR%\venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run FIX_INSTALLATION.bat first
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call "%INSTALL_DIR%\venv\Scripts\activate.bat"

:: Quick test of imports
echo.
echo Testing Python packages...
echo ========================================

"%INSTALL_DIR%\venv\Scripts\python.exe" -c "import sys; print(f'Python: {sys.version}')"
echo.

"%INSTALL_DIR%\venv\Scripts\python.exe" -c "import fastapi; print('✓ FastAPI installed')" 2>nul || echo ✗ FastAPI MISSING
"%INSTALL_DIR%\venv\Scripts\python.exe" -c "import uvicorn; print('✓ Uvicorn installed')" 2>nul || echo ✗ Uvicorn MISSING
"%INSTALL_DIR%\venv\Scripts\python.exe" -c "import yfinance; print('✓ YFinance installed')" 2>nul || echo ✗ YFinance MISSING
"%INSTALL_DIR%\venv\Scripts\python.exe" -c "import pandas; print('✓ Pandas installed')" 2>nul || echo ✗ Pandas MISSING
"%INSTALL_DIR%\venv\Scripts\python.exe" -c "import numpy; print('✓ NumPy installed')" 2>nul || echo ✗ NumPy MISSING
"%INSTALL_DIR%\venv\Scripts\python.exe" -c "import sklearn; print('✓ Scikit-learn installed')" 2>nul || echo ✗ Scikit-learn MISSING

echo.
echo ========================================
echo.

:: Ask which backend to use
echo Which backend would you like to start?
echo.
echo 1. Enhanced ML Backend (Full features)
echo 2. Simple Backend (Guaranteed to work)
echo 3. Exit
echo.
set /p BACKEND_CHOICE=Enter your choice (1-3): 

if "%BACKEND_CHOICE%"=="3" exit /b 0

echo.
echo Starting selected backend...
echo ========================================
echo.

if "%BACKEND_CHOICE%"=="1" (
    echo Starting Enhanced ML Backend...
    echo.
    echo Server will run at: http://localhost:8000
    echo Press Ctrl+C to stop the server
    echo.
    "%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\backend\enhanced_ml_backend.py"
    if %errorlevel% neq 0 (
        echo.
        echo Enhanced backend failed to start!
        echo Trying simple backend instead...
        echo.
        "%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\backend\simple_ml_backend.py"
    )
) else if "%BACKEND_CHOICE%"=="2" (
    echo Starting Simple Backend...
    echo.
    echo Server will run at: http://localhost:8000
    echo Press Ctrl+C to stop the server
    echo.
    "%INSTALL_DIR%\venv\Scripts\python.exe" "%INSTALL_DIR%\backend\simple_ml_backend.py"
)

pause