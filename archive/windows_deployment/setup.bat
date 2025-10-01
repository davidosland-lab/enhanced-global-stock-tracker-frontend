@echo off
echo ====================================================
echo    Enhanced Stock Tracker ML System Setup
echo    Windows 11 Standalone Installation
echo ====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/7] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
)

echo [2/7] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/7] Upgrading pip...
python -m pip install --upgrade pip

echo [4/7] Installing required packages...
pip install fastapi uvicorn yfinance numpy pandas scikit-learn

echo [5/7] Installing additional ML packages...
pip install xgboost lightgbm catboost

echo [6/7] Creating shortcuts...
echo @echo off > start_server.bat
echo title Enhanced Stock Tracker Server
echo call venv\Scripts\activate.bat
echo echo Starting Enhanced ML Backend Server...
echo python backend_server.py
echo pause >> start_server.bat

echo @echo off > open_dashboard.bat
echo start http://localhost:8000/dashboard
echo exit >> open_dashboard.bat

echo [7/7] Setup complete!
echo.
echo ====================================================
echo    Installation Successful!
echo ====================================================
echo.
echo To start the system:
echo 1. Run 'start_server.bat' to launch the backend
echo 2. Run 'open_dashboard.bat' to open the web interface
echo.
echo Or run 'run_all.bat' to start everything at once
echo.
pause