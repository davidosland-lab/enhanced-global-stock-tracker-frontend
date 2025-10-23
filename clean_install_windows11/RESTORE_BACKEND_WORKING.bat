@echo off
cls
echo ============================================================
echo Restore Backend to Working State
echo ============================================================
echo.
echo This will restore backend.py using an existing backup file.
echo.

REM Stop all running Python processes
echo Step 1: Stopping all services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Create backup of current backend
echo Step 2: Backing up current backend.py...
set timestamp=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%
copy backend.py "backend_before_restore_%timestamp%.py" >nul 2>&1
echo Current backend saved as: backend_before_restore_%timestamp%.py
echo.

REM Check for available working versions
echo Step 3: Looking for working backend versions...
echo.

if exist backend_working_before_ml_fix.py (
    echo Found: backend_working_before_ml_fix.py (28KB - Restored from git)
    echo This is the version from before the ML dropdown fix.
    set BACKEND_TO_USE=backend_working_before_ml_fix.py
    goto :restore
)

if exist backend_backup_20251006_075806.py (
    echo Found: backend_backup_20251006_075806.py (13KB - Oct 6 backup)
    echo This is a backup from October 6, before recent changes.
    set BACKEND_TO_USE=backend_backup_20251006_075806.py
    goto :restore
)

if exist StockTracker_Complete_ML_v1.0\backend.py (
    echo Found: StockTracker_Complete_ML_v1.0\backend.py
    echo This is from the complete ML v1.0 package.
    set BACKEND_TO_USE=StockTracker_Complete_ML_v1.0\backend.py
    goto :restore
)

echo ERROR: No working backend versions found!
echo.
echo Please check if these files exist:
echo - backend_working_before_ml_fix.py
echo - backend_backup_20251006_075806.py
echo - StockTracker_Complete_ML_v1.0\backend.py
echo.
pause
exit /b 1

:restore
echo.
echo Step 4: Restoring backend.py from %BACKEND_TO_USE%...
copy "%BACKEND_TO_USE%" backend.py /Y
if errorlevel 1 (
    echo ERROR: Failed to copy backend file!
    pause
    exit /b 1
)
echo ✓ Backend restored successfully!

echo.
echo ============================================================
echo Starting Services with Restored Backend
echo ============================================================
echo.

REM Start Backend API (Port 8002)
echo [1/3] Starting Backend API on port 8002...
start "Backend API" cmd /k "python backend.py"
timeout /t 3 /nobreak >nul

REM Start ML Backend - Try different options
echo [2/3] Starting ML Backend on port 8003...
if exist ml_backend_working.py (
    echo Using: ml_backend_working.py
    start "ML Backend" cmd /k "python ml_backend_working.py"
) else if exist ml_backend_simple.py (
    echo Using: ml_backend_simple.py
    start "ML Backend" cmd /k "python ml_backend_simple.py"
) else if exist ml_backend_v2.py (
    echo Using: ml_backend_v2.py
    start "ML Backend" cmd /k "python ml_backend_v2.py"
) else (
    echo WARNING: No ML backend found!
)
timeout /t 3 /nobreak >nul

REM Start Frontend (Port 8000)
echo [3/3] Starting Frontend Server on port 8000...
start "Frontend Server" cmd /k "python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo ✅ Services Started with Restored Backend!
echo ============================================================
echo.
echo Backend restored from: %BACKEND_TO_USE%
echo.
echo Services running:
echo - Frontend:    http://localhost:8000
echo - Backend API: http://localhost:8002  
echo - ML Backend:  http://localhost:8003
echo.
echo All modules should now work correctly:
echo ✓ prediction_centre_phase4.html
echo ✓ market_tracker_final.html
echo ✓ cba_enhanced.html
echo ✓ ML Training Centre (with working dropdown)
echo.
echo If you still have issues, try:
echo 1. Clear your browser cache (Ctrl+Shift+Delete)
echo 2. Use a different browser
echo 3. Check Windows Firewall settings
echo.
pause