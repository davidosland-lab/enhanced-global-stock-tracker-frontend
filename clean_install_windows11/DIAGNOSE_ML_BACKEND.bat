@echo off
title ML Backend Diagnostic Tool
color 0E

echo ================================================================================
echo                      ML BACKEND DIAGNOSTIC TOOL
echo ================================================================================
echo.
echo This will diagnose why ML Training Centre shows:
echo "GET http://localhost:8003/health net::ERR_CONNECTION_REFUSED"
echo.
echo Starting diagnostics...
echo.
echo ================================================================================

echo.
echo [1] Checking Python Installation...
echo --------------------------------------------------------------------------------
python --version 2>nul
if %errorlevel% == 0 (
    echo    ✓ Python is installed
    python --version
) else (
    echo    ✗ Python is NOT installed or not in PATH
    echo.
    echo    SOLUTION: Install Python 3.8 or higher from python.org
    goto :end
)

echo.
echo [2] Checking Current Directory...
echo --------------------------------------------------------------------------------
echo    Current directory: %cd%
echo.
echo    Checking for required files:

if exist backend_ml_enhanced.py (
    echo    ✓ backend_ml_enhanced.py found
) else (
    echo    ✗ backend_ml_enhanced.py NOT FOUND
    echo.
    echo    SOLUTION: Make sure you extracted ALL files from the zip
)

if exist backend.py (
    echo    ✓ backend.py found
) else (
    echo    ✗ backend.py NOT FOUND
)

if exist index.html (
    echo    ✓ index.html found
) else (
    echo    ✗ index.html NOT FOUND
)

echo.
echo [3] Checking Port 8003 Status...
echo --------------------------------------------------------------------------------
netstat -an | findstr :8003 >temp.txt 2>&1
if %errorlevel% == 0 (
    echo    Port 8003 status:
    type temp.txt
    echo.
    
    netstat -an | findstr :8003 | findstr LISTENING >nul 2>&1
    if %errorlevel% == 0 (
        echo    ✓ Something is LISTENING on port 8003
        
        :: Find what process
        for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
            echo    Process ID using port 8003: %%a
            
            :: Get process name
            for /f "tokens=1" %%b in ('tasklist ^| findstr %%a') do (
                echo    Process name: %%b
            )
        )
    ) else (
        echo    ✗ Nothing is LISTENING on port 8003
        echo.
        echo    SOLUTION: The ML Backend is not running. Start it with:
        echo    python backend_ml_enhanced.py
    )
) else (
    echo    ✓ Port 8003 is FREE (not in use)
    echo.
    echo    SOLUTION: Start the ML Backend with:
    echo    python backend_ml_enhanced.py
)
del temp.txt >nul 2>&1

echo.
echo [4] Testing ML Backend Connectivity...
echo --------------------------------------------------------------------------------

:: Try to connect to ML Backend
curl -s http://localhost:8003/health >response.txt 2>error.txt

if %errorlevel% == 0 (
    echo    ✓ ML Backend is RESPONDING!
    echo.
    echo    Response from /health endpoint:
    type response.txt
    echo.
) else (
    echo    ✗ Cannot connect to ML Backend
    echo.
    echo    Error details:
    type error.txt 2>nul
    echo.
    echo    COMMON CAUSES:
    echo    1. ML Backend is not running
    echo    2. Windows Firewall is blocking port 8003
    echo    3. Antivirus is blocking Python
)
del response.txt >nul 2>&1
del error.txt >nul 2>&1

echo.
echo [5] Checking Required Python Packages...
echo --------------------------------------------------------------------------------

python -c "import fastapi" 2>nul
if %errorlevel% == 0 (
    echo    ✓ fastapi installed
) else (
    echo    ✗ fastapi NOT installed - run: pip install fastapi
)

python -c "import uvicorn" 2>nul
if %errorlevel% == 0 (
    echo    ✓ uvicorn installed
) else (
    echo    ✗ uvicorn NOT installed - run: pip install uvicorn
)

python -c "import yfinance" 2>nul
if %errorlevel% == 0 (
    echo    ✓ yfinance installed
) else (
    echo    ✗ yfinance NOT installed - run: pip install yfinance
)

echo.
echo [6] Testing Direct Python Execution...
echo --------------------------------------------------------------------------------
echo.
echo    Attempting to start ML Backend directly...
echo    (If it starts successfully, press Ctrl+C to stop)
echo.

timeout /t 3 /nobreak >nul

if exist backend_ml_enhanced.py (
    echo    Running: python backend_ml_enhanced.py
    echo.
    echo    Watch for any error messages below:
    echo    ----------------------------------------
    python backend_ml_enhanced.py 2>&1 | findstr /N "^" | head -20
) else (
    echo    Cannot test - backend_ml_enhanced.py not found
)

:end
echo.
echo ================================================================================
echo                        DIAGNOSTIC COMPLETE
echo ================================================================================
echo.
echo QUICK FIX STEPS:
echo   1. Run: pip install fastapi uvicorn yfinance pandas numpy
echo   2. Run: python backend_ml_enhanced.py
echo   3. Refresh browser and check ML Training Centre
echo.
echo If still having issues:
echo   - Check Windows Firewall settings for port 8003
echo   - Run as Administrator
echo   - Disable antivirus temporarily for testing
echo.
pause