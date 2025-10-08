@echo off
title Stock Tracker - Start All Services
color 0A

echo ================================================================================
echo                    STOCK TRACKER - COMPLETE STARTUP
echo ================================================================================
echo.
echo This will start all three required services:
echo   1. Frontend Server (Port 8000) - Web Interface
echo   2. Main Backend (Port 8002) - Stock Data API
echo   3. ML Backend (Port 8003) - Machine Learning API
echo.
echo Press any key to start all services...
pause >nul

echo.
echo [STEP 1/4] Cleaning up any existing services...
echo.

:: Kill any existing services on our ports
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000"') do (
    echo    Stopping process on port 8000 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8002"') do (
    echo    Stopping process on port 8002 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8003"') do (
    echo    Stopping process on port 8003 (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 /nobreak >nul
echo    ✓ Cleanup complete

echo.
echo [STEP 2/4] Starting Frontend Server (Port 8000)...
echo.

if exist index.html (
    start "Frontend Server (8000)" /min cmd /c "python -m http.server 8000"
    echo    ✓ Frontend server starting...
    timeout /t 2 /nobreak >nul
) else (
    echo    ✗ ERROR: index.html not found!
    echo    Please run this from the Stock Tracker directory
)

echo.
echo [STEP 3/4] Starting Main Backend (Port 8002)...
echo.

if exist backend.py (
    start "Main Backend (8002)" /min cmd /c "python backend.py"
    echo    ✓ Main backend starting...
    timeout /t 3 /nobreak >nul
) else (
    echo    ✗ ERROR: backend.py not found!
)

echo.
echo [STEP 4/4] Starting ML Backend (Port 8003)...
echo.

if exist backend_ml_enhanced.py (
    start "ML Backend (8003)" /min cmd /c "python backend_ml_enhanced.py"
    echo    ✓ ML backend starting...
    timeout /t 3 /nobreak >nul
) else (
    echo    ✗ ERROR: backend_ml_enhanced.py not found!
)

echo.
echo ================================================================================
echo                         VERIFYING ALL SERVICES
echo ================================================================================
echo.

:: Wait a bit more for services to fully start
timeout /t 3 /nobreak >nul

:: Check Frontend
netstat -an | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ Frontend Server:    RUNNING on port 8000
) else (
    echo    ✗ Frontend Server:    NOT RUNNING
)

:: Check Main Backend
netstat -an | findstr :8002 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ Main Backend:       RUNNING on port 8002
) else (
    echo    ✗ Main Backend:       NOT RUNNING
)

:: Check ML Backend
netstat -an | findstr :8003 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ ML Backend:         RUNNING on port 8003
) else (
    echo    ✗ ML Backend:         NOT RUNNING
)

echo.
echo ================================================================================
echo                    TESTING SERVICE CONNECTIONS
echo ================================================================================
echo.

:: Test Main Backend
echo Testing Main Backend API...
curl -s http://localhost:8002/api/stock/CBA.AX >test.tmp 2>nul
if %errorlevel% == 0 (
    echo    ✓ Main Backend API responding
    del test.tmp >nul 2>&1
) else (
    echo    ! Main Backend API not responding yet
)

:: Test ML Backend
echo Testing ML Backend Health...
curl -s http://localhost:8003/health >test.tmp 2>nul
if %errorlevel% == 0 (
    echo    ✓ ML Backend Health endpoint responding
    del test.tmp >nul 2>&1
) else (
    echo    ! ML Backend not responding yet
)

echo.
echo ================================================================================
echo                         ✓ STARTUP COMPLETE!
echo ================================================================================
echo.
echo Stock Tracker is now running!
echo.
echo Access the application at: http://localhost:8000
echo.
echo Service Status:
echo   • Frontend:    http://localhost:8000
echo   • Main API:    http://localhost:8002
echo   • ML API:      http://localhost:8003/health
echo.
echo To stop all services:
echo   1. Close this window
echo   2. Run shutdown.bat or STOP_ALL_SERVICES.bat
echo.
echo Opening Stock Tracker in your browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000
echo.
pause