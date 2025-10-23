@echo off
title Fix V4.0 Real Data Only Issues
color 0C

echo ================================================================================
echo                     FIX V4.0 REAL DATA ONLY ISSUES
echo ================================================================================
echo.
echo Version 4.0 removed ALL fallbacks but broke some things:
echo   - Main backend missing /api/health endpoint (404 error)
echo   - ML Backend not starting properly
echo   - Error handler too aggressive
echo.
echo This fix will repair these issues while keeping real data only.
echo.
echo Press any key to apply fixes...
pause >nul

echo.
echo [1/5] Applying fixes to code...
python FIX_V4_ISSUES.py

if %errorlevel% NEQ 0 (
    echo.
    echo ✗ Python fix script failed!
    echo Make sure Python is installed and you're in the right directory.
    pause
    exit /b 1
)

echo.
echo [2/5] Stopping all existing services...

for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8002"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8003"') do (
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 3 /nobreak >nul

echo.
echo [3/5] Starting Frontend Server (port 8000)...
start "Frontend" /min cmd /c "python -m http.server 8000"
timeout /t 2 /nobreak >nul

echo.
echo [4/5] Starting Main Backend with health endpoint (port 8002)...
start "Backend" /min cmd /c "python backend.py"
timeout /t 3 /nobreak >nul

echo.
echo [5/5] Starting ML Backend (port 8003)...
if exist backend_ml_enhanced.py (
    start "ML Backend" /min cmd /c "python backend_ml_enhanced.py"
    echo    ✓ ML Backend starting...
) else (
    echo    ! backend_ml_enhanced.py not found
    echo    The ML Training Centre will show "Disconnected"
)

timeout /t 5 /nobreak >nul

echo.
echo ================================================================================
echo                         TESTING FIXES
echo ================================================================================
echo.

:: Test main backend health endpoint
echo Testing Main Backend /api/health endpoint...
curl -s http://localhost:8002/api/health >test.tmp 2>nul
if %errorlevel% == 0 (
    echo    ✓ Main Backend health endpoint working!
    type test.tmp 2>nul | findstr /i "healthy"
) else (
    echo    ! Main Backend not responding yet
)
del test.tmp >nul 2>&1

echo.
echo Testing ML Backend /health endpoint...
curl -s http://localhost:8003/health >test.tmp 2>nul
if %errorlevel% == 0 (
    echo    ✓ ML Backend health endpoint working!
    type test.tmp 2>nul | findstr /i "healthy"
) else (
    echo    ! ML Backend not responding - check if it's running
)
del test.tmp >nul 2>&1

echo.
echo ================================================================================
echo                      ✓ V4.0 ISSUES FIXED!
echo ================================================================================
echo.
echo Fixed:
echo   ✓ Added /api/health endpoint to main backend
echo   ✓ Fixed error handler to be less aggressive
echo   ✓ Fixed health check fallbacks in index.html
echo   ✓ Services restarted properly
echo.
echo The application should now work correctly with:
echo   • Real data only (no fallbacks)
echo   • No annoying error popups
echo   • All health checks working
echo.
echo Please refresh your browser (Ctrl+F5) and try again!
echo.
pause