@echo off
REM =========================================
REM GSMT Windows Launcher - FIXED VERSION
REM Includes localhost URL fixes
REM =========================================

echo.
echo ========================================
echo   Global Stock Market Tracker (GSMT)
echo   Windows Launch Script - FIXED
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Navigate to script directory
cd /d "%~dp0"
echo Working directory: %CD%

REM Fix localhost URLs in HTML files (PowerShell one-liner)
echo.
echo Fixing localhost URLs for Windows...
powershell -Command "(Get-Content simple_working_dashboard.html) -replace 'window.location.protocol.*8002[^''\"]*', '''http://localhost:8002''' | Set-Content simple_working_dashboard.html"
powershell -Command "Get-ChildItem modules\*.html | ForEach-Object { (Get-Content $_) -replace 'window.location.protocol.*8002[^''\"]*', '''http://localhost:8002''' | Set-Content $_ }"
echo URLs fixed for Windows localhost

REM Install/update Python packages
echo.
echo Installing Python dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if port 8002 is already in use
netstat -an | find ":8002" >nul
if not errorlevel 1 (
    echo.
    echo WARNING: Port 8002 is already in use
    echo Attempting to stop existing process...
    taskkill /F /FI "WINDOWTITLE eq GSMT Backend*" >nul 2>&1
    timeout /t 2 /nobreak >nul
)

REM Start backend server
echo.
echo Starting backend server on port 8002...
start "GSMT Backend Server" /MIN cmd /c "python backend_fixed.py"

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

REM Verify backend is running
curl -s http://localhost:8002/ >nul 2>&1
if errorlevel 1 (
    echo WARNING: Backend may not be responding yet
    echo Continuing anyway...
) else (
    echo Backend server is running successfully!
)

REM Open dashboard in default browser
echo.
echo Opening dashboard in browser...
timeout /t 2 /nobreak >nul
start "" "http://localhost:8080/simple_working_dashboard.html"

REM Also try opening with file protocol as backup
start "" "%CD%\simple_working_dashboard.html"

echo.
echo ========================================
echo   GSMT is now running!
echo.
echo   Backend API: http://localhost:8002
echo   Dashboard: Open in your browser
echo.
echo   To stop: Close this window or run STOP_GSMT_WINDOWS.bat
echo ========================================
echo.
echo Press any key to view backend logs...
pause >nul

REM Keep window open to show backend logs
echo.
echo Backend logs (Ctrl+C to stop):
echo --------------------------------
python backend_fixed.py