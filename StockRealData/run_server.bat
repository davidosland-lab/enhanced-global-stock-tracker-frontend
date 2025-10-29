@echo off
cls
echo ============================================================
echo    STOCK ANALYSIS SYSTEM - STARTING SERVER
echo ============================================================
echo.

REM Ensure we're in the correct directory
cd /d "%~dp0"
echo Working directory: %CD%
echo.

REM Check if venv exists
if exist "venv\Scripts\python.exe" (
    echo [OK] Virtual environment found
    set PYTHON_EXE=venv\Scripts\python.exe
    set PIP_EXE=venv\Scripts\pip.exe
) else (
    echo [INFO] No virtual environment, using system Python
    set PYTHON_EXE=python
    set PIP_EXE=python -m pip
)

REM Display Python version being used
echo Using Python:
%PYTHON_EXE% --version
echo.

REM Check if required packages are installed in the environment
echo Checking installed packages...
%PYTHON_EXE% -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Flask not found in environment
    echo Installing Flask...
    %PIP_EXE% install flask==3.0.0
)

%PYTHON_EXE% -c "import yfinance" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] yfinance not found in environment
    echo Installing yfinance...
    %PIP_EXE% install yfinance==0.2.33
)

%PYTHON_EXE% -c "import sklearn" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] scikit-learn not found in environment
    echo Installing scikit-learn...
    %PIP_EXE% install scikit-learn==1.3.2
)

echo.
echo ============================================================
echo Starting server at http://localhost:8000
echo ============================================================
echo.

REM Set environment variables
set FLASK_SKIP_DOTENV=1
set PYTHONUNBUFFERED=1

REM Open browser after a short delay
timeout /t 3 /nobreak >nul
start "" "http://localhost:8000"

REM Run the server with the correct Python
echo Running server...
echo Press Ctrl+C to stop
echo.
%PYTHON_EXE% app.py

echo.
echo Server stopped.
pause