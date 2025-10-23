@echo off
cls
echo ================================================================
echo     KILLING PROCESS ON PORT 8002
echo ================================================================
echo.

echo Finding what's using port 8002...
netstat -ano | findstr :8002

echo.
echo Killing ALL processes on port 8002...

:: Kill any process on port 8002
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Killing PID %%a
    taskkill /F /PID %%a
    timeout /t 1 >nul
)

:: Double check with wmic
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    wmic process where ProcessId=%%a delete >nul 2>&1
)

echo.
echo Verifying port 8002 is free...
netstat -ano | findstr :8002
if errorlevel 1 (
    echo SUCCESS: Port 8002 is now FREE!
) else (
    echo WARNING: Port 8002 might still be in use
    echo Trying force kill of all Python processes...
    taskkill /F /IM python.exe
)

echo.
echo ================================================================
echo     NOW START THE BACKEND FRESH
echo ================================================================
echo.
echo Port 8002 should be free now. Starting backend...
echo.

timeout /t 3 >nul

:: Start backend fresh
start "Stock Tracker Backend - KEEP OPEN" cmd /k "python backend.py"

echo.
echo Waiting for backend to start...
timeout /t 5 >nul

:: Test it
curl http://localhost:8002/api/status
if errorlevel 1 (
    echo.
    echo If backend still fails, try changing to a different port:
    echo Edit backend.py and change 8002 to 8082
) else (
    echo.
    echo SUCCESS! Backend is running on port 8002!
)

echo.
pause