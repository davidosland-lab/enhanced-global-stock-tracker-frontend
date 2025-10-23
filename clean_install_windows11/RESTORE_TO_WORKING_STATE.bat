@echo off
cls
echo ============================================================
echo Restoring Stock Tracker to Working State (Before ML Fix)
echo ============================================================
echo.
echo This will restore backend.py to the version that was working
echo before the ML dropdown fix that broke multiple modules.
echo.

REM Stop all running Python processes
echo Step 1: Stopping all services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Create backup of current (broken) files
echo Step 2: Creating backup of current files...
if not exist "backups_ml_fix_issue" mkdir "backups_ml_fix_issue"
copy backend.py "backups_ml_fix_issue\backend_broken_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%.py" >nul 2>&1
echo Backup saved to backups_ml_fix_issue folder
echo.

REM Restore the working backend
echo Step 3: Restoring working backend.py...
if exist backend_working_before_ml_fix.py (
    copy backend_working_before_ml_fix.py backend.py /Y >nul
    echo ✓ Restored backend.py to working version
) else (
    echo ✗ ERROR: backend_working_before_ml_fix.py not found!
    echo.
    echo Please ensure you have the working version of backend.py
    echo from before the ML dropdown fix was applied.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Starting Services with Restored Configuration
echo ============================================================
echo.

REM Start Backend API (Port 8002)
echo [1/3] Starting Backend API on port 8002...
start "Backend API" cmd /k "python backend.py"
timeout /t 3 /nobreak >nul

REM Start ML Backend - Use ml_backend_working.py as it was before
echo [2/3] Starting ML Backend on port 8003...
if exist ml_backend_working.py (
    start "ML Backend" cmd /k "python ml_backend_working.py"
) else if exist ml_backend_simple.py (
    start "ML Backend" cmd /k "python ml_backend_simple.py"
) else if exist ml_backend_minimal.py (
    start "ML Backend" cmd /k "python ml_backend_minimal.py"
) else (
    echo WARNING: No suitable ML backend found. Using ml_backend_v2.py
    start "ML Backend" cmd /k "python ml_backend_v2.py"
)
timeout /t 3 /nobreak >nul

REM Start Frontend (Port 8000)
echo [3/3] Starting Frontend Server on port 8000...
start "Frontend Server" cmd /k "python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo ✅ Services Started with Working Configuration!
echo ============================================================
echo.
echo What was restored:
echo - backend.py reverted to version before ML dropdown fix
echo - Default values (0) restored for all market data fields
echo - All API endpoints should work correctly now
echo.
echo Services running:
echo - Frontend:    http://localhost:8000
echo - Backend API: http://localhost:8002  
echo - ML Backend:  http://localhost:8003
echo.
echo The following modules should now work correctly:
echo ✓ prediction_centre_phase4.html
echo ✓ market_tracker_final.html
echo ✓ cba_enhanced.html
echo ✓ All other modules
echo.
echo Note: The ML Training Centre dropdown fix is still in place
echo in ml_training_centre.html, but the backend issues are fixed.
echo.
pause