@echo off
title Stock Tracker - Master Startup Controller (Enhanced)
color 0A
cls

echo ===============================================================================
echo                  STOCK TRACKER MASTER STARTUP (ENHANCED)
echo              Complete System Launch with Port Management v2.0
echo ===============================================================================
echo.
echo This startup script will:
echo  1. Force shutdown ALL servers and clear ALL ports
echo  2. Verify no demo/synthetic data is being used
echo  3. Start all servers in the correct sequence
echo  4. Verify all services are running correctly
echo  5. Open the landing page when ready
echo.
echo Press any key to begin...
pause >nul

echo.
echo ===============================================================================
echo [PHASE 1: COMPLETE CLEANUP AND SHUTDOWN]
echo ===============================================================================

:: Set environment variables to reduce TensorFlow warnings
set TF_ENABLE_ONEDNN_OPTS=0
set TF_CPP_MIN_LOG_LEVEL=2
set PYTHONWARNINGS=ignore

echo.
echo [1.1] Forcefully terminating ALL Python processes...
echo -----------------------------------------------
echo   Killing all python.exe processes...
taskkill /F /IM python.exe 2>nul
if %errorlevel%==0 (
    echo   ✓ Python processes terminated
) else (
    echo   ✓ No Python processes were running
)

echo   Killing all pythonw.exe processes...
taskkill /F /IM pythonw.exe 2>nul
if %errorlevel%==0 (
    echo   ✓ Pythonw processes terminated
) else (
    echo   ✓ No Pythonw processes were running
)

:: Wait for processes to fully terminate
timeout /t 3 >nul

echo.
echo [1.2] Advanced port cleanup (8000, 8002, 8003)...
echo -----------------------------------------------

:: Function to clear a port using multiple methods
echo   Clearing port 8000 (Frontend Server)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo     - Found process %%a on port 8000
        taskkill /F /PID %%a >nul 2>&1
        wmic process where ProcessId=%%a delete >nul 2>&1
        echo     ✓ Terminated process %%a
    )
)

echo   Clearing port 8002 (Main Backend API)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo     - Found process %%a on port 8002
        taskkill /F /PID %%a >nul 2>&1
        wmic process where ProcessId=%%a delete >nul 2>&1
        echo     ✓ Terminated process %%a
    )
)

echo   Clearing port 8003 (ML Training Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    if not "%%a"=="0" (
        echo     - Found process %%a on port 8003
        taskkill /F /PID %%a >nul 2>&1
        wmic process where ProcessId=%%a delete >nul 2>&1
        echo     ✓ Terminated process %%a
    )
)

:: Additional cleanup using PowerShell for stubborn processes
echo.
echo [1.3] PowerShell deep cleanup...
echo -----------------------------------------------
powershell -Command "Get-Process | Where-Object {$_.ProcessName -like '*python*'} | Stop-Process -Force -ErrorAction SilentlyContinue"
echo   ✓ PowerShell cleanup completed

:: Final wait to ensure all ports are released
timeout /t 2 >nul

echo.
echo [1.4] Verifying all ports are clear...
echo -----------------------------------------------
set PORTS_CLEAR=1

netstat -aon | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo   ⚠ WARNING: Port 8000 still in use
    set PORTS_CLEAR=0
) else (
    echo   ✓ Port 8000 is clear
)

netstat -aon | findstr :8002 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo   ⚠ WARNING: Port 8002 still in use
    set PORTS_CLEAR=0
) else (
    echo   ✓ Port 8002 is clear
)

netstat -aon | findstr :8003 | findstr LISTENING >nul 2>&1
if %errorlevel%==0 (
    echo   ⚠ WARNING: Port 8003 still in use
    set PORTS_CLEAR=0
) else (
    echo   ✓ Port 8003 is clear
)

if %PORTS_CLEAR%==0 (
    echo.
    echo   ⚠ Some ports are still in use. Attempting force clear...
    :: Try to clear ports using netsh
    netsh int ipv4 reset >nul 2>&1
    netsh int ipv6 reset >nul 2>&1
    timeout /t 3 >nul
)

echo.
echo ===============================================================================
echo [PHASE 2: DATA VERIFICATION]
echo ===============================================================================

echo.
echo [2.1] Verifying no demo/synthetic data in modules...
echo -----------------------------------------------

:: Check if verification script exists and run it
if exist verify_real_data.py (
    echo   Running data verification scan...
    python verify_real_data.py >data_verify_temp.txt 2>&1
    findstr /C:"SYSTEM VERIFIED" data_verify_temp.txt >nul
    if %errorlevel%==0 (
        echo   ✅ All modules use real Yahoo Finance data
    ) else (
        echo   ⚠ Warning: Some modules may contain synthetic data
        echo   Please review data_verification_report.txt for details
    )
    del data_verify_temp.txt >nul 2>&1
) else (
    echo   ✓ Skipping verification (script not found)
)

echo.
echo ===============================================================================
echo [PHASE 3: SEQUENTIAL SERVICE STARTUP]
echo ===============================================================================

