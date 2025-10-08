@echo off
cls
echo ============================================================
echo Fixing "Backend API Disconnected" Issue
echo ============================================================
echo.

echo Step 1: Checking if Backend is running on port 8002...
netstat -an | findstr :8002 | findstr LISTENING >nul
if errorlevel 1 (
    echo   [NOT RUNNING] Backend is not running on port 8002
    goto :start_backend
) else (
    echo   [RUNNING] Backend is listening on port 8002
    goto :test_backend
)

:test_backend
echo.
echo Step 2: Testing Backend connection...
curl -s http://localhost:8002/api/health >nul 2>&1
if errorlevel 1 (
    echo   [FAILED] Backend is not responding properly
    goto :restart_backend
) else (
    echo   [OK] Backend is responding
    curl -s http://localhost:8002/api/health
    echo.
    goto :check_cors
)

:check_cors
echo.
echo Step 3: Backend is running but browser shows disconnected.
echo This is usually a CORS or browser cache issue.
echo.
echo Solutions:
echo.
echo 1. Clear Browser Cache:
echo    - Press Ctrl+Shift+Delete in your browser
echo    - Clear cached images and files
echo    - Refresh the page (F5)
echo.
echo 2. Try a Different Browser:
echo    - Chrome, Firefox, or Edge
echo.
echo 3. Check Windows Firewall:
echo    - May be blocking localhost connections
echo.
echo 4. Open Developer Console (F12) and check for errors
echo.
goto :end

:restart_backend
echo.
echo Step 3: Restarting Backend...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

:start_backend
echo.
echo Starting Backend API on port 8002...
if exist backend.py (
    start "Backend API" cmd /k "python backend.py"
) else if exist backend_working_before_ml_fix.py (
    copy backend_working_before_ml_fix.py backend.py /Y
    start "Backend API" cmd /k "python backend.py"
) else (
    echo ERROR: No backend.py found!
    echo Please ensure backend.py exists in the current directory.
    pause
    exit /b 1
)

timeout /t 5 /nobreak >nul

echo.
echo Testing new Backend connection...
curl -s http://localhost:8002/api/health >nul 2>&1
if errorlevel 1 (
    echo   [FAILED] Backend still not responding
    echo.
    echo Possible issues:
    echo   - Python not installed or not in PATH
    echo   - Missing packages (run INSTALL_REQUIREMENTS.bat)
    echo   - Port 8002 blocked by firewall
    echo   - Another application using port 8002
    echo.
) else (
    echo   [SUCCESS] Backend is now running!
    echo.
    curl -s http://localhost:8002/api/health
    echo.
    echo.
    echo ✅ Backend Fixed!
    echo.
    echo Now refresh your browser (F5) at http://localhost:8000
    echo The "Backend API Disconnected" message should be gone.
)

:end
echo.
echo ============================================================
echo Additional Debugging
echo ============================================================
echo.
echo To test the connection manually:
echo 1. Open: TEST_BACKEND_CONNECTION.html in your browser
echo 2. Click "Test All Connections"
echo 3. Check which endpoints are working
echo.
echo If backend is running but still shows disconnected:
echo - It's likely a browser issue (try incognito mode)
echo - Or CORS is being blocked (check browser console)
echo.
pause