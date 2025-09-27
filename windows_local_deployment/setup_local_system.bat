@echo off
echo ================================================
echo GSMT Trading System - Windows Local Deployment
echo ================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/5] Installing backend dependencies...
pip install --upgrade pip
pip install fastapi uvicorn
pip install numpy pandas yfinance
pip install scikit-learn
pip install requests python-dotenv
pip install aiofiles python-multipart

echo [3/5] Installing minimal ML dependencies...
pip install --no-deps ta

echo [4/5] Setting up directory structure...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "models" mkdir models

echo [5/5] Creating startup script...
echo Backend installation complete!
echo.
echo To start the system, run: start_local_server.bat
echo.
pause