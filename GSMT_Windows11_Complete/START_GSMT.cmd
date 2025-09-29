@echo off
:: GSMT Ver 8.1.3 - Main Launcher (Use .cmd extension to ensure execution)
:: This is a Windows Command file that will execute properly

title GSMT Ver 8.1.3 - Complete System
color 0A
cls

echo ================================================================================
echo                    GSMT STOCK TRACKER Ver 8.1.3
echo                    COMPLETE SYSTEM WITH ALL FIXES
echo ================================================================================
echo.

:: Change to script directory
cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo [✓] Python detected
echo.

:: Install dependencies
echo Installing dependencies...
python -m pip install fastapi uvicorn yfinance pandas numpy scikit-learn --quiet >nul 2>&1
echo [✓] Dependencies ready
echo.

:: Clear ports
echo Clearing ports...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8001"') do taskkill /F /PID %%a >nul 2>&1
echo [✓] Ports cleared
echo.

:: Start servers
echo Starting servers...
start "Market Server" /min cmd /c "python backend\market_data_server.py"
timeout /t 3 /nobreak >nul
start "CBA Server" /min cmd /c "python backend\cba_specialist_server.py"
timeout /t 5 /nobreak >nul
echo [✓] Servers running
echo.

:: Open main dashboard in browser (using proper browser command)
echo Opening dashboard...
start "" "http://localhost:8000/frontend/landing_dashboard_fixed.html"

:: Alternative: Open local HTML file
if exist "frontend\landing_dashboard_fixed.html" (
    start "" /max "frontend\landing_dashboard_fixed.html"
)

echo.
echo ================================================================================
echo GSMT LAUNCHED SUCCESSFULLY!
echo Servers: http://localhost:8000 and http://localhost:8001
echo ================================================================================
echo.
pause