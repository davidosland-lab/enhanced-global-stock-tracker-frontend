@echo off
cls
echo ================================================================
echo     STARTING BOTH BACKEND AND FRONTEND
echo ================================================================
echo.

:: Kill any existing processes
echo Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

:: Start Backend
echo Starting Backend on port 8002...
start "Backend Server - KEEP THIS OPEN" cmd /k "python backend.py"

:: Wait for backend
timeout /t 5 >nul

:: Test backend
curl -s http://localhost:8002/api/status >nul 2>&1
if errorlevel 1 (
    echo Backend starting slowly...
    timeout /t 5 >nul
) else (
    echo Backend is running!
)

:: Start Frontend
echo Starting Frontend on port 8000...
start "Frontend Server" /min cmd /c "python -m http.server 8000"
timeout /t 3 >nul

:: Open browser
echo.
echo ================================================================
echo     BOTH SERVICES ARE RUNNING!
echo ================================================================
echo.
echo Backend:  http://localhost:8002 (KEEP THE WINDOW OPEN!)
echo Frontend: http://localhost:8000
echo.
echo IMPORTANT: DO NOT CLOSE THE BACKEND WINDOW!
echo.
echo Opening browser...
start http://localhost:8000

echo.
echo ================================================================
echo This window can be closed, but KEEP THE BACKEND WINDOW OPEN!
echo ================================================================
pause