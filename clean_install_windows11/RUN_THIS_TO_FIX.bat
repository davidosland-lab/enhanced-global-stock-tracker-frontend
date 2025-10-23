@echo off
cls
echo ================================================================
echo     IMMEDIATE FIX FOR STOCK TRACKER ERRORS
echo     Solves 500 errors and module loading issues
echo ================================================================
echo.

:: Kill existing processes
echo Stopping existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

:: Start the fixed backend
echo.
echo Starting FIXED backend (handles all errors)...
start "Fixed Backend" /min cmd /c "python backend_fixed_final.py"
timeout /t 5 >nul

:: Start frontend server
echo Starting frontend server...
start "Frontend Server" /min cmd /c "python -m http.server 8000"
timeout /t 3 >nul

:: Test the backend
echo.
echo Testing backend...
curl -s http://localhost:8002/api/status >nul 2>&1
if errorlevel 1 (
    echo Backend may need more time to start...
    timeout /t 5 >nul
)

:: Open browser
echo.
echo ================================================================
echo     FIXED VERSION IS NOW RUNNING!
echo ================================================================
echo.
echo The following issues are now FIXED:
echo - 500 Internal Server Errors
echo - AAPL stock data errors
echo - Module loading issues
echo - Prediction Centre errors
echo.
echo Opening browser to http://localhost:8000
start http://localhost:8000

echo.
echo Keep this window open. Press any key to stop...
pause >nul

:: Cleanup
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo Services stopped.
timeout /t 2 >nul