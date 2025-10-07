@echo off
REM ============================================================
REM STOCK TRACKER - Desktop Shortcut Startup/Shutdown
REM Place this on your desktop for easy access
REM ============================================================

title Stock Tracker Control Panel
color 0A

:MENU
cls
echo.
echo    =========================================================
echo                  STOCK TRACKER CONTROL PANEL
echo    =========================================================
echo.
echo    [1] START Stock Tracker (Launch all services)
echo    [2] STOP Stock Tracker  (Shutdown all services)
echo    [3] STATUS Check        (View service status)
echo    [4] RESTART Services    (Stop then Start)
echo    [5] EXIT
echo.
echo    =========================================================
echo.
set /p choice="    Enter your choice (1-5): "

if "%choice%"=="1" goto START
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto STATUS
if "%choice%"=="4" goto RESTART
if "%choice%"=="5" goto EXIT
echo Invalid choice! Please try again...
timeout /t 2 >nul
goto MENU

REM ============================================================
REM START SERVICES
REM ============================================================
:START
cls
echo.
echo    =========================================================
echo              STARTING STOCK TRACKER SERVICES
echo    =========================================================
echo.

REM Check if already running
netstat -an | findstr :8002 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo    [WARNING] Services appear to be already running!
    echo.
    set /p confirm="    Start anyway? (y/n): "
    if /i not "%confirm%"=="y" goto MENU
)

echo    [1/9] Checking ports and clearing if necessary...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo        Cleared port 8000
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo        Cleared port 8002
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo        Cleared port 8003
)
timeout /t 2 >nul

echo    [2/9] Creating required directories...
if not exist historical_data mkdir historical_data
if not exist models mkdir models
if not exist uploads mkdir uploads
if not exist predictions mkdir predictions
if not exist logs mkdir logs

echo    [3/9] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo    [ERROR] Python not found! Please install Python 3.x
    pause
    goto MENU
)

echo    [4/9] Installing/updating dependencies...
echo        This may take a minute on first run...
pip install --quiet --upgrade fastapi uvicorn yfinance pandas numpy >nul 2>&1
pip install --quiet --upgrade joblib scikit-learn python-multipart aiofiles >nul 2>&1
pip install --quiet urllib3==1.26.15 >nul 2>&1

echo    [5/9] Verifying backend.py exists...
if not exist backend.py (
    echo    [ERROR] backend.py not found!
    pause
    goto MENU
)

echo    [6/9] Starting Frontend Server (port 8000)...
start "Stock Tracker Frontend" /min cmd /c "python -m http.server 8000 >logs\frontend.log 2>&1"
timeout /t 3 >nul

echo    [7/9] Starting Backend API (port 8002)...
start "Stock Tracker Backend" /min cmd /c "python -m uvicorn backend:app --host 0.0.0.0 --port 8002 --reload >logs\backend.log 2>&1"
timeout /t 5 >nul

echo    [8/9] Starting ML Backend (port 8003)...
if exist backend_ml_enhanced.py (
    start "Stock Tracker ML" /min cmd /c "python -m uvicorn backend_ml_enhanced:app --host 0.0.0.0 --port 8003 --reload >logs\ml.log 2>&1"
    echo        ML Backend started
) else (
    echo        [WARNING] ML Backend not found - ML features disabled
)
timeout /t 5 >nul

echo    [9/9] Verifying all services are running...
echo.
set SERVICES_OK=1

netstat -an | findstr :8000 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo        [OK] Frontend Server running on port 8000
) else (
    echo        [FAIL] Frontend Server NOT running!
    set SERVICES_OK=0
)

netstat -an | findstr :8002 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo        [OK] Backend API running on port 8002
) else (
    echo        [FAIL] Backend API NOT running!
    set SERVICES_OK=0
)

netstat -an | findstr :8003 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo        [OK] ML Backend running on port 8003
) else (
    echo        [WARNING] ML Backend not running (optional)
)

echo.
if %SERVICES_OK%==1 (
    echo    =========================================================
    echo              STOCK TRACKER STARTED SUCCESSFULLY!
    echo    =========================================================
    echo.
    echo    Opening browser to http://localhost:8000
    start http://localhost:8000
    echo.
    echo    Services are running in background.
) else (
    echo    =========================================================
    echo              WARNING: SOME SERVICES FAILED TO START
    echo    =========================================================
    echo.
    echo    Check logs folder for error details.
)
echo.
pause
goto MENU

REM ============================================================
REM STOP SERVICES
REM ============================================================
:STOP
cls
echo.
echo    =========================================================
echo              STOPPING STOCK TRACKER SERVICES
echo    =========================================================
echo.

echo    [1/4] Finding running services...
set FOUND_SERVICES=0

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo        Found Frontend on PID %%a
    set FOUND_SERVICES=1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    echo        Found Backend on PID %%a
    set FOUND_SERVICES=1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    echo        Found ML Backend on PID %%a
    set FOUND_SERVICES=1
)

if %FOUND_SERVICES%==0 (
    echo        No services found running
    echo.
    pause
    goto MENU
)

echo.
echo    [2/4] Stopping services gracefully...

