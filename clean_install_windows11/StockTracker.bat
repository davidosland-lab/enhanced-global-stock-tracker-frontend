@echo off
title Stock Tracker Control Panel
color 0A
setlocal EnableDelayedExpansion

:MAIN_MENU
cls
echo ================================================================================
echo                      STOCK TRACKER CONTROL PANEL
echo                         Windows 11 Edition v2.0
echo ================================================================================
echo.
echo    [1] START Stock Tracker  (Launch all services)
echo    [2] STOP Stock Tracker   (Shutdown all services)  
echo    [3] STATUS Check         (View service status)
echo    [4] RESTART Services     (Stop then Start)
echo    [5] OPEN Web Interface   (Launch in browser)
echo    [6] TROUBLESHOOT         (Fix common issues)
echo    [7] EXIT
echo.
echo ================================================================================
echo.
set /p choice="Enter your choice [1-7]: "

if "%choice%"=="1" goto START_ALL
if "%choice%"=="2" goto STOP_ALL
if "%choice%"=="3" goto CHECK_STATUS
if "%choice%"=="4" goto RESTART_ALL
if "%choice%"=="5" goto OPEN_BROWSER
if "%choice%"=="6" goto TROUBLESHOOT
if "%choice%"=="7" exit /b 0
goto MAIN_MENU

:START_ALL
cls
echo ================================================================================
echo                          STARTING STOCK TRACKER
echo ================================================================================
echo.

:: Kill any existing processes on required ports
echo [1/4] Cleaning up ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

:: Start Frontend Server
echo [2/4] Starting Frontend Server (Port 8000)...
start "Frontend Server" /min cmd /c "cd /d %~dp0 && python -m http.server 8000"
timeout /t 2 /nobreak >nul

:: Start Main Backend
echo [3/4] Starting Main Backend (Port 8002)...
start "Main Backend" /min cmd /c "cd /d %~dp0 && python backend.py"
timeout /t 3 /nobreak >nul

:: Start ML Backend
echo [4/4] Starting ML Backend (Port 8003)...
start "ML Backend" /min cmd /c "cd /d %~dp0 && python backend_ml_enhanced.py"
timeout /t 3 /nobreak >nul

echo.
echo ================================================================================
echo ✓ All services started successfully!
echo ================================================================================
echo.
echo Press any key to return to menu...
pause >nul
goto MAIN_MENU

:STOP_ALL
cls
echo ================================================================================
echo                         STOPPING STOCK TRACKER
echo ================================================================================
echo.

echo Shutting down all services...
:: Kill Python processes on our ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    echo Stopping Frontend Server (PID: %%a)...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Stopping Main Backend (PID: %%a)...
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    echo Stopping ML Backend (PID: %%a)...
    taskkill /F /PID %%a 2>nul
)

echo.
echo ================================================================================
echo ✓ All services stopped successfully!
echo ================================================================================
echo.
echo Press any key to return to menu...
pause >nul
goto MAIN_MENU

:CHECK_STATUS
cls
echo ================================================================================
echo                          SERVICE STATUS CHECK
echo ================================================================================
echo.

:: Check Frontend
echo Checking Frontend Server (Port 8000)...
netstat -an | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ Frontend Server:     RUNNING [Port 8000]
    set frontend_status=RUNNING
) else (
    echo    ✗ Frontend Server:     STOPPED
    set frontend_status=STOPPED
)

:: Check Main Backend
echo Checking Main Backend (Port 8002)...
netstat -an | findstr :8002 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ Main Backend:        RUNNING [Port 8002]
    set backend_status=RUNNING
) else (
    echo    ✗ Main Backend:        STOPPED
    set backend_status=STOPPED
)

:: Check ML Backend
echo Checking ML Backend (Port 8003)...
netstat -an | findstr :8003 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ ML Backend:          RUNNING [Port 8003]
    set ml_status=RUNNING
) else (
    echo    ✗ ML Backend:          STOPPED
    set ml_status=STOPPED
)

echo.
echo ================================================================================

:: Check if all services are running
if "%frontend_status%"=="RUNNING" if "%backend_status%"=="RUNNING" if "%ml_status%"=="RUNNING" (
    echo STATUS: ALL SYSTEMS OPERATIONAL ✓
    echo ================================================================================
    echo.
    echo You can access the application at: http://localhost:8000
) else (
    echo STATUS: SOME SERVICES ARE NOT RUNNING ✗
    echo ================================================================================
    echo.
    echo Recommended action: Choose option [1] to start all services
)

