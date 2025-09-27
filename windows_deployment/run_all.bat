@echo off
echo ====================================================
echo    Enhanced Stock Tracker ML System
echo    Starting all components...
echo ====================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run 'setup.bat' first to install the system.
    pause
    exit /b 1
)

REM Start the backend server
echo Starting backend server...
start "Stock Tracker Backend" cmd /k "call venv\Scripts\activate.bat && python backend_server.py"

REM Wait for server to start
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

REM Open the dashboard in default browser
echo Opening dashboard in browser...
start http://localhost:8000/dashboard

echo.
echo ====================================================
echo    System Started Successfully!
echo ====================================================
echo.
echo The dashboard should open in your browser automatically.
echo If not, navigate to: http://localhost:8000/dashboard
echo.
echo To stop the system, close the backend server window.
echo.
pause