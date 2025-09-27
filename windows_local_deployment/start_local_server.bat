@echo off
echo ================================================
echo Starting GSMT Trading System - Local Server
echo ================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start backend server
echo Starting Backend API on http://localhost:8000
start "GSMT Backend" cmd /k python backend_local.py

REM Wait for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend server
echo Starting Frontend on http://localhost:3000
start "GSMT Frontend" cmd /k python -m http.server 3000 --directory frontend

echo.
echo ================================================
echo System is starting...
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the frontend in your browser...
pause >nul

start http://localhost:3000
echo.
echo To stop the servers, close the command windows.
pause