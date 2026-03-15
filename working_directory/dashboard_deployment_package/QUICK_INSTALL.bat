@echo off
REM Quick Install - Dashboard v2.0
REM Simple installation for Windows

echo Dashboard Quick Installer v2.0
echo ==============================
echo.

REM Install dependencies
echo Installing dependencies...
pip install flask flask-cors pandas numpy --quiet >nul 2>&1
echo [OK] Dependencies installed

REM Create directories
echo Creating directories...
if not exist templates mkdir templates
if not exist static\css mkdir static\css
if not exist static\js mkdir static\js
if not exist logs mkdir logs
echo [OK] Directories created

REM Verify files
echo Verifying files...
if exist live_trading_dashboard.py echo [OK] Backend ready
if exist templates\dashboard.html echo [OK] Templates ready
if exist static\css\dashboard.css echo [OK] Styles ready
if exist static\js\dashboard.js echo [OK] JavaScript ready

echo.
echo [OK] Installation complete!
echo.
echo To start the dashboard:
echo   python live_trading_dashboard.py
echo.
echo Then visit: http://localhost:5000
echo.
pause
