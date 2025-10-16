@echo off
echo ============================================================
echo Stock Tracker V9 - REAL DATA ONLY
echo NO MOCK DATA - NO SIMULATIONS - NO SYNTHETIC DATA
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Create/activate venv
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

REM SSL Fix
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=
set PYTHONWARNINGS=ignore

REM First, diagnose any issues
echo.
echo Running diagnostics...
echo ============================================================
python diagnose_crash.py
echo ============================================================
echo.

REM Ask user to continue
echo.
choice /C YN /M "Continue with startup?"
if %errorlevel%==2 goto end

REM Install required packages
echo.
echo Ensuring required packages are installed...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet fastapi uvicorn pandas numpy yfinance scikit-learn joblib aiohttp requests

REM Kill existing processes
echo.
echo Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    echo Stopping process on port 8003...
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

REM Start the REAL ML backend
echo.
echo ============================================================
echo Starting ML Backend with REAL DATA ONLY...
echo ============================================================
echo.
python ml_backend_real.py

:end
pause