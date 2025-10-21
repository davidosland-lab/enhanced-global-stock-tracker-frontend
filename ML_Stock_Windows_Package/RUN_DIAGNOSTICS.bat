@echo off
REM ============================================================
REM COMPREHENSIVE SERVER DIAGNOSTICS
REM ============================================================

title ML Stock Predictor - Diagnostics
color 0E
cls

echo ============================================================
echo    COMPREHENSIVE SERVER DIAGNOSTICS
echo ============================================================
echo.
echo This will run multiple diagnostic tests to find issues
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ❌ CRITICAL ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from https://python.org
    echo During installation, make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ============================================
echo STEP 1: System Information
echo ============================================
echo.
echo Python version:
python --version
echo.
echo Current directory:
cd
echo.
echo Python location:
where python
echo.

echo ============================================
echo STEP 2: Running Diagnostic Tool
echo ============================================
echo.
python diagnose_server.py

echo.
echo ============================================
echo STEP 3: Quick Port Check
echo ============================================
echo.
echo Checking what's using port 8000...
netstat -ano | findstr :8000
echo.
echo If you see a process above, you can kill it with:
echo   taskkill /F /PID [number]
echo.

echo ============================================
echo STEP 4: Test Server Attempt
echo ============================================
echo.
echo Trying to start the test server...
echo (Press Ctrl+C to stop if it starts)
echo.
timeout /t 3 /nobreak >nul
python test_server.py

echo.
echo ============================================
echo DIAGNOSTIC COMPLETE
echo ============================================
echo.
echo Review the output above to identify issues.
echo.
echo Common solutions:
echo   1. Run AUTO_FIX.bat to fix common issues
echo   2. Kill processes using port 8000
echo   3. Install missing packages with pip
echo   4. Use server_minimal.py if you have NumPy issues
echo.
pause