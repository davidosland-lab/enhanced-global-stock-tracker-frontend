@echo off
title Stock Tracker Complete - Control Panel
color 0A

:MENU
cls
echo ============================================================
echo    Stock Tracker Complete - Windows 11 Control Panel
echo    Version 2.0 with ML Integration
echo ============================================================
echo.
echo    [1] Start Basic System (Frontend + Backend)
echo    [2] Start with ML Integration (All Features)
echo    [3] Start Individual Services
echo    [4] Stop All Services
echo    [5] Check Service Status
echo    [6] Open Dashboard in Browser
echo    [7] Open Integration Dashboard
echo    [8] Run Diagnostics
echo    [9] Exit
echo.
echo ============================================================
set /p choice="Select option (1-9): "

if "%choice%"=="1" goto START_BASIC
if "%choice%"=="2" goto START_FULL
if "%choice%"=="3" goto START_INDIVIDUAL
if "%choice%"=="4" goto STOP_ALL
if "%choice%"=="5" goto CHECK_STATUS
if "%choice%"=="6" goto OPEN_BROWSER
if "%choice%"=="7" goto OPEN_INTEGRATION
if "%choice%"=="8" goto RUN_DIAGNOSTICS
if "%choice%"=="9" goto EXIT

echo Invalid choice. Please try again.
pause
goto MENU

:START_BASIC
cls
echo Starting Basic System...
echo.
echo [1/3] Starting Frontend Server (Port 8000)...
start /min cmd /c "python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo [2/3] Starting Main Backend (Port 8002)...
start /min cmd /c "python backend.py"
timeout /t 2 /nobreak >nul

echo [3/3] Starting ML Backend (Port 8003)...
start /min cmd /c "python ml_backend.py"
timeout /t 3 /nobreak >nul

echo.
echo Basic system started successfully!
echo Dashboard: http://localhost:8000
echo.
pause
goto MENU

:START_FULL
cls
echo Starting Full System with ML Integration...
echo.
echo [1/4] Starting Frontend Server (Port 8000)...
start /min cmd /c "python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo [2/4] Starting Main Backend (Port 8002)...
start /min cmd /c "python backend.py"
timeout /t 2 /nobreak >nul

echo [3/4] Starting ML Backend (Port 8003)...
start /min cmd /c "python ml_backend.py"
timeout /t 2 /nobreak >nul

echo [4/4] Starting Integration Bridge (Port 8004)...
start /min cmd /c "python integration_bridge.py"
timeout /t 3 /nobreak >nul

echo.
echo Full system with ML Integration started!
echo Dashboard: http://localhost:8000
echo Integration Monitor: http://localhost:8000/integration_dashboard.html
echo.
pause
goto MENU

:START_INDIVIDUAL
cls
echo Select Service to Start:
echo.
echo    [1] Frontend Server (Port 8000)
echo    [2] Main Backend (Port 8002)
echo    [3] ML Backend (Port 8003)
echo    [4] Integration Bridge (Port 8004)
echo    [5] Enhanced ML Backend (Alternative)
echo    [6] Back to Menu
echo.
set /p service="Select service (1-6): "

if "%service%"=="1" (
    start /min cmd /c "python -m http.server 8000"
    echo Frontend started on port 8000
)
if "%service%"=="2" (
    start /min cmd /c "python backend.py"
    echo Main Backend started on port 8002
)
if "%service%"=="3" (
    start /min cmd /c "python ml_backend.py"
    echo ML Backend started on port 8003
)
if "%service%"=="4" (
    start /min cmd /c "python integration_bridge.py"
    echo Integration Bridge started on port 8004
)
if "%service%"=="5" (
    start /min cmd /c "python ml_backend_enhanced.py"
    echo Enhanced ML Backend started
)
if "%service%"=="6" goto MENU

pause
goto START_INDIVIDUAL

:STOP_ALL
cls
echo Stopping all services...
taskkill /F /IM python.exe 2>nul
echo All Python services stopped.
pause
goto MENU

:CHECK_STATUS
cls
echo Checking Service Status...
echo.
echo Checking port 8000 (Frontend)...
netstat -an | findstr :8000 | findstr LISTENING >nul
if %errorlevel%==0 (echo    Frontend: RUNNING) else (echo    Frontend: STOPPED)

echo Checking port 8002 (Main Backend)...
netstat -an | findstr :8002 | findstr LISTENING >nul
if %errorlevel%==0 (echo    Main Backend: RUNNING) else (echo    Main Backend: STOPPED)

echo Checking port 8003 (ML Backend)...
netstat -an | findstr :8003 | findstr LISTENING >nul
if %errorlevel%==0 (echo    ML Backend: RUNNING) else (echo    ML Backend: STOPPED)

echo Checking port 8004 (Integration Bridge)...
netstat -an | findstr :8004 | findstr LISTENING >nul
if %errorlevel%==0 (echo    Integration Bridge: RUNNING) else (echo    Integration Bridge: STOPPED)

echo.
pause
goto MENU

:OPEN_BROWSER
start http://localhost:8000
goto MENU

:OPEN_INTEGRATION
start http://localhost:8000/integration_dashboard.html
goto MENU

:RUN_DIAGNOSTICS
cls
echo Running System Diagnostics...
echo.
python -c "import sys; print(f'Python Version: {sys.version}')"
echo.
python -c "import yfinance; print('yfinance: OK')" 2>nul || echo yfinance: NOT INSTALLED
python -c "import fastapi; print('FastAPI: OK')" 2>nul || echo FastAPI: NOT INSTALLED
python -c "import pandas; print('pandas: OK')" 2>nul || echo pandas: NOT INSTALLED
python -c "import numpy; print('numpy: OK')" 2>nul || echo numpy: NOT INSTALLED
python -c "import sklearn; print('scikit-learn: OK')" 2>nul || echo scikit-learn: NOT INSTALLED
echo.
echo Testing API endpoints...
curl -s http://localhost:8002/api/status >nul 2>&1 && echo Main Backend API: OK || echo Main Backend API: NOT RESPONDING
curl -s http://localhost:8003/api/health >nul 2>&1 && echo ML Backend API: OK || echo ML Backend API: NOT RESPONDING
curl -s http://localhost:8004/api/bridge/health >nul 2>&1 && echo Integration Bridge: OK || echo Integration Bridge: NOT RESPONDING
echo.
pause
goto MENU

:EXIT
echo.
echo Thank you for using Stock Tracker Complete!
echo Shutting down...
timeout /t 2 /nobreak >nul
exit