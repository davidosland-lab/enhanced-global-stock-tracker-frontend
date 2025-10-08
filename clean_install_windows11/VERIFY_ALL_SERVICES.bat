@echo off
title Stock Tracker Service Verification
color 0B

echo ================================================================================
echo                    STOCK TRACKER SERVICE VERIFICATION
echo ================================================================================
echo.
echo Checking all three required services...
echo.

set frontend_running=0
set backend_running=0
set ml_backend_running=0

:: Check Frontend (Port 8000)
echo [1/3] Checking Frontend Server (Port 8000)...
netstat -an | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo       ✓ Frontend is RUNNING on port 8000
    set frontend_running=1
    
    :: Test if it responds
    curl -s -o nul -w "       Response: %%{http_code}\n" http://localhost:8000/ 2>nul
) else (
    echo       ✗ Frontend is NOT RUNNING
    echo       To fix: Run "python -m http.server 8000" in the Stock Tracker folder
)

echo.

:: Check Main Backend (Port 8002)
echo [2/3] Checking Main Backend (Port 8002)...
netstat -an | findstr :8002 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo       ✓ Main Backend is RUNNING on port 8002
    set backend_running=1
    
    :: Test the API
    curl -s http://localhost:8002/ >test.tmp 2>nul
    if %errorlevel% == 0 (
        echo       ✓ API is responding
    )
    del test.tmp >nul 2>&1
) else (
    echo       ✗ Main Backend is NOT RUNNING
    echo       To fix: Run "python backend.py" in the Stock Tracker folder
)

echo.

:: Check ML Backend (Port 8003)
echo [3/3] Checking ML Backend (Port 8003)...
netstat -an | findstr :8003 | findstr LISTENING >nul 2>&1
if %errorlevel% == 0 (
    echo       ✓ ML Backend is RUNNING on port 8003
    set ml_backend_running=1
    
    :: Test the health endpoint
    curl -s http://localhost:8003/health >test.tmp 2>nul
    if %errorlevel% == 0 (
        echo       ✓ Health endpoint responding
    )
    del test.tmp >nul 2>&1
) else (
    echo       ✗ ML Backend is NOT RUNNING
    echo       To fix: Run "python backend_ml_enhanced.py" in the Stock Tracker folder
    echo.
    echo       This is why ML Training Centre shows "Disconnected"!
)

echo.
echo ================================================================================
echo                           SUMMARY
echo ================================================================================
echo.

:: Calculate total running
set /a total_running=%frontend_running%+%backend_running%+%ml_backend_running%

if %total_running% == 3 (
    echo ✓ ALL SERVICES ARE RUNNING!
    echo.
    echo You can access Stock Tracker at: http://localhost:8000
    echo.
    echo All features should be working, including ML Training Centre.
) else (
    echo ✗ SOME SERVICES ARE NOT RUNNING
    echo.
    echo You need all 3 services running for Stock Tracker to work properly.
    echo.
    echo Quick fix options:
    echo   1. Run INSTALL.bat to start everything
    echo   2. Run START_ALL_SERVICES_FIXED.bat
    echo   3. Manually start each missing service (see instructions above)
    echo.
    echo For ML Training Centre specifically:
    echo   - ML Backend MUST be running on port 8003
    echo   - Run START_ML_BACKEND_NOW.bat to start it
)

echo.
echo ================================================================================
echo                         FILE CHECK
echo ================================================================================
echo.
echo Checking required files in current directory...
echo.

if exist backend.py (
    echo    ✓ backend.py found
) else (
    echo    ✗ backend.py NOT FOUND
)

if exist backend_ml_enhanced.py (
    echo    ✓ backend_ml_enhanced.py found
) else (
    echo    ✗ backend_ml_enhanced.py NOT FOUND - ML Training Centre won't work!
)

if exist index.html (
    echo    ✓ index.html found
) else (
    echo    ✗ index.html NOT FOUND
)

echo.
echo Current directory: %cd%
echo.
pause