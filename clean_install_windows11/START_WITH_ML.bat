@echo off
title Stock Tracker with ML Training - Complete Launch
color 0A

echo ===============================================================================
echo                 STOCK TRACKER WITH ML TRAINING CENTRE
echo                        Complete System Launch
echo ===============================================================================
echo.

:: Set environment variable to suppress TensorFlow warnings
set TF_ENABLE_ONEDNN_OPTS=0

echo [1/5] Checking and clearing ports...
echo -----------------------------------------------

:: Kill any Python processes on our ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Clearing port 8000...
    taskkill /F /PID %%a 2>nul
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Clearing port 8002...
    taskkill /F /PID %%a 2>nul
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    echo Clearing port 8003...
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 >nul

echo.
echo [2/5] Starting Main Backend (Port 8002)...
echo -----------------------------------------------
start "Stock Tracker Backend" /min cmd /k "python backend.py"
timeout /t 3 >nul

echo.
echo [3/5] Starting ML Training Backend (Port 8003)...
echo -----------------------------------------------
:: Try the working version first
if exist ml_backend_working.py (
    start "ML Training Backend" /min cmd /k "python ml_backend_working.py"
) else if exist ml_backend_simple.py (
    start "ML Training Backend" /min cmd /k "python ml_backend_simple.py"
) else (
    start "ML Training Backend" /min cmd /k "python ml_training_backend.py"
)
timeout /t 3 >nul

echo.
echo [4/5] Starting Frontend Server (Port 8000)...
echo -----------------------------------------------
start "Frontend Server" /min cmd /k "python -m http.server 8000"
timeout /t 2 >nul

echo.
echo [5/5] Verifying all services...
echo -----------------------------------------------

:: Check main backend
curl -s http://localhost:8002/ >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Main Backend: RUNNING on port 8002
) else (
    echo ✗ Main Backend: NOT RESPONDING
)

:: Check ML backend
curl -s http://localhost:8003/health >nul 2>&1
if %errorlevel%==0 (
    echo ✓ ML Backend: RUNNING on port 8003
) else (
    echo ✗ ML Backend: NOT RESPONDING
    echo   Note: ML Training Centre will show as disconnected
)

:: Check frontend
curl -s http://localhost:8000/ >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Frontend: RUNNING on port 8000
) else (
    echo ✗ Frontend: NOT RESPONDING
)

echo.
echo ===============================================================================
echo                         SYSTEM STARTUP COMPLETE
echo ===============================================================================
echo.
echo Access Points:
echo --------------
echo Main Application:    http://localhost:8000
echo Backend API:         http://localhost:8002
echo ML Training API:     http://localhost:8003
echo ML Health Check:     http://localhost:8003/health
echo.
echo Available Modules:
echo -----------------
echo 1. CBA Enhanced Tracker (Real $170 price)
echo 2. Global Indices Tracker
echo 3. Stock Tracker with Technical Analysis
echo 4. Document Uploader (FinBERT)
echo 5. Phase 4 Predictor (Dynamic calculations)
echo 6. ML Training Centre (Real neural networks)
echo.
echo Troubleshooting:
echo ---------------
echo - If ML Training Centre shows "Disconnected":
echo   1. Wait 5-10 seconds and refresh the page
echo   2. Check the ML Backend window for errors
echo   3. Run ML_TRAINING_QUICK_FIX.bat
echo.
echo ===============================================================================
echo.
echo Opening application in browser...
timeout /t 3 >nul
start "" "http://localhost:8000"

echo.
echo Press any key to view service windows...
pause >nul

:: Show the service windows
echo Showing service windows (minimize them if needed)...