@echo off
cls
echo ============================================================
echo ML Backend (Port 8003) Diagnostic Tool
echo ============================================================
echo.
echo This will help diagnose why the ML backend won't start.
echo.

echo Step 1: Checking if port 8003 is in use...
echo ----------------------------------------
netstat -an | findstr :8003
echo.
echo If you see LISTENING above, something is already using port 8003.
echo.

echo Step 2: Trying to kill any process on port 8003...
echo ----------------------------------------
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do (
    echo Killing process PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)
echo.

echo Step 3: Testing Python imports...
echo ----------------------------------------
python -c "import fastapi; print('✓ FastAPI installed')" 2>nul || echo ✗ FastAPI not installed - Run: pip install fastapi
python -c "import uvicorn; print('✓ Uvicorn installed')" 2>nul || echo ✗ Uvicorn not installed - Run: pip install uvicorn
python -c "import yfinance; print('✓ yfinance installed')" 2>nul || echo ✗ yfinance not installed - Run: pip install yfinance
python -c "import pandas; print('✓ pandas installed')" 2>nul || echo ✗ pandas not installed - Run: pip install pandas
python -c "import numpy; print('✓ numpy installed')" 2>nul || echo ✗ numpy not installed - Run: pip install numpy
echo.

echo Step 4: Testing ml_backend_v2.py syntax...
echo ----------------------------------------
python -m py_compile ml_backend_v2.py 2>&1 && (
    echo ✓ ml_backend_v2.py has no syntax errors
) || (
    echo ✗ ml_backend_v2.py has syntax errors:
    python -m py_compile ml_backend_v2.py 2>&1
)
echo.

echo Step 5: Attempting to start ML Backend...
echo ----------------------------------------
echo Starting ml_backend_v2.py in a new window...
echo (Close the new window if it opens and stays blank)
echo.
start "ML Backend Test" cmd /k "python ml_backend_v2.py 2>&1 || pause"

timeout /t 5 /nobreak >nul

echo.
echo Step 6: Checking if ML Backend started...
echo ----------------------------------------
curl -s http://localhost:8003/health >nul 2>&1 && (
    echo ✓ ML Backend is running successfully!
    curl -s http://localhost:8003/health
) || (
    echo ✗ ML Backend failed to start
    echo.
    echo Possible solutions:
    echo 1. Install missing dependencies:
    echo    pip install fastapi uvicorn yfinance pandas numpy scikit-learn
    echo.
    echo 2. Try alternative ML backend:
    echo    python ml_backend_simple.py
    echo    or
    echo    python ml_backend_working.py
    echo.
    echo 3. Check the error in the ML Backend Test window
)

echo.
echo ============================================================
echo Diagnostic complete.
echo ============================================================
echo.
echo If ML Backend won't start, try this command to install all dependencies:
echo.
echo pip install fastapi uvicorn yfinance pandas numpy scikit-learn python-multipart aiofiles
echo.
pause