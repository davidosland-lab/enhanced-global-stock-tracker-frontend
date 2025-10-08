@echo off
cls
echo ============================================================
echo Starting ML Backend - Try All Options Until One Works
echo ============================================================
echo.

REM Kill any existing process on port 8003
echo Clearing port 8003...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo Trying different ML backends in order of simplicity...
echo.

REM Option 1: Ultra Simple (no dependencies)
if exist ml_backend_ultra_simple.py (
    echo [1] Trying ml_backend_ultra_simple.py (no external dependencies)...
    start "ML Backend - Ultra Simple" cmd /k "python ml_backend_ultra_simple.py"
    timeout /t 3 /nobreak >nul
    curl -s http://localhost:8003/health >nul 2>&1
    if not errorlevel 1 (
        echo SUCCESS! ML Backend started with ultra_simple version.
        goto :success
    )
    echo Failed. Trying next option...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1
    echo.
)

REM Option 2: Simple
if exist ml_backend_simple.py (
    echo [2] Trying ml_backend_simple.py...
    start "ML Backend - Simple" cmd /k "python ml_backend_simple.py"
    timeout /t 3 /nobreak >nul
    curl -s http://localhost:8003/health >nul 2>&1
    if not errorlevel 1 (
        echo SUCCESS! ML Backend started with simple version.
        goto :success
    )
    echo Failed. Trying next option...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1
    echo.
)

REM Option 3: Minimal
if exist ml_backend_minimal.py (
    echo [3] Trying ml_backend_minimal.py...
    start "ML Backend - Minimal" cmd /k "python ml_backend_minimal.py"
    timeout /t 3 /nobreak >nul
    curl -s http://localhost:8003/health >nul 2>&1
    if not errorlevel 1 (
        echo SUCCESS! ML Backend started with minimal version.
        goto :success
    )
    echo Failed. Trying next option...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1
    echo.
)

REM Option 4: Working
if exist ml_backend_working.py (
    echo [4] Trying ml_backend_working.py...
    start "ML Backend - Working" cmd /k "python ml_backend_working.py"
    timeout /t 3 /nobreak >nul
    curl -s http://localhost:8003/health >nul 2>&1
    if not errorlevel 1 (
        echo SUCCESS! ML Backend started with working version.
        goto :success
    )
    echo Failed. Trying next option...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1
    echo.
)

REM Option 5: V2
if exist ml_backend_v2.py (
    echo [5] Trying ml_backend_v2.py...
    start "ML Backend - V2" cmd /k "python ml_backend_v2.py"
    timeout /t 3 /nobreak >nul
    curl -s http://localhost:8003/health >nul 2>&1
    if not errorlevel 1 (
        echo SUCCESS! ML Backend started with v2 version.
        goto :success
    )
    echo Failed.
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1
    echo.
)

echo ============================================================
echo ERROR: Could not start any ML Backend!
echo ============================================================
echo.
echo Please check:
echo 1. Python is installed and in PATH
echo 2. Required packages are installed:
echo    pip install fastapi uvicorn
echo.
echo For the ultra_simple version, only Python is required.
echo.
echo Try running manually:
echo    python ml_backend_ultra_simple.py
echo.
pause
exit /b 1

:success
echo.
echo ============================================================
echo ML Backend Successfully Started on Port 8003!
echo ============================================================
echo.
echo Testing connection...
curl http://localhost:8003/health 2>nul
echo.
echo.
echo ML Backend is ready to use with the Stock Tracker.
echo.
echo If the main application is not running, start it with:
echo   START_ALL_SERVICES.bat
echo.
pause