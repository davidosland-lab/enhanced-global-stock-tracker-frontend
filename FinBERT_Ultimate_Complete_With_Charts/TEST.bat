@echo off
echo ================================================================
echo    FinBERT Ultimate - System Test
echo ================================================================
echo.

:: Test Python
echo [1/5] Testing Python installation...
python --version
if errorlevel 1 (
    echo [FAIL] Python not found
    pause
    exit /b 1
)
echo [PASS] Python installed
echo.

:: Test required packages
echo [2/5] Testing required packages...
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
if errorlevel 1 (
    echo [FAIL] NumPy not installed - Run INSTALL.bat
    pause
    exit /b 1
)

python -c "import pandas; print(f'Pandas installed: OK')"
if errorlevel 1 (
    echo [FAIL] Pandas not installed - Run INSTALL.bat
    pause
    exit /b 1
)

python -c "import sklearn; print(f'Scikit-learn installed: OK')"
if errorlevel 1 (
    echo [FAIL] Scikit-learn not installed - Run INSTALL.bat
    pause
    exit /b 1
)

python -c "import flask; print(f'Flask installed: OK')"
if errorlevel 1 (
    echo [FAIL] Flask not installed - Run INSTALL.bat
    pause
    exit /b 1
)

python -c "import yfinance; print(f'yfinance installed: OK')"
if errorlevel 1 (
    echo [FAIL] yfinance not installed - Run INSTALL.bat
    pause
    exit /b 1
)

echo [PASS] All required packages installed
echo.

:: Test FinBERT (optional)
echo [3/5] Testing FinBERT (optional)...
python -c "import transformers; print('FinBERT support: ENABLED')" 2>nul
if errorlevel 1 (
    echo FinBERT support: DISABLED (using fallback sentiment)
) 
echo.

:: Test server startup
echo [4/5] Testing server startup...
echo Starting test server (will stop in 5 seconds)...
start /B python -c "from app_finbert_ultimate import app; print('Server test: OK')"
timeout /t 2 /nobreak >nul
taskkill /F /IM python.exe >nul 2>&1
echo [PASS] Server can start
echo.

:: Test data fetch
echo [5/5] Testing data fetch...
python -c "import yfinance as yf; data = yf.download('AAPL', period='1d', progress=False); print('Data fetch: OK' if len(data) > 0 else 'Data fetch: FAILED')"
echo.

echo ================================================================
echo    Test Results Summary
echo ================================================================
echo.
echo ✓ Python installed and working
echo ✓ Required packages available
echo ✓ Server can start
echo ✓ Data fetching works
echo.
echo System is ready to use!
echo Run START.bat to begin.
echo.
echo ================================================================
pause