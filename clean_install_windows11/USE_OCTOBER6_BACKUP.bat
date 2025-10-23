@echo off
cls
echo ============================================================
echo Using October 6 Backup (Known Working Version)
echo ============================================================
echo.
echo This will use the backup from October 6, 2025 which was
echo definitely working before the ML dropdown fix.
echo.

REM Stop services
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Use the October 6 backup
echo Restoring from October 6 backup...
copy backend_backup_20251006_075806.py backend.py /Y
echo ✓ Backend restored from October 6 backup
echo.

REM Start all services
echo Starting all services...
echo.
start "Backend API" cmd /k "python backend.py"
timeout /t 2 /nobreak >nul
start "ML Backend" cmd /k "python ml_backend_working.py"
timeout /t 2 /nobreak >nul
start "Frontend Server" cmd /k "python -m http.server 8000"

echo.
echo ============================================================
echo ✅ Done! Services started with October 6 backup
echo ============================================================
echo.
echo Access the application at: http://localhost:8000
echo.
echo This is using the backend from October 6, which was
echo definitely working before any recent fixes.
echo.
pause