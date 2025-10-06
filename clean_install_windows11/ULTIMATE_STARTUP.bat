@echo off
REM ============================================================
REM ULTIMATE STARTUP - Starts ALL services including ML Backend
REM Fixes all data flow issues
REM ============================================================

echo ============================================================
echo     ULTIMATE STOCK TRACKER STARTUP
echo     Starting ALL Services with Data Fixes
echo ============================================================
echo.

REM Step 1: Kill ALL Python processes for clean start
echo [Step 1/10] Terminating ALL existing Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
taskkill /F /IM py.exe 2>nul
timeout /t 3 >nul

REM Step 2: Clear ALL ports
echo [Step 2/10] Clearing ports 8000, 8002, 8003...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
timeout /t 2 >nul

REM Step 3: Ensure correct index.html
echo [Step 3/10] Ensuring correct landing page...
if exist index_complete.html (
    copy /Y index_complete.html index.html >nul
    echo Landing page updated!
)

REM Step 4: Apply backend fixes
echo [Step 4/10] Applying backend fixes...
if exist FINAL_FIX_ALL.py (
    python FINAL_FIX_ALL.py
    timeout /t 2 >nul
)

REM Step 5: Create necessary directories
echo [Step 5/10] Creating required directories...
if not exist historical_data mkdir historical_data
if not exist models mkdir models
if not exist uploads mkdir uploads
if not exist predictions mkdir predictions

REM Step 6: Install/Update ALL dependencies
echo [Step 6/10] Installing all dependencies...
pip install --quiet --upgrade fastapi uvicorn yfinance pandas numpy joblib scikit-learn python-multipart aiofiles
pip install --quiet --upgrade tensorflow torch xgboost lightgbm ta-lib
pip install --quiet urllib3==1.26.15
timeout /t 2 >nul

REM Step 7: Start Frontend HTTP Server
echo [Step 7/10] Starting Frontend Server on port 8000...
start "Frontend Server" /min cmd /c "cd /d %CD% && python -m http.server 8000 2>&1"
timeout /t 3 >nul

REM Step 8: Start Main Backend API
echo [Step 8/10] Starting Main Backend API on port 8002...
start "Backend API" /min cmd /c "cd /d %CD% && python -m uvicorn backend:app --host 0.0.0.0 --port 8002 --reload 2>&1"
timeout /t 5 >nul

REM Step 9: Start ML Backend - CRITICAL FOR ML TRAINING CENTRE
echo [Step 9/10] Starting ML Backend on port 8003 (REQUIRED for ML Training)...
if exist backend_ml_enhanced.py (
    start "ML Backend" /min cmd /c "cd /d %CD% && python -m uvicorn backend_ml_enhanced:app --host 0.0.0.0 --port 8003 --reload 2>&1"
    echo ML Backend started successfully!
    timeout /t 5 >nul
) else (
    echo ERROR: backend_ml_enhanced.py not found!
    echo ML Training Centre will not work without this file!
)

REM Step 10: Verify all services are running
echo [Step 10/10] Verifying all services...
timeout /t 3 >nul

echo.
echo ============================================================
echo     CHECKING SERVICE STATUS...
echo ============================================================
echo.

netstat -an | findstr :8000 >nul
if %errorlevel%==0 (
    echo [OK] Frontend Server is running on port 8000
) else (
    echo [FAIL] Frontend Server is NOT running!
)

netstat -an | findstr :8002 >nul
if %errorlevel%==0 (
    echo [OK] Backend API is running on port 8002
) else (
    echo [FAIL] Backend API is NOT running!
)

netstat -an | findstr :8003 >nul
if %errorlevel%==0 (
    echo [OK] ML Backend is running on port 8003
) else (
    echo [WARNING] ML Backend is NOT running - ML Training Centre won't work!
)

echo.
echo ============================================================
echo     ALL SERVICES DEPLOYMENT COMPLETE!
echo ============================================================
echo.
echo Services Status:
echo   Frontend Server:  http://localhost:8000
echo   Backend API:      http://localhost:8002  
echo   ML Backend:       http://localhost:8003
echo.
echo Available Modules:
echo   1. Global Stock Tracker    (uses Backend API)
echo   2. Document Analyser       (uses Backend API)
echo   3. Technical Analysis      (uses Backend API)
echo   4. Historical Data Manager (uses Backend API)
echo   5. ML Training Centre      (uses ML Backend on 8003)
echo   6. CBA Enhanced           (uses Backend API)
echo   7. Prediction Centre      (uses Backend API + ML Backend)
echo.
echo IMPORTANT NOTES:
echo   - Keep this window open to maintain services
echo   - ML Training Centre REQUIRES ML Backend on port 8003
echo   - Wait 10 seconds for all services to fully initialize
echo.
echo Opening browser in 5 seconds...
timeout /t 5 >nul
start http://localhost:8000

echo.
echo Press any key to view detailed status...
pause >nul

REM Show detailed status
echo.
echo Detailed Connection Status:
echo ===========================
netstat -an | findstr :8000
netstat -an | findstr :8002  
netstat -an | findstr :8003

echo.
echo If ML Backend (8003) is not LISTENING, ML Training Centre won't work!
echo.
echo Services are running. DO NOT close this window or services will stop.
pause >nul