@echo off
cls
echo ================================================================
echo     SIMPLE STARTUP - NO COMPLICATIONS
echo ================================================================
echo.

:: Kill everything first
echo Cleaning up...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

:: Backend
echo Starting Backend...
start "BACKEND" python backend.py
timeout /t 5 >nul

:: Frontend  
echo Starting Frontend...
start "FRONTEND" python -m http.server 8000
timeout /t 2 >nul

:: Open browser
echo Opening browser...
start http://localhost:8000

echo.
echo ================================================================
echo KEEP BOTH WINDOWS OPEN!
echo Backend window = Data server
echo Frontend window = Web server
echo ================================================================
echo.
pause