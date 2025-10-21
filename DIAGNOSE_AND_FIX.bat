@echo off
cls
echo ==============================================================================
echo                      DIAGNOSE AND FIX - ML STOCK PREDICTOR
echo ==============================================================================
echo.

echo STEP 1: Checking Current Setup
echo ------------------------------------------------------------------------------

REM Check if Python is installed
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check yfinance
echo.
echo Checking yfinance...
python -c "import yfinance as yf; print(f'yfinance version: {yf.__version__}')" 2>nul
if errorlevel 1 (
    echo yfinance is NOT installed
    set NEED_INSTALL=1
) else (
    REM Check version
    python -c "import yfinance as yf; v=yf.__version__; exit(0 if v.startswith('0.2.18') else 1)" 2>nul
    if errorlevel 1 (
        echo WARNING: Wrong yfinance version detected
        set NEED_FIX=1
    ) else (
        echo OK: yfinance 0.2.18 is installed
    )
)

REM Check curl_cffi
echo.
echo Checking curl_cffi...
python -c "import curl_cffi; print(f'WARNING: curl_cffi {curl_cffi.__version__} is installed')" 2>nul
if errorlevel 1 (
    echo OK: curl_cffi is NOT installed (good!)
) else (
    echo This will cause problems on Windows!
    set NEED_FIX=1
)

REM Check other dependencies
echo.
echo Checking other dependencies...
python -c "import pandas, numpy, ta, sklearn, fastapi, uvicorn; print('OK: All core dependencies installed')" 2>nul
if errorlevel 1 (
    echo Some dependencies are missing
    set NEED_DEPS=1
)

echo.
echo ==============================================================================
echo STEP 2: Testing Yahoo Finance Connection
echo ------------------------------------------------------------------------------

python -c "import yfinance as yf; t=yf.Ticker('MSFT'); h=t.history(period='1d'); print(f'SUCCESS: Yahoo Finance is working! MSFT: ${h[\"Close\"].iloc[-1]:.2f}')" 2>nul
if errorlevel 1 (
    echo FAILED: Yahoo Finance is not working properly
    set NEED_FIX=1
) else (
    echo Yahoo Finance connection is working!
)

echo.
echo ==============================================================================
echo STEP 3: Diagnosis Complete
echo ------------------------------------------------------------------------------

if defined NEED_INSTALL (
    echo.
    echo INSTALLING YFINANCE...
    pip install yfinance==0.2.18
    set FIXED=1
)

if defined NEED_FIX (
    echo.
    echo FIXING YFINANCE INSTALLATION...
    echo Removing problematic packages...
    pip uninstall yfinance curl-cffi curl_cffi -y >nul 2>&1
    echo Installing correct version...
    pip install yfinance==0.2.18
    set FIXED=1
)

if defined NEED_DEPS (
    echo.
    echo INSTALLING MISSING DEPENDENCIES...
    pip install pandas numpy ta scikit-learn xgboost fastapi uvicorn pydantic
    set FIXED=1
)

if defined FIXED (
    echo.
    echo ==============================================================================
    echo FIXES APPLIED - RETESTING...
    echo ------------------------------------------------------------------------------
    python -c "import yfinance as yf; t=yf.Ticker('AAPL'); h=t.history(period='1d'); print(f'SUCCESS: Fixed! AAPL: ${h[\"Close\"].iloc[-1]:.2f}')" 2>nul
    if errorlevel 1 (
        echo.
        echo Still having issues. Try:
        echo 1. Run as Administrator
        echo 2. Check internet connection
        echo 3. Disable VPN if using one
        echo 4. Check firewall settings
    ) else (
        echo.
        echo EVERYTHING IS WORKING NOW!
    )
)

echo.
echo ==============================================================================
echo STEP 4: Ready to Start Server
echo ------------------------------------------------------------------------------
echo.

if not defined NEED_FIX if not defined NEED_INSTALL if not defined NEED_DEPS (
    echo Everything looks good! You can now start the server.
    echo.
)

echo To start the ML Stock Predictor server:
echo.
echo   python ml_core_windows.py
echo.
echo The server will be available at:
echo   http://localhost:8000
echo.
echo API Documentation at:
echo   http://localhost:8000/docs
echo.
echo ==============================================================================
echo.

choice /C YN /M "Do you want to start the server now?"
if errorlevel 2 goto :end
if errorlevel 1 goto :start

:start
echo.
echo Starting server...
python ml_core_windows.py
goto :end

:end
pause