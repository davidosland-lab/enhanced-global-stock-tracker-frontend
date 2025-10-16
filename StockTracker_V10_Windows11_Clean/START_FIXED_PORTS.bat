@echo off
echo ========================================
echo StockTracker V10 - Starting with FIXED Ports
echo ========================================
echo.

REM First, kill everything
echo Step 1: Killing all existing processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul

REM Free all ports
echo Step 2: Freeing all ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8002"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8003"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8004"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8005"') do taskkill /PID %%a /F 2>nul

timeout /t 3 >nul

REM Clear SSL
set SSL_CERT_FILE=
set SSL_CERT_DIR=
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=

REM Activate venv
echo Step 3: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 4: Starting services with CORRECT ports...
echo.

REM Start Main Backend on 8000
echo Starting Main Backend on port 8000...
start "Main Backend - 8000" cmd /c "python main_backend.py"
timeout /t 3 >nul

REM Start ML Backend on 8002
echo Starting ML Backend on port 8002...
start "ML Backend - 8002" cmd /c "python ml_backend.py"
timeout /t 3 >nul

REM Start FinBERT on 8003 (FIXED!)
echo Starting FinBERT on port 8003...
start "FinBERT - 8003" cmd /c "python finbert_backend.py"
timeout /t 3 >nul

REM Start Historical on 8004
echo Starting Historical Backend on port 8004...
start "Historical - 8004" cmd /c "python historical_backend.py"
timeout /t 3 >nul

REM Start Backtesting on 8005
echo Starting Backtesting on port 8005...
start "Backtesting - 8005" cmd /c "python backtesting_backend.py"
timeout /t 5 >nul

echo.
echo ========================================
echo Services Started with CORRECT Ports:
echo ========================================
echo Main Backend:     http://localhost:8000
echo ML Backend:       http://localhost:8002
echo FinBERT:         http://localhost:8003
echo Historical:      http://localhost:8004
echo Backtesting:     http://localhost:8005
echo ========================================
echo.
echo Waiting for services to fully initialize...
timeout /t 5 >nul

echo Opening dashboard...
start http://localhost:8000

echo.
echo If you see port errors, run KILL_ALL_PORTS.bat first!
echo.
pause