@echo off
echo ========================================
echo Fixing Port Configuration
echo ========================================
echo.

REM Kill all Python processes first
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

REM Fix SSL certificate issues
set SSL_CERT_FILE=
set SSL_CERT_DIR=
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Starting services on correct ports...
echo.

REM Start Main Backend (Port 8000)
echo [1/5] Starting Main Backend on port 8000...
start /min cmd /c "cd /d %CD% && venv\Scripts\activate.bat && python main_backend.py"
timeout /t 3 >nul

REM Start ML Backend (Port 8002) - FIXED PORT
echo [2/5] Starting ML Backend on port 8002...
start /min cmd /c "cd /d %CD% && venv\Scripts\activate.bat && python -c \"import sys; sys.argv=['', '--port', '8002']; exec(open('ml_backend.py').read())\""
timeout /t 3 >nul

REM Start FinBERT Backend (Port 8003)
echo [3/5] Starting FinBERT Backend on port 8003...
start /min cmd /c "cd /d %CD% && venv\Scripts\activate.bat && python finbert_backend.py"
timeout /t 3 >nul

REM Start Historical Backend (Port 8004)
echo [4/5] Starting Historical Backend on port 8004...
start /min cmd /c "cd /d %CD% && venv\Scripts\activate.bat && python historical_backend.py"
timeout /t 3 >nul

REM Start Backtesting Backend (Port 8005)
echo [5/5] Starting Backtesting Backend on port 8005...
start /min cmd /c "cd /d %CD% && venv\Scripts\activate.bat && python backtesting_backend.py"
timeout /t 3 >nul

echo.
echo ========================================
echo Services Started with Correct Ports!
echo ========================================
echo.
echo Verifying services...
timeout /t 5 >nul

python diagnose.py

echo.
echo Service URLs:
echo - Main Dashboard: http://localhost:8000
echo - ML API: http://localhost:8002
echo - FinBERT API: http://localhost:8003  
echo - Historical API: http://localhost:8004
echo - Backtesting API: http://localhost:8005
echo.
echo Opening dashboard...
start http://localhost:8000

pause