@echo off
echo ============================================================
echo Fixing Backend API Issues
echo ============================================================
echo.
echo This fixes the issue where the ML dropdown fix accidentally
echo broke the backend by removing default values.
echo.

REM Stop running services
echo Stopping existing services...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Create backup
echo Creating backup of backend.py...
copy backend.py backend.py.backup_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2% >nul
echo Backup created.

REM Apply the fix
echo Applying fix to backend.py...
python FIX_BACKEND_DEFAULTS.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to apply fix. Please ensure Python is installed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Starting services with fixed backend...
echo ============================================================
echo.

REM Start Backend API (Port 8002)
echo Starting Backend API on port 8002...
start "Backend API" cmd /k "python backend.py"
timeout /t 3 /nobreak >nul

REM Start ML Backend (Port 8003) 
echo Starting ML Backend on port 8003...
start "ML Backend" cmd /k "python ml_backend_v2.py"
timeout /t 3 /nobreak >nul

REM Start Frontend (Port 8000)
echo Starting Frontend Server on port 8000...
start "Frontend Server" cmd /k "python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo ✅ Backend Fixed and Services Started!
echo ============================================================
echo.
echo What was fixed:
echo - Restored default values (0) for missing market data
echo - Fixed issues with prediction_centre_phase4.html
echo - Fixed issues with market_tracker_final.html
echo - Fixed issues with cba_enhanced.html
echo.
echo The application should now work properly.
echo Access it at: http://localhost:8000
echo.
pause