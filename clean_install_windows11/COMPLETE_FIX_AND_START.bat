@echo off
REM ============================================================
REM COMPLETE FIX AND START - Fixes everything including landing page
REM ============================================================

echo ============================================================
echo     COMPLETE STOCK TRACKER FIX AND START
echo     Windows 11 Production Environment
echo ============================================================
echo.

REM Step 1: Kill all existing Python processes
echo [1/8] Terminating existing processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul

REM Step 2: Clear ports
echo [2/8] Clearing ports 8000, 8002, 8003...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
timeout /t 2 >nul

REM Step 3: Fix the landing page
echo [3/8] Updating landing page with all 7 modules...
if exist index_complete.html (
    copy /Y index_complete.html index.html >nul
    echo Landing page updated successfully!
) else (
    echo WARNING: index_complete.html not found
)

REM Step 4: Apply backend fixes
echo [4/8] Applying comprehensive fixes to backend.py...
if exist FINAL_FIX_ALL.py (
    python FINAL_FIX_ALL.py
) else (
    echo WARNING: FINAL_FIX_ALL.py not found, skipping backend fix
)
timeout /t 2 >nul

REM Step 5: Install/Update dependencies
echo [5/8] Installing dependencies...
pip install --quiet --upgrade fastapi uvicorn yfinance pandas numpy joblib scikit-learn python-multipart aiofiles
pip install --quiet urllib3==1.26.15
timeout /t 2 >nul

REM Step 6: Start Frontend HTTP Server
echo [6/8] Starting Frontend Server on port 8000...
start /min cmd /c "cd /d %CD% && python -m http.server 8000"
timeout /t 3 >nul

REM Step 7: Start Backend API Server
echo [7/8] Starting Backend API on port 8002...
start /min cmd /c "cd /d %CD% && python -m uvicorn backend:app --host 0.0.0.0 --port 8002 --reload"
timeout /t 3 >nul

REM Step 8: Start ML Backend Server
echo [8/8] Starting ML Backend on port 8003...
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
echo   - Frontend:    http://localhost:8000 (with 7 modules)
echo   - Backend API: http://localhost:8002 (with fixed routes)
echo   - ML Backend:  http://localhost:8003
echo.
echo Modules available:
echo   1. Global Stock Tracker
echo   2. Document Analyser with FinBERT
echo   3. Technical Analysis Enhanced v5.3
echo   4. Historical Data Manager
echo   5. ML Training Centre
echo   6. CBA Enhanced
echo   7. Prediction Centre
echo.
echo Opening browser to landing page...
timeout /t 2 >nul
start http://localhost:8000

echo.
echo Press any key to check service status...
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