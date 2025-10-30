@echo off
setlocal enabledelayedexpansion
cls
echo ============================================================
echo    STOCK ANALYSIS SYSTEM - SETUP AND RUN
echo ============================================================
echo.

REM Get the directory where this batch file is located
cd /d "%~dp0"
echo Working Directory: %CD%
echo.

REM Check Python installation
echo Detecting Python installation...
where python >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python not found!
    echo Please install from https://www.python.org
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment exists
    echo.
    choice /C YN /M "Do you want to use existing virtual environment"
    if !errorlevel! equ 2 (
        echo Removing old virtual environment...
        rmdir /s /q venv 2>nul
        goto :CREATE_VENV
    ) else (
        goto :ACTIVATE_VENV
    )
) else (
    goto :CREATE_VENV
)

:CREATE_VENV
echo.
echo Creating virtual environment...
python -m venv venv
if !errorlevel! neq 0 (
    echo [ERROR] Failed to create virtual environment
    echo.
    echo Trying alternative method...
    python -m pip install --user virtualenv
    python -m virtualenv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Still failed. Please check Python installation.
        pause
        exit /b 1
    )
)
echo [OK] Virtual environment created

:ACTIVATE_VENV
echo.
echo Activating virtual environment...

REM Use full path to python.exe in venv
set VENV_PYTHON=%CD%\venv\Scripts\python.exe
set VENV_PIP=%CD%\venv\Scripts\pip.exe

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment Python not found!
    echo Path checked: %VENV_PYTHON%
    pause
    exit /b 1
)

echo Using Python: %VENV_PYTHON%
echo.

REM Upgrade pip first
echo Upgrading pip...
"%VENV_PYTHON%" -m pip install --upgrade pip --quiet

REM Install packages
echo.
echo Installing required packages...
echo This may take 2-3 minutes on first run...
echo.

REM Install each package with error checking
set PACKAGES=flask==3.0.0 flask-cors==4.0.0 yfinance==0.2.33 pandas==2.1.4 numpy==1.26.2 plotly==5.18.0 requests==2.31.0 scikit-learn==1.3.2

for %%p in (%PACKAGES%) do (
    echo Installing %%p...
    "%VENV_PIP%" install %%p --quiet --no-warn-script-location
    if !errorlevel! neq 0 (
        echo [WARNING] Failed to install %%p
    )
)

echo.
echo ============================================================
echo    SETUP COMPLETE - STARTING SERVER
echo ============================================================
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set FLASK_APP=app.py
set PYTHONUNBUFFERED=1

REM Show server info
echo Server Information:
echo -------------------
echo URL: http://localhost:8000
echo Python: %VENV_PYTHON%
echo.
echo Features:
echo - Real market data only (no synthetic data)
echo - Yahoo Finance + Alpha Vantage
echo - Machine Learning predictions
echo - Technical indicators
echo.

REM Wait before opening browser
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start "" "http://localhost:8000"

echo.
echo Starting server...
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

REM Run the application using venv Python
"%VENV_PYTHON%" app.py

echo.
echo Server stopped.
echo.
pause