@echo off
echo ============================================
echo STOCK TRACKER PRO - COMPLETE SYSTEM STARTUP
echo Version 5.0.0 - Clean Install Package
echo ============================================
echo.

REM Change to script directory
cd /D "%~dp0"

echo [1/5] Stopping any existing services...
echo --------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8002"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8003"') do taskkill /PID %%a /F 2>nul
timeout /t 2 >nul

echo.
echo [2/5] Creating necessary directories...
echo --------------------------------------
if not exist "historical_data" mkdir historical_data
if not exist "uploads" mkdir uploads
if not exist "analysis_cache" mkdir analysis_cache
if not exist "ml_models" mkdir ml_models
echo Directories created.

echo.
echo [3/5] Starting Frontend Server (Port 8000)...
echo --------------------------------------
start "Frontend Server" /min cmd /k python -m http.server 8000
timeout /t 2 >nul

echo.
echo [4/5] Starting Main Backend API (Port 8002)...
echo --------------------------------------
echo Features: Real Yahoo Finance data, FinBERT sentiment, 100MB uploads
start "Backend API" /min cmd /k python backend.py
timeout /t 3 >nul

echo.
echo [5/5] Starting ML Backend Service (Port 8003)...
echo --------------------------------------
start "ML Backend" /min cmd /k python ml_backend.py
timeout /t 3 >nul

echo.
echo ============================================
echo SYSTEM STATUS CHECK
echo ============================================
echo.

echo Testing Backend Health...
curl -s http://localhost:8002/api/health 2>nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Backend API is running
) else (
    echo.
    echo [WARNING] Backend API may not be ready yet
)

echo.
echo Testing ML Backend...
curl -s http://localhost:8003/health 2>nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] ML Backend is running
) else (
    echo.
    echo [WARNING] ML Backend may not be ready yet
)

echo.
echo ============================================
echo STARTUP COMPLETE!
echo ============================================
echo.
echo Access the application at:
echo   http://localhost:8000
echo.
echo Service Endpoints:
echo   - Frontend:     http://localhost:8000
echo   - Backend API:  http://localhost:8002
echo   - ML Backend:   http://localhost:8003
echo.
echo Features:
echo   - Real Yahoo Finance data (no synthetic data)
echo   - ADST timezone support (UTC+11)
echo   - FinBERT document analysis
echo   - 100MB file upload support
echo   - Consistent analysis with caching
echo.
echo Market Hours (ADST):
echo   - ASX:   10:00 - 16:00
echo   - FTSE:  19:00 - 03:30 (evening/night)
echo   - S&P:   01:30 - 08:00 (early morning)
echo.
echo To stop all services, close this window and
echo the three service windows that opened.
echo.
pause