@echo off
echo =========================================
echo     ASX Market Dashboard Starter
echo =========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if backend_fixed.py exists
if not exist "backend_fixed.py" (
    echo Error: backend_fixed.py not found
    echo Please run this script from the working_directory folder
    pause
    exit /b 1
)

REM Install requirements if needed
echo Checking Python dependencies...
python -m pip install -r requirements.txt -q 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
)

echo.
echo Starting backend server on port 8002...
echo ----------------------------------------
echo Once server is running:
echo 1. Open index.html in your web browser
echo 2. Or navigate to http://localhost:8002
echo ----------------------------------------
echo.

python backend_fixed.py