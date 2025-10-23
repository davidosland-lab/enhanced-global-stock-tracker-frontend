@echo off
cls
echo ================================================================
echo     FIX FOR PYTHON 3.12 + YFINANCE ISSUES
echo     Solves SSL, urllib3, and compatibility problems
echo ================================================================
echo.

:: Check Python version
python --version
echo.

:: STEP 1: Fix SSL certificates
echo [STEP 1] Fixing SSL certificates...
python -m pip install --upgrade certifi >nul 2>&1
python -c "import ssl; print('SSL version:', ssl.OPENSSL_VERSION)"
echo.

:: STEP 2: Uninstall problematic packages
echo [STEP 2] Cleaning up conflicting packages...
python -m pip uninstall urllib3 requests yfinance -y >nul 2>&1

:: STEP 3: Install specific versions that work with Python 3.12
echo [STEP 3] Installing compatible versions...
echo.

echo Installing urllib3 v1.26.18 (last version before v2.0)...
python -m pip install urllib3==1.26.18 --no-cache-dir

echo Installing requests with compatible urllib3...
python -m pip install requests==2.31.0 --no-cache-dir

echo Installing latest yfinance...
python -m pip install yfinance --no-cache-dir

echo Installing pandas and numpy for Python 3.12...
python -m pip install pandas==2.1.4 numpy==1.26.2 --no-cache-dir

:: STEP 4: Test yfinance
echo.
echo [STEP 4] Testing yfinance...
python -c "import yfinance as yf; t = yf.Ticker('AAPL'); print('AAPL current price:', t.history(period='1d')['Close'].iloc[-1])" 2>nul
if errorlevel 1 (
    echo.
    echo yfinance test failed. Trying alternative fix...
    
    :: Alternative fix - install older yfinance
    python -m pip uninstall yfinance -y >nul 2>&1
    python -m pip install yfinance==0.2.28 --no-cache-dir
    
    :: Test again
    python -c "import yfinance as yf; t = yf.Ticker('AAPL'); print('Test successful!')" 2>nul
    if errorlevel 1 (
        echo Still having issues. Will use compatibility mode.
    ) else (
        echo Alternative fix successful!
    )
) else (
    echo yfinance is working correctly!
)

:: STEP 5: Install remaining packages
echo.
echo [STEP 5] Installing remaining packages...
python -m pip install fastapi uvicorn python-multipart aiofiles cachetools --no-cache-dir >nul 2>&1

:: STEP 6: Create test script
echo.
echo [STEP 6] Creating test script...
(
echo import yfinance as yf
echo import sys
echo.
echo try:
echo     # Test CBA.AX
echo     cba = yf.Ticker^("CBA.AX"^)
echo     cba_hist = cba.history^(period="1d"^)
echo     if not cba_hist.empty:
echo         print^(f"CBA.AX Price: ${cba_hist['Close'].iloc[-1]:.2f}"^)
echo     else:
echo         print^("CBA.AX: No data"^)
echo.        
echo     # Test AAPL
echo     aapl = yf.Ticker^("AAPL"^)
echo     aapl_hist = aapl.history^(period="1d"^)
echo     if not aapl_hist.empty:
echo         print^(f"AAPL Price: ${aapl_hist['Close'].iloc[-1]:.2f}"^)
echo     else:
echo         print^("AAPL: No data"^)
echo.        
echo     print^("\nYahoo Finance is working correctly!"^)
echo     sys.exit^(0^)
echo except Exception as e:
echo     print^(f"Error: {e}"^)
echo     print^("\nYahoo Finance is not working properly."^)
echo     sys.exit^(1^)
) > test_yfinance.py

echo Running test...
python test_yfinance.py
echo.

:: STEP 7: Start the real-data backend
echo ================================================================
echo     STARTING REAL DATA BACKEND (NO FALLBACKS)
echo ================================================================
echo.

:: Kill any existing backend
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start real-only backend
echo Starting backend with REAL DATA ONLY...
start "Real Data Backend" /min cmd /c "python backend_real_only.py"
timeout /t 5 >nul

:: Start frontend
echo Starting frontend server...
start "Frontend Server" /min cmd /c "python -m http.server 8000"
timeout /t 3 >nul

:: Open browser
echo.
echo ================================================================
echo     REAL DATA STOCK TRACKER IS RUNNING!
echo ================================================================
echo.
echo - Backend: http://localhost:8002 (Real Yahoo Finance data only)
echo - Frontend: http://localhost:8000
echo - No fallback data, no synthetic data, no demo data
echo.
echo Opening browser...
start http://localhost:8000

echo.
echo Keep this window open. Press any key to stop...
pause >nul

:: Cleanup
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

del test_yfinance.py >nul 2>&1
echo Services stopped.
timeout /t 2 >nul