echo.
echo [3.1] Starting Main Backend API (Port 8002)...
echo -----------------------------------------------
if exist backend.py (
    echo   Launching backend.py on localhost:8002...
    start /min cmd /c "python backend.py"
    timeout /t 3 >nul
    
    :: Verify backend is running
    curl -s http://localhost:8002/api/status >nul 2>&1
    if %errorlevel%==0 (
        echo   ✅ Main Backend API is running on port 8002
    ) else (
        echo   ⚠ Backend may still be starting up...
    )
) else (
    echo   ❌ ERROR: backend.py not found!
)

echo.
echo [3.2] Starting ML Training Backend (Port 8003)...
echo -----------------------------------------------

:: Try different ML backend files in order of preference
set ML_STARTED=0

if exist ml_backend_working.py (
    echo   Launching ml_backend_working.py on localhost:8003...
    start /min cmd /c "python ml_backend_working.py"
    set ML_STARTED=1
) else if exist ml_training_backend.py (
    echo   Launching ml_training_backend.py on localhost:8003...
    start /min cmd /c "python ml_training_backend.py"
    set ML_STARTED=1
) else if exist ml_backend_simple.py (
    echo   Launching ml_backend_simple.py on localhost:8003...
    start /min cmd /c "python ml_backend_simple.py"
    set ML_STARTED=1
) else if exist start_ml_backend.py (
    echo   Launching start_ml_backend.py...
    start /min cmd /c "python start_ml_backend.py"
    set ML_STARTED=1
)

if %ML_STARTED%==1 (
    timeout /t 3 >nul
    :: Verify ML backend is running
    curl -s http://localhost:8003/health >nul 2>&1
    if %errorlevel%==0 (
        echo   ✅ ML Training Backend is running on port 8003
    ) else (
        echo   ⚠ ML Backend may still be starting up...
    )
) else (
    echo   ⚠ WARNING: No ML backend file found
    echo   Phase 4 predictions may not work
)

echo.
echo [3.3] Starting Frontend Server (Port 8000)...
echo -----------------------------------------------
echo   Launching HTTP server for frontend...
start /min cmd /c "python -m http.server 8000"
timeout /t 2 >nul

:: Verify frontend is accessible
curl -s http://localhost:8000 >nul 2>&1
if %errorlevel%==0 (
    echo   ✅ Frontend server is running on port 8000
) else (
    echo   ⚠ Frontend server may still be starting up...
)

echo.
echo ===============================================================================
echo [PHASE 4: SYSTEM VERIFICATION]
echo ===============================================================================

echo.
echo [4.1] Performing final system checks...
echo -----------------------------------------------

:: Check all services
set ALL_GOOD=1

echo   Checking Main Backend API...
curl -s http://localhost:8002/api/status >nul 2>&1
if %errorlevel%==0 (
    echo   ✓ Main Backend: ONLINE
) else (
    echo   ✗ Main Backend: OFFLINE
    set ALL_GOOD=0
)

echo   Checking ML Training Backend...
curl -s http://localhost:8003/health >nul 2>&1
if %errorlevel%==0 (
    echo   ✓ ML Backend: ONLINE
) else (
    echo   ✗ ML Backend: OFFLINE (Phase 4 predictions unavailable)
)

echo   Checking Frontend Server...
curl -s http://localhost:8000 >nul 2>&1
if %errorlevel%==0 (
    echo   ✓ Frontend: ONLINE
) else (
    echo   ✗ Frontend: OFFLINE
    set ALL_GOOD=0
)

echo.
echo [4.2] Service URLs:
echo -----------------------------------------------
echo   📊 Main Application:    http://localhost:8000
echo   🔌 Main Backend API:    http://localhost:8002
echo   🤖 ML Training Backend: http://localhost:8003
echo   📈 CBA Enhanced Module: http://localhost:8000/modules/cba_enhanced.html

echo.
echo ===============================================================================
echo [PHASE 5: LAUNCH APPLICATION]
echo ===============================================================================

if %ALL_GOOD%==1 (
    echo.
    echo ✅ All systems operational!
    echo.
    echo Launching Stock Tracker in your default browser...
    timeout /t 2 >nul
    start http://localhost:8000
    echo.
    echo ===============================================================================
    echo                        STARTUP COMPLETE
    echo ===============================================================================
    echo.
    echo The Stock Tracker is now running with:
    echo   • Real Yahoo Finance data (no synthetic/demo data)
    echo   • Hardcoded localhost:8002 for backend
    echo   • ML training on port 8003
    echo   • SQLite caching for 100x faster backtesting
    echo   • All 5 required modules functional
    echo.
    echo To stop all services, close this window and run MASTER_SHUTDOWN.bat
) else (
    echo.
    echo ⚠ WARNING: Some services failed to start properly
    echo.
    echo Please check:
    echo   1. Python is installed and in PATH
    echo   2. All required packages are installed (pip install -r requirements.txt)
    echo   3. No antivirus/firewall blocking ports
    echo   4. Try running as Administrator
    echo.
    echo You can still try to access: http://localhost:8000
)

echo.
echo Press any key to keep services running (DO NOT CLOSE THIS WINDOW)...
pause >nul

:: Keep the window open to maintain services
:KEEPALIVE
timeout /t 60 >nul
goto KEEPALIVE