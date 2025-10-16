@echo off
echo ============================================================
echo Stock Tracker V9 - Starting Services (SSL FIXED)
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found
    echo Please run QUICK_START.bat or INSTALL_WINDOWS.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Set SSL fix for Windows
echo Applying SSL certificate fix...
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=
set PYTHONWARNINGS=ignore:Unverified HTTPS request

REM Check dependencies
echo Checking dependencies...
python -c "import fastapi, pandas, yfinance, sklearn" 2>nul
if %errorlevel% neq 0 (
    echo Installing missing packages...
    python -m pip install fastapi uvicorn pandas numpy yfinance scikit-learn joblib aiohttp python-multipart requests urllib3 certifi
)

REM Kill existing processes on our ports
echo.
echo Checking for existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8004') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8005') do taskkill /F /PID %%a 2>nul

timeout /t 2 /nobreak >nul

REM Start services with fixed version
echo.
echo Starting all services with SSL fix...
echo ============================================================
python start_services_fixed.py

pause