@echo off
echo ========================================================
echo FORCE RESTART BACKEND WITH HEALTH ENDPOINT FIX
echo ========================================================
echo.
color 0A

echo [STEP 1] Forcefully killing ALL Python processes on port 8002...
echo --------------------------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo Killing process %%a
    taskkill /PID %%a /F 2>nul
    timeout /t 1 >nul
)

echo.
echo [STEP 2] Double-check - Kill any remaining backend processes...
echo --------------------------------------------------------
wmic process where "CommandLine like '%%backend.py%%'" delete 2>nul
wmic process where "CommandLine like '%%backend%%' and CommandLine like '%%8002%%'" delete 2>nul

echo.
echo [STEP 3] Wait for port to be fully released...
echo --------------------------------------------------------
timeout /t 3

echo.
echo [STEP 4] Verify port 8002 is now free...
echo --------------------------------------------------------
netstat -an | findstr :8002
if %ERRORLEVEL% EQU 0 (
    echo WARNING: Port 8002 may still be in use!
    echo Trying alternative kill method...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
        taskkill /PID %%a /T /F 2>nul
    )
    timeout /t 3
) else (
    echo SUCCESS: Port 8002 is free
)

echo.
echo [STEP 5] Starting NEW backend with health endpoint fix...
echo --------------------------------------------------------
cd /D "%~dp0"
start "Stock Tracker Backend API (Port 8002)" cmd /k "python backend.py"

echo.
echo [STEP 6] Waiting for backend to initialize...
echo --------------------------------------------------------
timeout /t 5

echo.
echo [STEP 7] Testing the health endpoint...
echo --------------------------------------------------------
curl -i http://localhost:8002/api/health
echo.
echo.

if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo SUCCESS! Backend is running with health endpoint
    echo ========================================================
    echo.
    echo The "Backend Status: Disconnected" issue should be fixed!
    echo.
    echo Please refresh your browser at http://localhost:8000
    echo The Backend Status should now show "Connected"
) else (
    echo ========================================================
    echo WARNING: Health endpoint test failed
    echo ========================================================
    echo.
    echo Please check:
    echo 1. Python is installed and in PATH
    echo 2. All requirements are installed (pip install -r requirements.txt)
    echo 3. No antivirus is blocking Python
    echo.
    echo Try running manually:
    echo   python backend.py
)

echo.
echo Press any key to close...
pause >nul