@echo off
echo ========================================
echo StockTracker V10 - Debug Startup
echo ========================================
echo.

REM Clean up any existing processes
echo Step 1: Killing existing Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul

REM Fix SSL
set SSL_CERT_FILE=
set SSL_CERT_DIR=
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=

REM Activate virtual environment
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Virtual environment not found!
    echo Please run INSTALL.bat first
    pause
    exit /b 1
)

echo.
echo Step 3: Starting services one by one with error checking...
echo.

REM Test Main Backend
echo [1/5] Testing Main Backend (Port 8000)...
echo Command: python main_backend.py
start /wait /min cmd /c "python main_backend.py 2>&1 | more"
timeout /t 5 >nul
netstat -an | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo Main Backend started successfully on port 8000
) else (
    echo WARNING: Main Backend may have failed to start
    echo Trying alternative startup...
    start cmd /k "python main_backend.py"
)
echo.

REM Test ML Backend
echo [2/5] Testing ML Backend (Port 8002)...
echo Command: python ml_backend.py
start /wait /min cmd /c "python ml_backend.py 2>&1 | more"
timeout /t 5 >nul
netstat -an | findstr :8002 >nul
if %errorlevel% equ 0 (
    echo ML Backend started successfully on port 8002
) else (
    echo WARNING: ML Backend may have failed to start
    echo Trying alternative startup...
    start cmd /k "python ml_backend.py"
)
echo.

REM Test FinBERT Backend
echo [3/5] Testing FinBERT Backend (Port 8003)...
echo Command: python finbert_backend.py
start /wait /min cmd /c "python finbert_backend.py 2>&1 | more"
timeout /t 5 >nul
netstat -an | findstr :8003 >nul
if %errorlevel% equ 0 (
    echo FinBERT Backend started successfully on port 8003
) else (
    echo WARNING: FinBERT Backend may have failed to start
    echo Trying alternative startup...
    start cmd /k "python finbert_backend.py"
)
echo.

REM Test Historical Backend
echo [4/5] Testing Historical Backend (Port 8004)...
echo Command: python historical_backend.py
start /wait /min cmd /c "python historical_backend.py 2>&1 | more"
timeout /t 5 >nul
netstat -an | findstr :8004 >nul
if %errorlevel% equ 0 (
    echo Historical Backend started successfully on port 8004
) else (
    echo WARNING: Historical Backend may have failed to start
    echo Trying alternative startup...
    start cmd /k "python historical_backend.py"
)
echo.

REM Test Backtesting Backend
echo [5/5] Testing Backtesting Backend (Port 8005)...
echo Command: python backtesting_backend.py
start /wait /min cmd /c "python backtesting_backend.py 2>&1 | more"
timeout /t 5 >nul
netstat -an | findstr :8005 >nul
if %errorlevel% equ 0 (
    echo Backtesting Backend started successfully on port 8005
) else (
    echo WARNING: Backtesting Backend may have failed to start
    echo Trying alternative startup...
    start cmd /k "python backtesting_backend.py"
)
echo.

echo ========================================
echo Checking Service Status...
echo ========================================
timeout /t 3 >nul

echo.
echo Active Python processes:
wmic process where "name='python.exe'" get ProcessId,CommandLine 2>nul | findstr /i python

echo.
echo Listening ports:
netstat -an | findstr "LISTENING" | findstr "800"

echo.
echo ========================================
echo Running diagnostics...
echo ========================================
python diagnose.py

echo.
echo ========================================
echo If services failed to start:
echo 1. Check the command windows for error messages
echo 2. Try running TEST_INDIVIDUAL.bat to test each service
echo 3. Check if ports are already in use by other applications
echo ========================================
pause