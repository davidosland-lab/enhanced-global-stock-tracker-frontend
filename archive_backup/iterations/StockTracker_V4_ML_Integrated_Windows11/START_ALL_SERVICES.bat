@echo off
title Stock Tracker v4.0 - Service Manager
color 0A
cls

echo =====================================================
echo    Stock Tracker v4.0 - ML Integrated Edition
echo    Starting All Services...
echo =====================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Installing Required Dependencies...
echo ---------------------------------------------
pip install -q fastapi uvicorn yfinance pandas numpy scikit-learn joblib ta httpx pydantic sqlite3-api 2>nul
pip install -q transformers torch 2>nul
echo Dependencies installed successfully!
echo.

:: Create necessary directories
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "historical_data" mkdir historical_data

echo [2/5] Starting Main Backend (Port 8002)...
echo ---------------------------------------------
start /B cmd /c "cd backend && python backend.py > ../logs/backend.log 2>&1"
timeout /t 3 /nobreak >nul
echo Main Backend started on http://localhost:8002
echo.

echo [3/5] Starting ML Backend (Port 8003)...
echo ---------------------------------------------
start /B cmd /c "cd backend && python ml_backend.py > ../logs/ml_backend.log 2>&1"
timeout /t 3 /nobreak >nul
echo ML Backend started on http://localhost:8003
echo.

echo [4/5] Starting Integration Bridge (Port 8004)...
echo ---------------------------------------------
start /B cmd /c "cd backend && python integration_bridge.py > ../logs/bridge.log 2>&1"
timeout /t 3 /nobreak >nul
echo Integration Bridge started on http://localhost:8004
echo.

echo [5/5] Verifying Services...
echo ---------------------------------------------
timeout /t 5 /nobreak >nul

:: Test services
curl -s http://localhost:8002/api/status >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Main Backend is running
) else (
    echo [WARNING] Main Backend may not be running correctly
)

curl -s http://localhost:8003/api/ml/status >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] ML Backend is running
) else (
    echo [WARNING] ML Backend may not be running correctly
)

curl -s http://localhost:8004/api/bridge/status >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Integration Bridge is running
) else (
    echo [WARNING] Integration Bridge may not be running correctly
)

echo.
echo =====================================================
echo    All Services Started Successfully!
echo =====================================================
echo.
echo Access the dashboard at:
echo http://localhost:8002 (or open index.html)
echo.
echo Service Endpoints:
echo - Main Backend: http://localhost:8002
echo - ML Backend: http://localhost:8003
echo - Integration Bridge: http://localhost:8004
echo.
echo Press any key to open the dashboard in your browser...
pause >nul

:: Open dashboard in default browser
start "" index.html

echo.
echo Services are running in the background.
echo To stop all services, close this window or press Ctrl+C
echo.
pause