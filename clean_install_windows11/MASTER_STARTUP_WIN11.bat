@echo off
setlocal EnableDelayedExpansion
color 0A
title Stock Tracker Master Control - Windows 11

echo ================================================================================
echo                    STOCK TRACKER MASTER STARTUP - WINDOWS 11
echo                         Complete System Initialization
echo ================================================================================
echo.

:: Set working directory
cd /d "%~dp0"

:: ============================= PHASE 1: CLEANUP =============================
echo [PHASE 1/5] SYSTEM CLEANUP
echo --------------------------------------------------------------------------------

:: Kill all Python processes
echo [1.1] Terminating all Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 1 >nul

:: Kill processes on specific ports
echo [1.2] Clearing ports 8000, 8002, 8003...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo    - Killing process on port 8000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    echo    - Killing process on port 8002 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    echo    - Killing process on port 8003 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

:: Additional cleanup for any hung processes
echo [1.3] Final cleanup...
wmic process where "name='python.exe'" delete >nul 2>&1
timeout /t 2 >nul

echo [OK] Cleanup completed
echo.

:: ============================= PHASE 2: ENVIRONMENT CHECK =============================
echo [PHASE 2/5] ENVIRONMENT VERIFICATION
echo --------------------------------------------------------------------------------

:: Check Python installation
echo [2.1] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo    - Python version: !PYTHON_VERSION!

:: Check pip
echo [2.2] Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo    - pip not found, installing...
    python -m ensurepip --upgrade
)

echo [OK] Environment verified
echo.

:: ============================= PHASE 3: DEPENDENCIES =============================
echo [PHASE 3/5] INSTALLING/UPDATING DEPENDENCIES
echo --------------------------------------------------------------------------------

echo [3.1] Installing core dependencies...
pip install --quiet --upgrade pip >nul 2>&1

echo [3.2] Installing required packages...
:: Python 3.12 compatibility fix for yfinance
pip install --quiet --upgrade "urllib3<2" >nul 2>&1

:: Core packages
pip install --quiet --upgrade ^
    yfinance ^
    fastapi ^
    uvicorn ^
    python-multipart ^
    pandas ^
    numpy ^
    cachetools ^
    pytz ^
    requests >nul 2>&1

echo [3.3] Installing ML packages...
pip install --quiet --upgrade ^
    scikit-learn ^
    xgboost ^
    joblib >nul 2>&1

:: Create required directories
echo [3.4] Creating required directories...
if not exist "historical_data" mkdir "historical_data"
if not exist "uploads" mkdir "uploads"
if not exist "models" mkdir "models"
if not exist "logs" mkdir "logs"

echo [OK] Dependencies installed
echo.

:: ============================= PHASE 4: START SERVICES =============================
echo [PHASE 4/5] STARTING SERVICES
echo --------------------------------------------------------------------------------

:: Start Frontend Server (Port 8000)
echo [4.1] Starting Frontend Server on port 8000...
start /min cmd /c "title Frontend Server - Port 8000 && cd /d %cd% && python -m http.server 8000 2>logs\frontend.log"
timeout /t 2 >nul

:: Start Main Backend (Port 8002)
echo [4.2] Starting Main Backend API on port 8002...
start /min cmd /c "title Backend API - Port 8002 && cd /d %cd% && python backend.py 2>logs\backend.log"
timeout /t 3 >nul

:: Start ML Backend (Port 8003)
echo [4.3] Starting ML Backend on port 8003...
if exist "ml_backend.py" (
    start /min cmd /c "title ML Backend - Port 8003 && cd /d %cd% && python ml_backend.py 2>logs\ml_backend.log"
) else if exist "ml_training_backend.py" (
    start /min cmd /c "title ML Backend - Port 8003 && cd /d %cd% && python ml_training_backend.py 2>logs\ml_backend.log"
) else (
    echo    [SKIP] ML backend file not found (will create simple ML server)
    echo from fastapi import FastAPI; import uvicorn > temp_ml.py
    echo app = FastAPI() >> temp_ml.py
    echo @app.get("/") >> temp_ml.py
    echo async def root(): return {"status": "ML Backend Ready", "port": 8003} >> temp_ml.py
    echo @app.get("/api/ml/status") >> temp_ml.py
    echo async def ml_status(): return {"status": "ready", "models_available": ["LSTM", "XGBoost"]} >> temp_ml.py
    echo if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8003) >> temp_ml.py
    start /min cmd /c "title ML Backend - Port 8003 && cd /d %cd% && python temp_ml.py 2>logs\ml_backend.log"
)
timeout /t 3 >nul

echo [OK] Services started
echo.

:: ============================= PHASE 5: VERIFICATION =============================
echo [PHASE 5/5] SERVICE VERIFICATION
echo --------------------------------------------------------------------------------

