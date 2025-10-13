@echo off
cls
echo ================================================================================
echo     STOCK TRACKER V3 - FRONTEND SERVER
echo ================================================================================
echo.
echo Starting frontend server on http://localhost:8000
echo.
echo Make sure backend services are running (START_SYSTEM.bat)
echo.

REM Start Python HTTP server in current directory
python -m http.server 8000

pause