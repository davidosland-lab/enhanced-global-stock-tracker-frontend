@echo off
echo ================================================================
echo    FINBERT ULTIMATE TRADING SYSTEM
echo ================================================================
echo.

REM Check if venv exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run INSTALL_ULTIMATE.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check numpy version
echo Checking NumPy compatibility...
python -c "import numpy; v=tuple(map(int,numpy.__version__.split('.')[:2])); exit(0 if v>=(1,26) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo WARNING: NumPy version issue detected!
    echo Upgrading NumPy for Python 3.12 compatibility...
    pip install --upgrade "numpy>=1.26.0,<2.0.0"
)

REM Clear any existing .env files that might cause issues
if exist .env (
    echo Removing problematic .env file...
    del .env
)

echo.
echo Starting server...
echo Navigate to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo ================================================================
echo.

REM Set environment variable to skip dotenv
set FLASK_SKIP_DOTENV=1

REM Run the application
python app_finbert_ultimate.py

echo.
echo Server stopped.
pause