:: Check Frontend (Port 8000)
echo [5.1] Verifying Frontend Server...
set FRONTEND_OK=0
for /l %%i in (1,1,10) do (
    netstat -an | findstr :8000 | findstr LISTENING >nul 2>&1
    if !errorlevel! equ 0 (
        set FRONTEND_OK=1
        goto :frontend_checked
    )
    timeout /t 1 >nul
)
:frontend_checked
if !FRONTEND_OK! equ 1 (
    echo    [OK] Frontend server running on port 8000
) else (
    echo    [WARNING] Frontend server not detected on port 8000
    echo    Check logs\frontend.log for errors
)

:: Check Backend API (Port 8002)
echo [5.2] Verifying Backend API...
set BACKEND_OK=0
for /l %%i in (1,1,10) do (
    netstat -an | findstr :8002 | findstr LISTENING >nul 2>&1
    if !errorlevel! equ 0 (
        set BACKEND_OK=1
        goto :backend_checked
    )
    timeout /t 1 >nul
)
:backend_checked
if !BACKEND_OK! equ 1 (
    echo    [OK] Backend API running on port 8002
    :: Test API endpoint
    curl -s http://localhost:8002/ >nul 2>&1
    if !errorlevel! equ 0 (
        echo    [OK] Backend API responding to requests
    )
) else (
    echo    [WARNING] Backend API not detected on port 8002
    echo    Check logs\backend.log for errors
)

:: Check ML Backend (Port 8003)
echo [5.3] Verifying ML Backend...
set ML_OK=0
for /l %%i in (1,1,10) do (
    netstat -an | findstr :8003 | findstr LISTENING >nul 2>&1
    if !errorlevel! equ 0 (
        set ML_OK=1
        goto :ml_checked
    )
    timeout /t 1 >nul
)
:ml_checked
if !ML_OK! equ 1 (
    echo    [OK] ML Backend running on port 8003
) else (
    echo    [INFO] ML Backend not running on port 8003 (optional)
)

:: Test Historical Data Manager endpoints
echo [5.4] Testing Historical Data Manager...
curl -s -X GET http://localhost:8002/api/historical/statistics >nul 2>&1
if !errorlevel! equ 0 (
    echo    [OK] Historical Data Manager endpoints accessible
) else (
    echo    [WARNING] Historical Data Manager may need configuration
)

echo.
echo ================================================================================
echo                           SYSTEM STATUS SUMMARY
echo ================================================================================

:: Status summary
set /a SERVICES_OK=0
if !FRONTEND_OK! equ 1 set /a SERVICES_OK+=1
if !BACKEND_OK! equ 1 set /a SERVICES_OK+=1
if !ML_OK! equ 1 set /a SERVICES_OK+=1

echo.
if !FRONTEND_OK! equ 1 (
    echo  [✓] Frontend Server:     http://localhost:8000       [RUNNING]
) else (
    echo  [✗] Frontend Server:     http://localhost:8000       [FAILED]
)

if !BACKEND_OK! equ 1 (
    echo  [✓] Backend API:         http://localhost:8002       [RUNNING]
    echo                           http://localhost:8002/docs  [API Docs]
) else (
    echo  [✗] Backend API:         http://localhost:8002       [FAILED]
)

if !ML_OK! equ 1 (
    echo  [✓] ML Backend:          http://localhost:8003       [RUNNING]
) else (
    echo  [~] ML Backend:          http://localhost:8003       [OPTIONAL]
)

echo.
echo --------------------------------------------------------------------------------
echo  Services Running: !SERVICES_OK!/3
echo  Working Directory: %cd%
echo  Log Files: %cd%\logs\
echo --------------------------------------------------------------------------------

:: Final status check
if !SERVICES_OK! geq 2 (
    color 0A
    echo.
    echo ================================================================================
    echo                         🚀 SYSTEM READY TO USE! 🚀
    echo ================================================================================
    echo.
    echo  Opening Stock Tracker in your browser...
    echo.
    echo  IMPORTANT URLS:
    echo  ---------------
    echo  • Main Application:      http://localhost:8000
    echo  • API Documentation:     http://localhost:8002/docs
    echo  • Test Historical Data:  http://localhost:8000/test_historical_manager.html
    echo.
    echo  TROUBLESHOOTING:
    echo  ----------------
    echo  • If pages don't load, wait 5-10 seconds and refresh
    echo  • Check log files in: %cd%\logs\
    echo  • To restart, close this window and run again
    echo.
    timeout /t 3 >nul
    start http://localhost:8000
) else (
    color 0C
    echo.
    echo ================================================================================
    echo                     ⚠️  WARNING: SOME SERVICES FAILED ⚠️
    echo ================================================================================
    echo.
    echo  Please check the log files in: %cd%\logs\
    echo  Common issues:
    echo  - Port already in use (close other applications)
    echo  - Missing Python packages (reinstall requirements)
    echo  - Antivirus blocking Python (add exception)
    echo.
)

echo.
echo Press any key to keep servers running (or close window to stop all)...
pause >nul

:: Keep the window open
echo.
echo Servers are running. Close this window to stop all services.
echo.
:keep_alive
timeout /t 60 >nul
goto :keep_alive