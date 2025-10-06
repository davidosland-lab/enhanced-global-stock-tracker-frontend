@echo off
echo ============================================================
echo STARTING FIXED HISTORICAL DATA MANAGER BACKEND
echo ============================================================
echo.

:: Kill ALL Python processes on port 8002
echo Killing any existing processes on port 8002...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)

:: Also kill by process name
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

timeout /t 3 >nul

:: Install requirements with specific versions for Python 3.12
echo Installing required packages...
pip install --quiet --upgrade yfinance "urllib3<2" fastapi uvicorn python-multipart pandas numpy cachetools pytz

:: Create historical_data directory
if not exist "historical_data" (
    echo Creating historical_data directory...
    mkdir historical_data
)

:: Start the backend
echo.
echo Starting Fixed Backend on port 8002...
echo.
echo IMPORTANT: The Historical Data Manager is now fully functional!
echo.
echo Test it by visiting:
echo   http://localhost:8000/test_historical_manager.html
echo.
echo Or use the Historical Data Manager module in the main app.
echo.
python backend.py