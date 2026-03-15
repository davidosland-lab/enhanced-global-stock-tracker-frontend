@echo off
title FinBERT v4.0 DEVELOPMENT
color 0E
cls

echo ================================================================================
echo                     FinBERT v4.0 - DEVELOPMENT VERSION
echo ================================================================================
echo.
echo WARNING: This is a DEVELOPMENT version!
echo For production use, please use v3.3 STABLE
echo.
echo Development Features:
echo [*] Debug mode enabled
echo [*] Hot reload active
echo [*] Verbose logging
echo [*] Test endpoints enabled
echo.
pause

REM Check if we're in the right directory
if not exist "app_finbert_predictions_clean.py" (
    echo ERROR: Development files not found!
    echo Please run this from the FinBERT_v4.0_Development directory
    pause
    exit /b 1
)

REM Kill any existing processes
echo.
echo Stopping any existing instances...
taskkill /F /FI "WindowTitle eq *FinBERT*" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating development virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing development dependencies...
    pip install flask flask-cors numpy pytest pylint black --quiet
)

REM Set development environment variables
set FLASK_ENV=development
set FLASK_DEBUG=1
set FINBERT_VERSION=4.0-DEV

REM Start the development server
echo.
echo ================================================================================
echo Starting FinBERT v4.0 Development Server...
echo ================================================================================
echo.
echo Server will run with:
echo - Debug mode: ON
echo - Auto-reload: ON
echo - Port: 5000
echo.

REM Start with debug mode
python -c "import sys; print(f'Python {sys.version}')"
echo.
start "FinBERT v4.0 DEV Backend" cmd /k "python app_finbert_predictions_clean.py"

timeout /t 5 /nobreak >nul

REM Open development dashboard
echo Opening development interface...
start http://localhost:5000

echo.
echo ================================================================================
echo DEVELOPMENT SERVER RUNNING
echo ================================================================================
echo.
echo URLs:
echo - Main: http://localhost:5000
echo - API: http://localhost:5000/api/stock/[SYMBOL]
echo - Health: http://localhost:5000/api/health
echo.
echo Commands:
echo - Press R to restart server
echo - Press T to run tests
echo - Press L to view logs
echo - Press X to exit
echo.

:dev_menu
choice /c RTLX /n >nul
if errorlevel 4 goto shutdown
if errorlevel 3 goto view_logs
if errorlevel 2 goto run_tests
if errorlevel 1 goto restart_server

:restart_server
echo.
echo Restarting development server...
taskkill /F /FI "WindowTitle eq *FinBERT v4.0 DEV Backend*" >nul 2>&1
timeout /t 2 /nobreak >nul
start "FinBERT v4.0 DEV Backend" cmd /k "python app_finbert_predictions_clean.py"
echo Server restarted!
echo.
goto dev_menu

:run_tests
echo.
echo Running development tests...
echo.
if exist "tests" (
    python -m pytest tests/ -v
) else (
    echo No tests directory found. Creating basic test...
    python -c "import requests; r=requests.get('http://localhost:5000/api/health'); print(f'Health Check: {r.json()}')" 2>nul || echo API test failed!
)
echo.
pause
cls
goto dev_menu

:view_logs
echo.
echo Recent server activity:
echo ========================
REM In a real scenario, we'd tail the log file
echo [Simulated logs - implement actual logging in v4.0]
echo.
pause
cls
goto dev_menu

:shutdown
echo.
echo Shutting down development server...
taskkill /F /FI "WindowTitle eq *FinBERT*" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo.
echo Development session ended.
pause
exit