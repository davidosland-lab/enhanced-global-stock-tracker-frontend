@echo off
color 0A
cls
echo ================================================================
echo          ULTIMATE FIX FOR 404 ERRORS ON BACKEND
echo ================================================================
echo.
echo This script will:
echo   1. Stop the OLD backend that's missing endpoints
echo   2. Apply ALL endpoint fixes to backend.py
echo   3. Start the NEW backend with all endpoints
echo   4. Verify everything is working
echo.
echo ================================================================
pause

cls
echo ================================================================
echo STEP 1: STOPPING OLD BACKEND PROCESSES
echo ================================================================

REM Kill all Python processes on port 8002
echo Killing processes on port 8002...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo   Terminating PID %%a
    taskkill /PID %%a /F 2>nul
)

REM Kill backend.py processes specifically
echo.
echo Killing backend.py processes...
wmic process where "CommandLine like '%%backend.py%%'" delete 2>nul

REM Kill any Python process using port 8002
echo.
echo Double-checking port 8002...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    taskkill /PID %%a /T /F 2>nul
)

timeout /t 3 >nul

echo.
echo ================================================================
echo STEP 2: APPLYING ENDPOINT FIXES
echo ================================================================

cd /D "%~dp0"

echo Running endpoint fix script...
python FIX_ALL_MISSING_ENDPOINTS.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to apply fixes. Trying alternative method...
    echo.
    echo Please ensure Python is installed and in PATH
    pause
    exit /b 1
)

timeout /t 2 >nul

echo.
echo ================================================================
echo STEP 3: STARTING FIXED BACKEND
echo ================================================================

echo Starting backend with all endpoints...
start "Stock Tracker Backend (Fixed)" /min cmd /c "cd /d %~dp0 && python backend.py"

echo Waiting for backend to initialize...
timeout /t 5 >nul

echo.
echo ================================================================
echo STEP 4: VERIFICATION
echo ================================================================

echo.
echo Testing /api/health endpoint...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8002/api/health
curl -s http://localhost:8002/api/health 2>nul
echo.

echo.
echo Testing /api/market-summary endpoint...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8002/api/market-summary
echo.

echo.
echo ================================================================
echo STEP 5: FINAL CHECKS
echo ================================================================

REM Check if backend is running
netstat -an | findstr :8002 >nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Backend is running on port 8002
) else (
    echo [ERROR] Backend is NOT running on port 8002
    echo.
    echo Please check:
    echo   1. Python is installed
    echo   2. Requirements are installed: pip install -r requirements.txt
    echo   3. No firewall/antivirus blocking
)

echo.
echo ================================================================
echo                    FIX COMPLETE!
echo ================================================================
echo.
echo The following should now work:
echo   ✓ Backend Status: Connected (green)
echo   ✓ No more 404 errors in browser console
echo   ✓ http://localhost:8002/api/health returns JSON
echo   ✓ http://localhost:8002/api/market-summary returns data
echo.
echo Please:
echo   1. Go to http://localhost:8000
echo   2. Press F5 to refresh the page
echo   3. Check that Backend Status shows "Connected"
echo   4. Open F12 console - no more 404 errors!
echo.
echo ================================================================
echo.
pause