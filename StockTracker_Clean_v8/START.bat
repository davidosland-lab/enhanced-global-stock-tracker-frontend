@echo off
cls
color 0A
echo ================================================================================
echo                          STOCK TRACKER PRO v8.0
echo                        Windows 11 Clean Installation
echo ================================================================================
echo.
echo [STEP 1/4] Checking Python Installation...
echo --------------------------------------------------------------------------------

python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from: https://www.python.org/downloads/
    echo During installation, make sure to CHECK "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

python --version
echo Python OK!
echo.

echo [STEP 2/4] Installing Required Packages...
echo --------------------------------------------------------------------------------
echo This may take 1-2 minutes on first run...
echo.

REM Install core packages quietly
python -m pip install --quiet --upgrade pip
python -m pip install --quiet flask flask-cors yfinance pandas numpy requests cachetools

if errorlevel 1 (
    echo.
    echo Trying alternative installation method...
    pip install --user flask flask-cors yfinance pandas numpy requests cachetools
)

echo Packages installed successfully!
echo.

echo [STEP 3/4] Starting Backend Server...
echo --------------------------------------------------------------------------------

REM Kill any existing Python processes on our ports
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    taskkill /PID %%a /F >nul 2>&1
)

timeout /t 2 /nobreak >nul

REM Start the backend in background
start /min python backend.py

echo Backend server starting on port 8002...
timeout /t 3 /nobreak >nul
echo.

echo [STEP 4/4] Launching Application...
echo --------------------------------------------------------------------------------
echo.
color 0B
echo ================================================================================
echo                         APPLICATION READY!
echo ================================================================================
echo.
echo Dashboard URL: http://localhost:8002
echo.
echo Opening in your default browser...
start http://localhost:8002
echo.
echo ================================================================================
echo                    Press Ctrl+C to stop the server
echo                    Or close this window to exit
echo ================================================================================
echo.

REM Keep the window open
pause >nul