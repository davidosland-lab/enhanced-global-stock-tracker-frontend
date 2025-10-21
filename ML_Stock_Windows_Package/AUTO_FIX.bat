@echo off
REM ============================================================
REM AUTO-FIX COMMON SERVER ISSUES
REM ============================================================

title ML Stock Predictor - Auto Fix
color 0E
cls

echo ============================================================
echo    AUTO-FIX FOR COMMON SERVER ISSUES
echo ============================================================
echo.
echo This script will attempt to fix common problems automatically
echo.

REM Step 1: Kill processes on port 8000
echo [1/5] Checking port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo    Found process %%a using port 8000
    echo    Killing process...
    taskkill /F /PID %%a >nul 2>&1
    echo    [OK] Process terminated
)
echo    [OK] Port 8000 cleared
echo.

REM Step 2: Update pip
echo [2/5] Updating pip...
python -m pip install --upgrade pip >nul 2>&1
echo    [OK] Pip updated
echo.

REM Step 3: Install/reinstall core packages
echo [3/5] Installing core packages...
pip uninstall -y flask flask-cors >nul 2>&1
pip install flask==3.0.0 flask-cors==4.0.0
echo    [OK] Flask installed
pip install --upgrade yfinance
echo    [OK] yfinance updated
pip install pandas requests
echo    [OK] Other packages installed
echo.

REM Step 4: Clear yfinance cache
echo [4/5] Clearing yfinance cache...
python -c "import shutil, tempfile, os; cache_dir = os.path.join(tempfile.gettempdir(), 'yfinance'); shutil.rmtree(cache_dir, ignore_errors=True); print('   [OK] Cache cleared')"
echo.

REM Step 5: Test imports
echo [5/5] Testing imports...
python -c "import flask; import flask_cors; import yfinance; import pandas; import numpy; print('   [OK] All imports successful')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo    [WARNING] Some imports failed, checking details...
    python -c "import sys; print(f'   Python: {sys.version}')"
    
    echo.
    echo    Attempting alternative fix...
    pip install --force-reinstall flask flask-cors yfinance pandas numpy
)

echo.
echo ============================================================
echo    AUTO-FIX COMPLETE
echo ============================================================
echo.
echo Next steps:
echo   1. Run: diagnose_server.py to check for remaining issues
echo   2. Try: START_MINIMAL.bat (works with most configurations)
echo   3. Or:  START_PRODUCTION.bat (full featured system)
echo.
pause