echo.
echo Press any key to return to menu...
pause >nul
goto MAIN_MENU

:RESTART_ALL
cls
echo ================================================================================
echo                         RESTARTING ALL SERVICES
echo ================================================================================
echo.
echo Step 1: Stopping all services...
echo.

:: Stop all services
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a 2>nul
)

echo Waiting for ports to be released...
timeout /t 3 /nobreak >nul

echo.
echo Step 2: Starting all services...
echo.
goto START_ALL

:OPEN_BROWSER
cls
echo ================================================================================
echo                         OPENING WEB INTERFACE
echo ================================================================================
echo.

:: Check if services are running
netstat -an | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo Opening Stock Tracker in your default browser...
    start http://localhost:8000
    echo.
    echo ✓ Browser launched successfully!
) else (
    echo ✗ Frontend server is not running!
    echo.
    echo Please start the services first (Option 1)
)

echo.
echo Press any key to return to menu...
pause >nul
goto MAIN_MENU

:TROUBLESHOOT
cls
echo ================================================================================
echo                           TROUBLESHOOTING
echo ================================================================================
echo.
echo Performing system checks...
echo.

:: Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo    ✓ Python is installed
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo        Version: %%i
) else (
    echo    ✗ Python is not installed or not in PATH
    echo        Please install Python 3.8 or higher
)

:: Check required packages
echo.
echo [2/5] Checking required packages...
python -c "import fastapi" 2>nul
if %errorlevel% == 0 (
    echo    ✓ FastAPI installed
) else (
    echo    ✗ FastAPI not installed - run: pip install fastapi
)

python -c "import yfinance" 2>nul
if %errorlevel% == 0 (
    echo    ✓ yfinance installed
) else (
    echo    ✗ yfinance not installed - run: pip install yfinance
)

python -c "import uvicorn" 2>nul
if %errorlevel% == 0 (
    echo    ✓ Uvicorn installed
) else (
    echo    ✗ Uvicorn not installed - run: pip install uvicorn
)

:: Check file existence
echo.
echo [3/5] Checking required files...
if exist "%~dp0backend.py" (
    echo    ✓ backend.py found
) else (
    echo    ✗ backend.py missing
)

if exist "%~dp0backend_ml_enhanced.py" (
    echo    ✓ backend_ml_enhanced.py found
) else (
    echo    ✗ backend_ml_enhanced.py missing
)

if exist "%~dp0index.html" (
    echo    ✓ index.html found
) else (
    echo    ✗ index.html missing
)

:: Check port conflicts
echo.
echo [4/5] Checking for port conflicts...
set port_8000_free=1
set port_8002_free=1
set port_8003_free=1

netstat -an | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 set port_8000_free=0

netstat -an | findstr :8002 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 set port_8002_free=0

netstat -an | findstr :8003 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 set port_8003_free=0

if %port_8000_free% == 1 (
    echo    ✓ Port 8000 is available
) else (
    echo    ! Port 8000 is in use (possibly by our service)
)

if %port_8002_free% == 1 (
    echo    ✓ Port 8002 is available
) else (
    echo    ! Port 8002 is in use (possibly by our service)
)

if %port_8003_free% == 1 (
    echo    ✓ Port 8003 is available
) else (
    echo    ! Port 8003 is in use (possibly by our service)
)

:: Network connectivity test
echo.
echo [5/5] Testing network connectivity...
python -c "import urllib.request; urllib.request.urlopen('https://finance.yahoo.com')" 2>nul
if %errorlevel% == 0 (
    echo    ✓ Internet connection working
    echo    ✓ Yahoo Finance accessible
) else (
    echo    ✗ Cannot reach Yahoo Finance - check internet connection
)

echo.
echo ================================================================================
echo TROUBLESHOOTING COMPLETE
echo ================================================================================
echo.
echo If you're experiencing issues:
echo   1. Ensure Python 3.8+ is installed
echo   2. Install required packages: pip install fastapi uvicorn yfinance pandas numpy
echo   3. Check Windows Firewall settings for ports 8000, 8002, 8003
echo   4. Try running as Administrator
echo.
echo Press any key to return to menu...
pause >nul
goto MAIN_MENU