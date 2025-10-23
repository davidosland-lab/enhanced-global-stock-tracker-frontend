@echo off
cls
echo ============================================================
echo ML Backend Port 8003 - Complete Diagnostic
echo ============================================================
echo.
date /t
time /t
echo.

echo Step 1: Checking what's using port 8003...
echo ------------------------------------------------------------
netstat -an | findstr :8003
echo.
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    echo Found process on port 8003 with PID: %%a
    echo Process details:
    tasklist /FI "PID eq %%a" 2>nul
    echo.
)

echo Step 2: Killing any process on port 8003...
echo ------------------------------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    echo Killing PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo Port 8003 should now be free.
echo.

echo Step 3: Checking Python and required packages...
echo ------------------------------------------------------------
python --version 2>nul || echo ERROR: Python not found in PATH!
echo.

echo Checking required packages:
python -c "import fastapi; print('  [OK] FastAPI version:', fastapi.__version__)" 2>nul || echo  [MISSING] FastAPI - Run: pip install fastapi
python -c "import uvicorn; print('  [OK] Uvicorn installed')" 2>nul || echo  [MISSING] Uvicorn - Run: pip install uvicorn
python -c "import pydantic; print('  [OK] Pydantic installed')" 2>nul || echo  [MISSING] Pydantic - Run: pip install pydantic
python -c "import yfinance; print('  [OK] yfinance installed')" 2>nul || echo  [WARNING] yfinance - Run: pip install yfinance
python -c "import pandas; print('  [OK] pandas installed')" 2>nul || echo  [WARNING] pandas - Run: pip install pandas
python -c "import numpy; print('  [OK] numpy installed')" 2>nul || echo  [WARNING] numpy - Run: pip install numpy
echo.

echo Step 4: Checking which ML backend files exist...
echo ------------------------------------------------------------
if exist ml_backend_working.py (
    echo  [FOUND] ml_backend_working.py - 7KB
    python -m py_compile ml_backend_working.py 2>nul && echo  [OK] No syntax errors || echo  [ERROR] Syntax errors found!
)
if exist ml_backend_simple.py (
    echo  [FOUND] ml_backend_simple.py - 2KB
    python -m py_compile ml_backend_simple.py 2>nul && echo  [OK] No syntax errors || echo  [ERROR] Syntax errors found!
)
if exist ml_backend_v2.py (
    echo  [FOUND] ml_backend_v2.py - 14KB
    python -m py_compile ml_backend_v2.py 2>nul && echo  [OK] No syntax errors || echo  [ERROR] Syntax errors found!
)
if exist ml_backend_minimal.py (
    echo  [FOUND] ml_backend_minimal.py - 5KB
    python -m py_compile ml_backend_minimal.py 2>nul && echo  [OK] No syntax errors || echo  [ERROR] Syntax errors found!
)
echo.

echo Step 5: Testing ML Backend startup...
echo ------------------------------------------------------------
echo Trying to start ML Backend in test mode...
echo (A new window will open - check for error messages)
echo.

REM Try each ML backend until one works
if exist ml_backend_simple.py (
    echo Attempting ml_backend_simple.py...
    start "ML Backend Test" cmd /c "python ml_backend_simple.py 2>&1 | more && pause"
    goto :wait
)

if exist ml_backend_minimal.py (
    echo Attempting ml_backend_minimal.py...
    start "ML Backend Test" cmd /c "python ml_backend_minimal.py 2>&1 | more && pause"
    goto :wait
)

if exist ml_backend_working.py (
    echo Attempting ml_backend_working.py...
    start "ML Backend Test" cmd /c "python ml_backend_working.py 2>&1 | more && pause"
    goto :wait
)

if exist ml_backend_v2.py (
    echo Attempting ml_backend_v2.py...
    start "ML Backend Test" cmd /c "python ml_backend_v2.py 2>&1 | more && pause"
    goto :wait
)

echo ERROR: No ML backend files found!
goto :end

:wait
echo Waiting for ML Backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 6: Testing ML Backend connection...
echo ------------------------------------------------------------
curl -s http://localhost:8003/health >nul 2>&1
if errorlevel 1 (
    echo [FAILED] ML Backend is NOT responding on port 8003
    echo.
    echo Possible issues:
    echo 1. Missing Python packages (install with pip)
    echo 2. Python script has errors (check the test window)
    echo 3. Firewall blocking port 8003
    echo 4. Another program using port 8003
) else (
    echo [SUCCESS] ML Backend is responding!
    echo.
    echo Testing endpoints:
    curl -s http://localhost:8003/health
    echo.
    curl -s http://localhost:8003/api/ml/status 2>nul
    echo.
)

:end
echo.
echo ============================================================
echo Diagnostic Summary
echo ============================================================
echo.
echo If ML Backend won't start, try these solutions:
echo.
echo 1. Install all required packages:
echo    pip install fastapi uvicorn pydantic
echo.
echo 2. Try the simplest backend first:
echo    python ml_backend_simple.py
echo.
echo 3. Check Windows Firewall:
echo    - Add exception for port 8003
echo    - Or temporarily disable firewall for testing
echo.
echo 4. Check the error messages in the test window
echo.
pause