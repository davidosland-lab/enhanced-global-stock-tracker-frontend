@echo off
:: Check if server is running and on which port

color 0B
cls

echo ============================================================
echo  CHECKING SERVER STATUS
echo ============================================================
echo.

echo Checking what's running on port 8000...
netstat -an | findstr :8000

echo.
echo Checking Python processes...
tasklist | findstr python

echo.
echo ============================================================
echo  TESTING SERVER ENDPOINTS
echo ============================================================
echo.

:: Test if server is responding
echo Testing http://localhost:8000/health ...
curl -s http://localhost:8000/health 2>nul
if %errorlevel% equ 0 (
    echo.
    echo [OK] Server is responding!
) else (
    echo.
    echo [ERROR] Server not responding or curl not available
)

echo.
echo ============================================================
echo  QUICK FIX OPTIONS
echo ============================================================
echo.
echo If server is NOT running:
echo   1. Double-click START_NOW_CMD.bat
echo   2. Or double-click OPEN_CMD_HERE.bat and run:
echo      venv\Scripts\python.exe backend\test_server.py
echo.
echo If server IS running but endpoints don't work:
echo   1. Kill it: taskkill /F /IM python.exe
echo   2. Start fresh with START_NOW_CMD.bat
echo.
pause