REM Kill by window title first (cleaner)
taskkill /FI "WINDOWTITLE eq Stock Tracker Frontend" >nul 2>&1
taskkill /FI "WINDOWTITLE eq Stock Tracker Backend" >nul 2>&1
taskkill /FI "WINDOWTITLE eq Stock Tracker ML" >nul 2>&1
timeout /t 2 >nul

echo    [3/4] Force stopping any remaining services...

REM Force kill by port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo    [4/4] Verifying all services stopped...
echo.
set ALL_STOPPED=1

netstat -an | findstr :8000 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo        [WARNING] Port 8000 still in use!
    set ALL_STOPPED=0
) else (
    echo        [OK] Port 8000 cleared
)

netstat -an | findstr :8002 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo        [WARNING] Port 8002 still in use!
    set ALL_STOPPED=0
) else (
    echo        [OK] Port 8002 cleared
)

netstat -an | findstr :8003 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo        [WARNING] Port 8003 still in use!
    set ALL_STOPPED=0
) else (
    echo        [OK] Port 8003 cleared
)

echo.
if %ALL_STOPPED%==1 (
    echo    =========================================================
    echo              ALL SERVICES STOPPED SUCCESSFULLY
    echo    =========================================================
) else (
    echo    =========================================================
    echo              WARNING: SOME SERVICES MAY STILL BE RUNNING
    echo    =========================================================
    echo.
    echo    You may need to restart your computer to fully clear ports.
)
echo.
pause
goto MENU

REM ============================================================
REM STATUS CHECK
REM ============================================================
:STATUS
cls
echo.
echo    =========================================================
echo                   SERVICE STATUS CHECK
echo    =========================================================
echo.
echo    Checking service status...
echo.

set FRONTEND_STATUS=STOPPED
set BACKEND_STATUS=STOPPED
set ML_STATUS=STOPPED

netstat -an | findstr :8000 | findstr LISTENING >nul
if %errorlevel%==0 set FRONTEND_STATUS=RUNNING

netstat -an | findstr :8002 | findstr LISTENING >nul
if %errorlevel%==0 set BACKEND_STATUS=RUNNING

netstat -an | findstr :8003 | findstr LISTENING >nul
if %errorlevel%==0 set ML_STATUS=RUNNING

echo    Service Status:
echo    ---------------
echo    Frontend Server (8000):  %FRONTEND_STATUS%
echo    Backend API (8002):      %BACKEND_STATUS%
echo    ML Backend (8003):       %ML_STATUS%
echo.

if "%BACKEND_STATUS%"=="RUNNING" (
    echo    Testing Backend Health...
    curl -s http://localhost:8002/api/health >nul 2>&1
    if %errorlevel%==0 (
        echo        [OK] Backend responding to health check
    ) else (
        echo        [WARNING] Backend not responding to health check
    )
)

echo.
echo    Module Readiness:
echo    -----------------
if "%BACKEND_STATUS%"=="RUNNING" (
    echo    [✓] CBA Enhanced         - Ready
    echo    [✓] Market Tracker       - Ready
    echo    [✓] Technical Analysis   - Ready
    echo    [✓] Document Analyser    - Ready
    echo    [✓] Historical Data      - Ready
) else (
    echo    [✗] All modules require Backend API
)

if "%ML_STATUS%"=="RUNNING" (
    echo    [✓] ML Training Centre   - Ready
    echo    [✓] Advanced Predictions - Ready
) else (
    echo    [✗] ML Training Centre   - Requires ML Backend
    echo    [✗] Advanced Predictions - Requires ML Backend
)

echo.
echo    URLs:
echo    -----
if "%FRONTEND_STATUS%"=="RUNNING" (
    echo    Main Page:    http://localhost:8000
) else (
    echo    Main Page:    Not available (Frontend not running)
)

if "%BACKEND_STATUS%"=="RUNNING" (
    echo    Backend API:  http://localhost:8002
    echo    API Health:   http://localhost:8002/api/health
)

if "%ML_STATUS%"=="RUNNING" (
    echo    ML Backend:   http://localhost:8003/health
)

echo.
pause
goto MENU

REM ============================================================
REM RESTART SERVICES
REM ============================================================
:RESTART
cls
echo.
echo    =========================================================
echo                    RESTARTING SERVICES
echo    =========================================================
echo.
echo    This will stop all services and start them again...
echo.
pause
goto STOP_FOR_RESTART

:STOP_FOR_RESTART
REM Stop all services first
echo    Stopping all services first...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1
timeout /t 3 >nul
goto START

REM ============================================================
REM EXIT
REM ============================================================
:EXIT
cls
echo.
echo    =========================================================
echo                      EXITING CONTROL PANEL
echo    =========================================================
echo.

netstat -an | findstr :8002 | findstr LISTENING >nul
if %errorlevel%==0 (
    echo    [WARNING] Services are still running!
    echo.
    set /p confirm="    Do you want to stop services before exiting? (y/n): "
    if /i "%confirm%"=="y" goto STOP
)

echo    Thank you for using Stock Tracker!
echo.
timeout /t 2 >nul
exit