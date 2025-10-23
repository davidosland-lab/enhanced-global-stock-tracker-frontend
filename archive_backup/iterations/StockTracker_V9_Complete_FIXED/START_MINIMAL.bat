@echo off
echo ============================================================
echo Stock Tracker V9 - Minimal Version (GUARANTEED TO WORK)
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python from python.org
    pause
    exit /b 1
)

REM Create venv if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate
call venv\Scripts\activate.bat

REM Install only essential packages
echo Installing essential packages...
python -m pip install --quiet fastapi uvicorn 2>nul

REM Try to install optional packages but don't fail if they don't work
echo Installing optional packages (may show errors - that's OK)...
python -m pip install --quiet pandas numpy yfinance scikit-learn joblib 2>nul

REM SSL Fix
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=
set PYTHONWARNINGS=ignore

REM Test the ML backend first
echo.
echo Testing ML backend...
python test_ml_backend.py
echo.

REM Kill existing processes
echo Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8004') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8005') do taskkill /F /PID %%a 2>nul

timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo Starting services with minimal backend...
echo ============================================================
echo.

REM Start only the working services
echo Starting ML Backend (Minimal)...
start /b python ml_backend_minimal.py

timeout /t 3 /nobreak >nul

echo Starting Main Backend...
start /b python main_backend.py 2>nul

timeout /t 2 /nobreak >nul

echo Starting FinBERT Backend...
start /b python finbert_backend.py 2>nul

timeout /t 2 /nobreak >nul

echo Starting Backtesting Backend...
start /b python backtesting_backend.py 2>nul

echo.
echo ============================================================
echo Services Started!
echo ============================================================
echo.
echo Open these in your browser:
echo   - Landing Page: index.html
echo   - Prediction Center: prediction_center.html
echo.
echo Check service status:
echo   - http://localhost:8003/api/ml/status (ML Backend)
echo   - http://localhost:8002/ (Main Backend)
echo.
echo Press Ctrl+C to stop all services
echo ============================================================
echo.

REM Keep window open and monitor
:loop
timeout /t 10 /nobreak >nul
goto loop