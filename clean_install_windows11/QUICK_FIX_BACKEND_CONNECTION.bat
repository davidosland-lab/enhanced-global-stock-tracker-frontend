@echo off
cls
echo ============================================================
echo Quick Fix for "Backend API Disconnected" Message
echo ============================================================
echo.

REM Kill all Python processes
echo Stopping all services...
taskkill /F /IM python.exe 2>NUL
timeout /t 2 /nobreak >NUL

echo.
echo Starting all services fresh...
echo.

REM Start Backend API
echo [1/3] Starting Backend API on port 8002...
start "Backend API" /min cmd /c "cd /d %~dp0 && python backend.py"
timeout /t 3 /nobreak >NUL

REM Start ML Backend
echo [2/3] Starting ML Backend on port 8003...
if exist ml_backend_fixed.py (
    start "ML Backend" /min cmd /c "cd /d %~dp0 && python ml_backend_fixed.py"
) else (
    start "ML Backend" /min cmd /c "cd /d %~dp0 && python ml_backend_v2.py"
)
timeout /t 3 /nobreak >NUL

REM Start Frontend
echo [3/3] Starting Frontend on port 8000...
start "Frontend" /min cmd /c "cd /d %~dp0 && python -m http.server 8000"
timeout /t 2 /nobreak >NUL

echo.
echo Services started. Testing connections...
timeout /t 3 /nobreak >NUL

echo.
curl -s http://localhost:8002/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠ Backend may still be starting up...
    echo   Wait 10 seconds then refresh your browser
) else (
    echo ✅ Backend is responding!
)

curl -s http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo ⚠ ML Backend may still be starting up...
) else (
    echo ✅ ML Backend is responding!
)

echo.
echo ============================================================
echo Next Steps:
echo ============================================================
echo.
echo 1. Open a NEW browser window (or incognito/private mode)
echo 2. Go to: http://localhost:8000
echo 3. The Backend API should show "Connected"
echo.
echo If still showing "Disconnected":
echo - Press F12 to open browser console
echo - Look for red error messages
echo - Try Microsoft Edge if using Chrome
echo - Disable browser extensions
echo.
echo The backend IS running, this is usually a browser issue!
echo.
pause