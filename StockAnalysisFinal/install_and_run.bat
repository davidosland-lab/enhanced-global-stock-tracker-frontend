@echo off
cls
echo ===============================================
echo   STOCK ANALYSIS SYSTEM - WINDOWS 11
echo ===============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install from: https://www.python.org
    echo.
    pause
    exit /b 1
)

echo Python detected successfully!
echo.

REM Check if first run
if not exist "venv\" (
    echo First run detected. Installing...
    echo.
    
    echo Creating virtual environment...
    python -m venv venv
    
    echo Activating environment...
    call venv\Scripts\activate.bat
    
    echo Installing packages...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    echo.
    echo Installation complete!
    echo.
) else (
    echo Activating environment...
    call venv\Scripts\activate.bat
)

echo.
echo ===============================================
echo Starting server at http://localhost:8000
echo ===============================================
echo.
echo Opening browser...
start http://localhost:8000

echo.
set FLASK_SKIP_DOTENV=1
python app.py

pause