@echo off
cls
color 0C
echo ================================================================
echo     EMERGENCY RESTART - BOTH SERVERS DOWN
echo ================================================================
echo.

echo [STEP 1] Killing ALL Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul

echo.
echo [STEP 2] Clearing all ports...
:: Clear port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a 2>nul
)
:: Clear port 8002
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a 2>nul
)
:: Clear port 8003
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 >nul

echo.
echo [STEP 3] Verifying ports are free...
netstat -ano | findstr "8000 8002" >nul 2>&1
if not errorlevel 1 (
    echo Some ports still in use, forcing cleanup...
    taskkill /F /IM python.exe 2>nul
    timeout /t 3 >nul
)

color 0A
echo.
echo [STEP 4] Starting Backend on port 8002...
start "BACKEND - DO NOT CLOSE" /MAX cmd /k "color 0E && echo BACKEND SERVER - KEEP THIS WINDOW OPEN && python backend.py"
timeout /t 5 >nul

echo.
echo [STEP 5] Starting Frontend on port 8000...
start "FRONTEND SERVER" /MIN cmd /k "python -m http.server 8000"
timeout /t 3 >nul

echo.
echo [STEP 6] Testing services...
echo.
echo Testing Backend...
curl -s http://localhost:8002/api/status >nul 2>&1
if errorlevel 1 (
    color 0E
    echo WARNING: Backend may need more time to start
    timeout /t 5 >nul
) else (
    echo Backend: ONLINE
)

echo Testing Frontend...
curl -s http://localhost:8000 >nul 2>&1
if errorlevel 1 (
    echo Frontend: Starting...
) else (
    echo Frontend: ONLINE
)

color 0B
echo.
echo ================================================================
echo     SERVICES RESTARTED
echo ================================================================
echo.
echo Backend:  http://localhost:8002  [YELLOW WINDOW - KEEP OPEN]
echo Frontend: http://localhost:8000
echo.
echo IMPORTANT RULES:
echo 1. DO NOT CLOSE the yellow BACKEND window
echo 2. Access app at: http://localhost:8000
echo 3. If backend window closes, everything stops!
echo.
echo Opening browser in 3 seconds...
timeout /t 3 >nul
start http://localhost:8000

echo.
echo ================================================================
echo If the browser shows errors:
echo 1. Press Ctrl+F5 to hard refresh
echo 2. Check if the BACKEND window is still open
echo 3. Try: http://localhost:8002/api/status
echo ================================================================
echo.
pause