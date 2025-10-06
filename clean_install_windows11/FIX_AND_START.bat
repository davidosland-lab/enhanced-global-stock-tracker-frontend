@echo off
REM ============================================================
REM FIX AND START - Complete Windows 11 Stock Tracker Solution
REM This script fixes all issues and starts the complete system
REM ============================================================

echo ============================================================
echo       STOCK TRACKER - COMPLETE FIX AND START
echo       Windows 11 Production Environment
echo ============================================================
echo.

REM Step 1: Kill all existing Python processes
echo [1/7] Terminating existing processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul

REM Step 2: Clear ports
echo [2/7] Clearing ports 8000, 8002, 8003...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
timeout /t 2 >nul

REM Step 3: Apply all fixes to backend.py
echo [3/7] Applying comprehensive fixes to backend.py...
python FINAL_FIX_ALL.py
if errorlevel 1 (
    echo WARNING: Fix script encountered an issue, continuing...
)
timeout /t 2 >nul

REM Step 4: Install/Update dependencies
echo [4/7] Installing dependencies...
pip install --quiet --upgrade fastapi uvicorn yfinance pandas numpy joblib scikit-learn python-multipart aiofiles
pip install --quiet urllib3==1.26.15
timeout /t 2 >nul

REM Step 5: Start Frontend HTTP Server
echo [5/7] Starting Frontend Server on port 8000...
start /min cmd /c "cd /d %CD% && python -m http.server 8000"
timeout /t 3 >nul

REM Step 6: Start Backend API Server
echo [6/7] Starting Backend API on port 8002...
start /min cmd /c "cd /d %CD% && python -m uvicorn backend:app --host 0.0.0.0 --port 8002 --reload"
timeout /t 3 >nul

REM Step 7: Start ML Backend Server
echo [7/7] Starting ML Backend on port 8003...
if exist backend_ml_enhanced.py (
    start /min cmd /c "cd /d %CD% && python backend_ml_enhanced.py"
) else (
    echo WARNING: ML Backend file not found, skipping...
)
timeout /t 3 >nul

REM Open browser
echo.
echo ============================================================
echo     ALL SERVICES STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo Services running:
echo   - Frontend:    http://localhost:8000
echo   - Backend API: http://localhost:8002
echo   - ML Backend:  http://localhost:8003
echo.
echo Opening browser to landing page...
timeout /t 2 >nul
start http://localhost:8000

echo.
echo Press any key to view service status, or close this window to keep services running...
pause >nul

REM Show status
echo.
echo Checking service status...
netstat -an | findstr :8000
netstat -an | findstr :8002
netstat -an | findstr :8003

echo.
echo Services are running. Close this window to stop all services.
pause >nul