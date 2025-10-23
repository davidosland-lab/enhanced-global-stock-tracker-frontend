@echo off
title Stock Tracker - Start All Three Services
color 0A

echo ================================================================================
echo               STARTING ALL THREE STOCK TRACKER SERVICES
echo ================================================================================
echo.
echo This will open 3 separate command windows:
echo   1. Frontend Server (Port 8000)
echo   2. Main Backend (Port 8002) 
echo   3. ML Backend (Port 8003)
echo.
echo IMPORTANT: Keep all 3 windows open while using Stock Tracker!
echo.
echo Press any key to start all services...
pause >nul

echo.
echo Starting services in separate windows...
echo.

:: Start Frontend in new window
echo [1/3] Starting Frontend Server on port 8000...
start "Frontend Server - Port 8000" cmd /k "cd /d %cd% && echo Starting Frontend Server on port 8000... && python -m http.server 8000"

timeout /t 2 /nobreak >nul

:: Start Main Backend in new window
echo [2/3] Starting Main Backend on port 8002...
if exist backend.py (
    start "Main Backend - Port 8002" cmd /k "cd /d %cd% && echo Starting Main Backend on port 8002... && python backend.py"
) else (
    echo       ERROR: backend.py not found!
)

timeout /t 2 /nobreak >nul

:: Start ML Backend in new window
echo [3/3] Starting ML Backend on port 8003...
if exist backend_ml_enhanced.py (
    start "ML Backend - Port 8003" cmd /k "cd /d %cd% && echo Starting ML Backend on port 8003... && python backend_ml_enhanced.py"
) else (
    echo       ERROR: backend_ml_enhanced.py not found!
    echo       ML Training Centre will show Disconnected
)

echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

echo.
echo ================================================================================
echo                    CHECKING SERVICE STATUS
echo ================================================================================
echo.

:: Quick status check
netstat -an | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ Frontend running on port 8000
) else (
    echo    ✗ Frontend not detected on port 8000
)

netstat -an | findstr :8002 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ Main Backend running on port 8002
) else (
    echo    ✗ Main Backend not detected on port 8002
)

netstat -an | findstr :8003 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ ML Backend running on port 8003
) else (
    echo    ✗ ML Backend not detected on port 8003
)

echo.
echo ================================================================================
echo                         IMPORTANT NOTES
echo ================================================================================
echo.
echo 1. You should now have 3 command windows open
echo 2. DO NOT close these windows while using Stock Tracker
echo 3. If a window shows errors, check for missing Python packages
echo 4. To install missing packages: pip install fastapi uvicorn yfinance pandas
echo.
echo Opening Stock Tracker in your browser...
timeout /t 2 /nobreak >nul
start http://localhost:8000

echo.
echo If ML Training Centre still shows "Disconnected":
echo   - Check the ML Backend window (Port 8003) for errors
echo   - Make sure Windows Firewall isn't blocking port 8003
echo   - Try running as Administrator
echo.
pause