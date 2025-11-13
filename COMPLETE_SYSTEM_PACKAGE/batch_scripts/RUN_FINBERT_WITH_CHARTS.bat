@echo off
echo ===============================================
echo   FinBERT Ultimate Trading System with Charts
echo ===============================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Set Flask environment variable
set FLASK_SKIP_DOTENV=1

echo [1/3] Starting FinBERT Ultimate backend server...
echo.

:: Start the backend server
start "FinBERT Ultimate Server" /min cmd /c "python app_finbert_ultimate.py"

:: Wait for server to start
echo Waiting for server to initialize...
timeout /t 5 /nobreak >nul

:: Check if server is running
curl -s http://localhost:5000/ >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Server might still be starting up...
    echo Please wait a moment and refresh the browser if needed.
) else (
    echo [SUCCESS] Server is running!
)

echo.
echo [2/3] Opening FinBERT Charts interface...
echo.

:: Open the charts in default browser
start "" "finbert_charts.html"

echo.
echo [3/3] System is ready!
echo.
echo ===============================================
echo   Access Points:
echo   - API Server: http://localhost:5000
echo   - Charts UI:  file://%cd%\finbert_charts.html
echo ===============================================
echo.
echo Press Ctrl+C in the server window to stop the backend
echo.
pause