@echo off
echo ============================================================
echo Stock Tracker V9 - Quick Start (Simplified Installation)
echo ============================================================
echo.
echo This will install minimal requirements and start services.
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Remove old venv if exists
if exist "venv" rmdir /s /q venv

REM Create fresh venv
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install minimal requirements without version constraints
echo Installing packages (this may take 2-3 minutes)...
python -m pip install fastapi
python -m pip install uvicorn
python -m pip install pandas
python -m pip install numpy
python -m pip install yfinance
python -m pip install scikit-learn
python -m pip install joblib
python -m pip install aiohttp
python -m pip install python-multipart

REM Try to install optional packages
echo Installing optional packages...
python -m pip install ta
python -m pip install xgboost

echo.
echo ============================================================
echo Installation complete! Starting services...
echo ============================================================
echo.

REM Start the services
python start_services.py

pause