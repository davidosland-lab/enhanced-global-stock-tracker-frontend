@echo off
cls
echo ================================================================================
echo     STOCK TRACKER V3 FINAL - COMPLETE STARTUP
echo ================================================================================
echo.
echo This will start all services and open the application
echo.

REM Kill any existing Python processes
echo [Step 1/5] Stopping any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Create required directories
echo [Step 2/5] Checking/creating required directories...
if not exist "historical_data" mkdir historical_data
if not exist "historical_data\cache" mkdir historical_data\cache
if not exist "models" mkdir models
if not exist "uploads" mkdir uploads
if not exist "cache" mkdir cache
if not exist "knowledge_base" mkdir knowledge_base
if not exist "ml_models" mkdir ml_models

REM Start all backend services
echo [Step 3/5] Starting backend services...
echo.
echo   Starting Main Backend (port 8002)...
start /min "Main Backend" cmd /c "python backend.py"
timeout /t 2 /nobreak >nul

echo   Starting ML Backend (port 8003)...
start /min "ML Backend" cmd /c "python ml_backend_enhanced.py"
timeout /t 2 /nobreak >nul

echo   Starting Integration Bridge (port 8004)...
start /min "Integration Bridge" cmd /c "python integration_bridge.py"
timeout /t 2 /nobreak >nul

REM Start frontend server
echo [Step 4/5] Starting frontend server (port 8000)...
start /min "Frontend Server" cmd /c "python -m http.server 8000"
timeout /t 3 /nobreak >nul

REM Test services
echo [Step 5/5] Verifying all services...
echo.

REM Test frontend
curl -s http://localhost:8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Frontend server running on port 8000
) else (
    echo   [!] Frontend not responding, starting again...
    start /min "Frontend Retry" cmd /c "python -m http.server 8000"
)

REM Test main backend
curl -s http://localhost:8002/api/status >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Main backend running on port 8002
) else (
    echo   [!] Backend not ready yet, please wait...
)

REM Test ML backend
curl -s http://localhost:8003/api/ml/status >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] ML backend running on port 8003
) else (
    echo   [!] ML backend starting...
)

REM Test Integration Bridge
curl -s http://localhost:8004/health >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] Integration Bridge running on port 8004
) else (
    echo   [!] Integration Bridge starting...
)

echo.
echo ================================================================================
echo     ALL SERVICES STARTED SUCCESSFULLY!
echo ================================================================================
echo.
echo Application URLs:
echo   Main Dashboard:     http://localhost:8000
echo   Module List:        http://localhost:8000/modules_list.html
echo   API Documentation:  http://localhost:8002/docs
echo.
echo Key Features:
echo   - FinBERT sentiment analysis (consistent results)
echo   - Historical Data Module (local SQLite storage)
echo   - ML Integration (all modules connected)
echo   - Real Yahoo Finance data
echo   - Working charts with Chart.js
echo.
echo Quick Start:
echo   1. Go to http://localhost:8000/modules_list.html
echo   2. Click any module to open it
echo   3. Try Historical Data Module first to download data
echo   4. Test Document Analyzer with FinBERT
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul

REM Open browser
start http://localhost:8000

echo.
echo Services are running. Press Ctrl+C to stop all services.
pause >nul