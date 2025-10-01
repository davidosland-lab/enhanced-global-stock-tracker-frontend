@echo off
REM Self-contained launcher that verifies files exist
REM This MUST be run from the extracted folder

echo =========================================
echo Stock Predictor Pro - File Check & Run
echo =========================================
echo.

REM Show current directory
echo Current location: %CD%
echo.

REM Check if we're in the right place
echo Checking for required files...
echo.

if exist "stock_predictor_lite.py" (
    echo [OK] Found stock_predictor_lite.py
) else (
    echo [ERROR] stock_predictor_lite.py NOT FOUND!
    echo.
    echo YOU MUST EXTRACT ALL FILES FROM THE ZIP FIRST!
    echo.
    echo Instructions:
    echo 1. Go back to the ZIP file
    echo 2. Right-click and select "Extract All..."
    echo 3. Extract to a folder like C:\StockPredictor or Desktop
    echo 4. Open the extracted folder
    echo 5. Run this file again from the extracted folder
    echo.
    pause
    exit /b 1
)

echo.
echo All files found. Now checking Python...
echo.

REM Try to find Python - check multiple locations
set PYTHON_FOUND=NO
set PYTHON_CMD=

REM Check if python works
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_FOUND=YES
    set PYTHON_CMD=python
    echo [OK] Found Python using 'python' command
    python --version
    goto :RunApp
)

REM Check Windows Store Python location for user 'david'
set STORE_PYTHON=C:\Users\david\AppData\Local\Microsoft\WindowsApps\python.exe
if exist "%STORE_PYTHON%" (
    "%STORE_PYTHON%" --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_FOUND=YES
        set PYTHON_CMD="%STORE_PYTHON%"
        echo [OK] Found Windows Store Python
        "%STORE_PYTHON%" --version
        goto :RunApp
    )
)

REM Check common Python 3.9 locations
if exist "C:\Python39\python.exe" (
    set PYTHON_FOUND=YES
    set PYTHON_CMD="C:\Python39\python.exe"
    echo [OK] Found Python 3.9 at C:\Python39
    "C:\Python39\python.exe" --version
    goto :RunApp
)

REM Check user Python installations
if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
    set PYTHON_FOUND=YES
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    echo [OK] Found Python 3.9 in user directory
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" --version
    goto :RunApp
)

REM If Python not found
if "%PYTHON_FOUND%"=="NO" (
    echo.
    echo [ERROR] Python is not installed or not accessible!
    echo.
    echo Please install Python 3.9 from:
    echo https://www.python.org/downloads/release/python-3913/
    echo.
    echo During installation, make sure to:
    echo [X] Add Python to PATH
    echo.
    pause
    exit /b 1
)

:RunApp
echo.
echo =========================================
echo Starting Stock Predictor Pro...
echo =========================================
echo.

REM Run the lite version with the found Python
%PYTHON_CMD% stock_predictor_lite.py

if %errorlevel% neq 0 (
    echo.
    echo =========================================
    echo Application ended with an error.
    echo =========================================
    echo.
    echo Possible issues:
    echo 1. Missing tkinter (usually included with Python)
    echo 2. Python installation is incomplete
    echo.
)

pause