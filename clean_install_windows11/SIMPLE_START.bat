@echo off
cd /d "%~dp0"
cls
color 0A

echo ================================================================================
echo                    STOCK TRACKER - SIMPLE STARTUP
echo ================================================================================
echo.

echo [1] Killing old Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
timeout /t 2 >nul

echo [2] Installing requirements...
pip install --quiet yfinance fastapi uvicorn pandas numpy "urllib3<2" >nul 2>&1

echo [3] Creating directories...
if not exist "historical_data" mkdir "historical_data"
if not exist "logs" mkdir "logs"

echo [4] Starting Frontend Server (port 8000)...
start /min cmd /c "python -m http.server 8000"
timeout /t 2 >nul

echo [5] Starting Backend API (port 8002)...
start /min cmd /c "python backend.py"
timeout /t 3 >nul

echo [6] Starting ML Backend (port 8003)...
if exist "ml_backend.py" (
    start /min cmd /c "python ml_backend.py"
) else if exist "ml_training_backend.py" (
    start /min cmd /c "python ml_training_backend.py"
)
timeout /t 3 >nul

echo.
echo ================================================================================
echo                          SYSTEM STARTED!
echo ================================================================================
echo.
echo Opening browser to: http://localhost:8000
echo.
echo If the page doesn't load, wait 10 seconds and refresh.
echo.
start http://localhost:8000

echo Press any key to exit (servers will keep running)...
pause >nul