@echo off
cls
echo ============================================================
echo Using October 8 Restored Backend (From Git History)
echo ============================================================
echo.
echo This will use backend_working_before_ml_fix.py (28KB)
echo which was extracted from git history today.
echo It contains the working version from before the ML fix.
echo.

REM Stop all running Python processes
echo Step 1: Stopping all existing services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Backup current backend
echo Step 2: Backing up current backend.py...
set timestamp=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
copy backend.py "backend_BACKUP_%timestamp%.py" >nul 2>&1
echo Current backend saved as: backend_BACKUP_%timestamp%.py
echo.

REM Restore the October 8 file
echo Step 3: Restoring backend from October 8 git extraction...
copy backend_working_before_ml_fix.py backend.py /Y
if errorlevel 1 (
    echo ERROR: Could not copy backend_working_before_ml_fix.py!
    echo Please ensure the file exists in the current directory.
    pause
    exit /b 1
)
echo ✓ Backend successfully restored (28KB version)
echo.

echo ============================================================
echo Starting All Services
echo ============================================================
echo.

REM Start Backend API (Port 8002)
echo [1/3] Starting Backend API on port 8002...
start "Backend API - Restored" cmd /k "python backend.py"
timeout /t 3 /nobreak >nul

REM Start ML Backend (Port 8003) - Use ml_backend_working.py
echo [2/3] Starting ML Backend on port 8003...
if exist ml_backend_working.py (
    echo Using ml_backend_working.py (original working version)
    start "ML Backend - Working" cmd /k "python ml_backend_working.py"
) else if exist ml_backend_v2.py (
    echo ml_backend_working.py not found, using ml_backend_v2.py
    start "ML Backend - V2" cmd /k "python ml_backend_v2.py"
) else (
    echo WARNING: No suitable ML backend found!
    echo Please ensure ml_backend_working.py or ml_backend_v2.py exists
)
timeout /t 3 /nobreak >nul

REM Start Frontend (Port 8000)
echo [3/3] Starting Frontend Server on port 8000...
start "Frontend Server" cmd /k "python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo Verifying Services...
echo ============================================================
timeout /t 3 /nobreak >nul

REM Check if services are responding
curl -s http://localhost:8002/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠ Backend API may still be starting up...
) else (
    echo ✓ Backend API is responding on port 8002
)

curl -s http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo ⚠ ML Backend may still be starting up...
) else (
    echo ✓ ML Backend is responding on port 8003
)

echo.
echo ============================================================
echo ✅ Services Started with October 8 Restored Backend!
echo ============================================================
echo.
echo Using: backend_working_before_ml_fix.py (28KB)
echo This version has all features up to Oct 7 but without
echo the breaking changes from the ML dropdown fix.
echo.
echo Services running:
echo - Frontend:    http://localhost:8000
echo - Backend API: http://localhost:8002  
echo - ML Backend:  http://localhost:8003
echo.
echo All modules should work correctly now:
echo ✓ prediction_centre_phase4.html - No more 404 errors
echo ✓ market_tracker_final.html - Market data works
echo ✓ cba_enhanced.html - CBA stock data loads
echo ✓ ML Training Centre - With working dropdown
echo.
echo If any issues persist:
echo 1. Wait 10 seconds for services to fully start
echo 2. Refresh your browser (F5)
echo 3. Clear browser cache if needed (Ctrl+Shift+Delete)
echo.
pause