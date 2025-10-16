@echo off
echo ========================================
echo StockTracker V10 - Starting Services
echo Real Data Only from Yahoo Finance
echo ========================================
echo.

REM Fix SSL certificate issues on Windows
set SSL_CERT_FILE=
set SSL_CERT_DIR=
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=

REM Activate virtual environment
call venv\Scripts\activate.bat 2>nul
if %errorlevel% neq 0 (
    echo Virtual environment not found. Running INSTALL.bat first...
    call INSTALL.bat
    call venv\Scripts\activate.bat
)

REM Kill any existing processes
echo Cleaning up any existing processes...
taskkill /F /IM python.exe 2>nul

echo Starting services...
echo.

REM Start Main Backend (Port 8000)
echo [1/5] Starting Main Backend on port 8000...
start /min cmd /c "python main_backend.py"
timeout /t 2 >nul

REM Start ML Backend (Port 8002) - Fixed version with real data
echo [2/5] Starting ML Backend on port 8002...
start /min cmd /c "python ml_backend.py"
timeout /t 2 >nul

REM Start FinBERT Backend (Port 8003)
echo [3/5] Starting FinBERT Backend on port 8003...
start /min cmd /c "python finbert_backend.py"
timeout /t 2 >nul

REM Start Historical Backend with SQLite (Port 8004)
echo [4/5] Starting Historical Backend on port 8004...
start /min cmd /c "python historical_backend.py"
timeout /t 2 >nul

REM Start Backtesting Backend (Port 8005)
echo [5/5] Starting Backtesting Backend on port 8005...
start /min cmd /c "python backtesting_backend.py"
timeout /t 3 >nul

echo.
echo ========================================
echo All Services Started Successfully!
echo ========================================
echo.
echo Service URLs:
echo - Main Dashboard: http://localhost:8000
echo - ML Training: http://localhost:8002
echo - FinBERT Analysis: http://localhost:8003
echo - Historical Data (50x faster): http://localhost:8004
echo - Backtesting: http://localhost:8005
echo.
echo Opening main dashboard in browser...
start http://localhost:8000
echo.
echo Press Ctrl+C to stop all services
pause >nul