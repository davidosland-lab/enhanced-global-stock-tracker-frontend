@echo off
echo ==========================================
echo Stock Tracker - Service Status Check
echo ==========================================
echo.
echo Checking which services are running...
echo.

:: Check Frontend
echo Frontend Server (Port 8000):
netstat -an | findstr :8000 | findstr LISTENING >nul
if errorlevel 1 (
    echo   [STOPPED] Not running
) else (
    echo   [RUNNING] http://localhost:8000
    curl -s http://localhost:8000 >nul 2>&1
    if errorlevel 1 (
        echo   [WARNING] Port is open but not responding
    )
)

echo.
echo Main Backend API (Port 8002):
netstat -an | findstr :8002 | findstr LISTENING >nul
if errorlevel 1 (
    echo   [STOPPED] Not running
) else (
    echo   [RUNNING] http://localhost:8002
    curl -s http://localhost:8002/health >nul 2>&1
    if errorlevel 1 (
        echo   [WARNING] Port is open but health check failed
    ) else (
        echo   [HEALTHY] API is responding
    )
)

echo.
echo ML Training Backend (Port 8003):
netstat -an | findstr :8003 | findstr LISTENING >nul
if errorlevel 1 (
    echo   [STOPPED] Not running
) else (
    echo   [RUNNING] http://localhost:8003
    curl -s http://localhost:8003/health >nul 2>&1
    if errorlevel 1 (
        echo   [WARNING] Port is open but health check failed
    ) else (
        echo   [HEALTHY] ML Backend is responding
    )
)

echo.
echo ==========================================
echo Quick Actions:
echo ==========================================
echo - To restart all services: Run QUICK_RESTART.bat
echo - To stop all services: Run STOP_ALL_SERVICES.bat
echo - To apply latest fixes: Run APPLY_LATEST_FIXES.bat
echo.
pause