@echo off
REM =========================================================
REM UNIFIED STOCK PREDICTOR SYSTEM - SINGLE STARTUP SCRIPT
REM =========================================================
REM Combines Yahoo Finance, Alpha Vantage, and ML Predictions
REM Single interface at localhost:8000
REM =========================================================

color 0A
cls

echo =========================================================
echo    UNIFIED ML STOCK PREDICTOR SYSTEM
echo =========================================================
echo.
echo Features:
echo  - Yahoo Finance Integration (Primary)
echo  - Alpha Vantage API (Backup)
echo  - Machine Learning Predictions
echo  - MCP Integration Ready
echo  - Australian Stock Support (CBA, BHP, etc.)
echo.
echo =========================================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check for required packages
echo.
echo Checking required packages...
pip show yfinance >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing yfinance...
    pip install yfinance
)

pip show flask >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Flask...
    pip install flask flask-cors
)

pip show pandas >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing pandas...
    pip install pandas numpy
)

pip show scikit-learn >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing scikit-learn...
    pip install scikit-learn
)

pip show xgboost >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing XGBoost...
    pip install xgboost
)

pip show requests >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing requests...
    pip install requests
)

REM Kill any existing Python servers on port 8000
echo.
echo Checking for existing servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping existing server (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

REM Wait a moment for port to be freed
timeout /t 2 /nobreak >nul

REM Start the unified server
echo.
echo =========================================================
echo Starting Unified Stock Predictor Server...
echo =========================================================
echo.
echo Server Configuration:
echo  - Port: 8000
echo  - Yahoo Finance: ENABLED (Primary)
echo  - Alpha Vantage: ENABLED (Backup)
echo  - API Key: 68ZFANK047DL0KSR
echo  - Auto-detection: Australian stocks (.AX)
echo.
echo =========================================================
echo.

REM Check which server file to use
if exist "fixed_flask_server.py" (
    echo Starting fixed_flask_server.py...
    start "Stock Server" /min cmd /c "python fixed_flask_server.py"
) else if exist "unified_system.py" (
    echo Starting unified_system.py...
    start "Stock Server" /min cmd /c "python unified_system.py"
) else if exist "yahoo_only_server.py" (
    echo Starting yahoo_only_server.py...
    start "Stock Server" /min cmd /c "python yahoo_only_server.py"
) else (
    echo ERROR: No server file found!
    echo Please ensure one of these files exists:
    echo  - fixed_flask_server.py
    echo  - unified_system.py
    echo  - yahoo_only_server.py
    pause
    exit /b 1
)

REM Wait for server to start
echo.
echo Waiting for server to initialize...
timeout /t 5 /nobreak >nul

REM Test server connection
echo.
echo Testing server connection...
curl -s -o nul -w "Server Status: %%{http_code}" http://localhost:8000/api/status
echo.
echo.

REM Open browser to interface
echo =========================================================
echo    SERVER STARTED SUCCESSFULLY!
echo =========================================================
echo.
echo Access the interface at:
echo   http://localhost:8000
echo.
echo Quick Test URLs:
echo   - Status: http://localhost:8000/api/status
echo   - Interface: http://localhost:8000
echo.
echo Australian Stocks (auto-detect .AX):
echo   CBA, BHP, CSL, NAB, WBC, ANZ, WES, WOW, RIO, FMG
echo.
echo US Stocks:
echo   AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META
echo.
echo =========================================================
echo.
echo Opening browser...
start http://localhost:8000

echo.
echo Press any key to stop the server and exit...
pause >nul

REM Kill the server
echo.
echo Stopping server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Server stopped.
echo.
pause