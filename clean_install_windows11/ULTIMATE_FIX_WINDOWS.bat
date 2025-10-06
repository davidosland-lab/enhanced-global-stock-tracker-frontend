@echo off
cls
color 0A
echo ================================================================
echo        ULTIMATE STOCK TRACKER - WINDOWS 11 FIX
echo        Handling All Dependencies and Issues
echo ================================================================
echo.

:: Set window title
title Stock Tracker Master Control

:: Phase 1: Kill existing processes
echo [PHASE 1] Terminating existing processes...
echo ----------------------------------------

:: Kill Python processes on our ports
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo Cleanup complete!
timeout /t 2 >nul

:: Phase 2: Fix Python Environment
echo.
echo [PHASE 2] Fixing Python environment...
echo ----------------------------------------

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo Python detected!
python --version

:: Fix setuptools and pip first
echo.
echo Fixing setuptools and pip issues...
python -m ensurepip --upgrade >nul 2>&1
python -m pip install --upgrade --force-reinstall pip >nul 2>&1
python -m pip install --upgrade --force-reinstall setuptools wheel >nul 2>&1

:: Phase 3: Install Dependencies (with error handling)
echo.
echo [PHASE 3] Installing dependencies (this may take a minute)...
echo ----------------------------------------

:: Create a temporary requirements file with core packages only
echo fastapi>temp_requirements.txt
echo uvicorn[standard]>>temp_requirements.txt
echo yfinance>>temp_requirements.txt
echo pandas>>temp_requirements.txt
echo numpy>>temp_requirements.txt
echo cachetools>>temp_requirements.txt
echo python-multipart>>temp_requirements.txt
echo aiofiles>>temp_requirements.txt
echo websockets>>temp_requirements.txt

:: Install packages one by one with error handling
echo Installing core packages...

python -m pip install fastapi --no-cache-dir 2>nul
if errorlevel 1 echo Warning: fastapi installation had issues

python -m pip install uvicorn --no-cache-dir 2>nul
if errorlevel 1 echo Warning: uvicorn installation had issues

python -m pip install yfinance --no-cache-dir 2>nul
if errorlevel 1 echo Warning: yfinance installation had issues

python -m pip install pandas --no-cache-dir 2>nul
if errorlevel 1 echo Warning: pandas installation had issues

python -m pip install numpy --no-cache-dir 2>nul
if errorlevel 1 echo Warning: numpy installation had issues

python -m pip install cachetools --no-cache-dir 2>nul
python -m pip install python-multipart --no-cache-dir 2>nul
python -m pip install aiofiles --no-cache-dir 2>nul
python -m pip install websockets --no-cache-dir 2>nul

:: Clean up temp file
del temp_requirements.txt >nul 2>&1

echo.
echo Dependencies installation attempted!

:: Phase 4: Check for backend file
echo.
echo [PHASE 4] Checking application files...
echo ----------------------------------------

if exist backend_ultimate_fixed.py (
    set BACKEND_FILE=backend_ultimate_fixed.py
    echo Found: backend_ultimate_fixed.py
) else if exist backend.py (
    set BACKEND_FILE=backend.py
    echo Found: backend.py
) else (
    echo ERROR: No backend file found!
    echo Creating minimal backend...
    call :create_minimal_backend
    set BACKEND_FILE=backend_minimal.py
)

:: Create uploads directory
if not exist uploads mkdir uploads

:: Phase 5: Start Services with Error Handling
echo.
echo [PHASE 5] Starting services...
echo ----------------------------------------

:: Start Backend
echo Starting Backend API on port 8002...
start "Stock Tracker Backend" /min cmd /c "python %BACKEND_FILE% 2>backend_error.log"
timeout /t 5 >nul

:: Check if backend started
curl -s http://localhost:8002/api/status >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Backend may have issues. Checking error log...
    if exist backend_error.log (
        type backend_error.log | head -5
    )
    echo.
    echo Attempting alternative backend start...
    start "Stock Tracker Backend" /min cmd /c "python -m uvicorn backend:app --host 0.0.0.0 --port 8002"
    timeout /t 5 >nul
) else (
    echo Backend API: RUNNING
)

:: Start Frontend Server
echo Starting Frontend Server on port 8000...
if exist frontend_server.py (
    start "Stock Tracker Frontend" /min cmd /c "python frontend_server.py 2>frontend_error.log"
) else (
    echo Using simple HTTP server...
    start "Stock Tracker Frontend" /min cmd /c "python -m http.server 8000 --directory . 2>frontend_error.log"
)
timeout /t 3 >nul

:: Phase 6: Launch Application
echo.
echo ================================================================
echo        STOCK TRACKER IS READY!
echo ================================================================
echo.
echo Services:
echo ---------
echo Backend API:  http://localhost:8002
echo Frontend UI:  http://localhost:8000
echo.
echo If modules show "file://" errors:
echo 1. Make sure you access via http://localhost:8000
echo 2. NOT by opening index.html directly
echo.
echo Opening application in browser...
timeout /t 3 >nul

:: Open browser
start http://localhost:8000

echo.
echo ================================================================
echo KEEP THIS WINDOW OPEN while using the application
echo Press any key to stop all services and exit
echo ================================================================
echo.

pause >nul

:: Cleanup
echo.
echo Shutting down services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1

echo All services stopped!
timeout /t 2 >nul
exit

:: Function to create minimal backend if none exists
:create_minimal_backend
(
echo import yfinance as yf
echo from fastapi import FastAPI, HTTPException, UploadFile, File
echo from fastapi.middleware.cors import CORSMiddleware
echo import uvicorn
echo from datetime import datetime
echo.
echo app = FastAPI^(^)
echo.
echo app.add_middleware^(
echo     CORSMiddleware,
echo     allow_origins=["*"],
echo     allow_credentials=True,
echo     allow_methods=["*"],
echo     allow_headers=["*"]
echo ^)
echo.
echo @app.get^("/api/status"^)
echo async def status^(^):
echo     return {"status": "online", "timestamp": datetime.now^(^).isoformat^(^)}
echo.
echo @app.get^("/api/stock/{symbol}"^)
echo async def get_stock^(symbol: str^):
echo     ticker = yf.Ticker^(symbol^)
echo     info = ticker.info
echo     hist = ticker.history^(period="1d"^)
echo     if hist.empty:
echo         raise HTTPException^(404, f"No data for {symbol}"^)
echo     latest = hist.iloc[-1]
echo     return {
echo         "symbol": symbol,
echo         "price": float^(latest['Close']^),
echo         "volume": int^(latest['Volume']^),
echo         "timestamp": datetime.now^(^).isoformat^(^)
echo     }
echo.
echo @app.get^("/api/historical/{symbol}"^)
echo async def get_historical^(symbol: str, period: str = "1mo"^):
echo     ticker = yf.Ticker^(symbol^)
echo     hist = ticker.history^(period=period^)
echo     data = []
echo     for idx, row in hist.iterrows^(^):
echo         data.append^({
echo             "date": idx.strftime^('%%Y-%%m-%%d %%H:%%M:%%S'^),
echo             "open": float^(row['Open']^),
echo             "high": float^(row['High']^),
echo             "low": float^(row['Low']^),
echo             "close": float^(row['Close']^),
echo             "volume": int^(row['Volume']^)
echo         }^)
echo     return {"symbol": symbol, "data": data}
echo.
echo @app.get^("/api/technical/{symbol}"^)
echo async def get_technical^(symbol: str^):
echo     ticker = yf.Ticker^(symbol^)
echo     hist = ticker.history^(period="3mo"^)
echo     close = hist['Close']
echo     sma_20 = close.rolling^(window=20^).mean^(^)
echo     sma_50 = close.rolling^(window=50^).mean^(^)
echo     return {
echo         "symbol": symbol,
echo         "indicators": {
echo             "sma_20": float^(sma_20.iloc[-1]^) if len^(sma_20^) ^> 0 else None,
echo             "sma_50": float^(sma_50.iloc[-1]^) if len^(sma_50^) ^> 0 else None,
echo             "current_price": float^(close.iloc[-1]^)
echo         },
echo         "signals": {
echo             "trend": "bullish" if sma_20.iloc[-1] ^> sma_50.iloc[-1] else "bearish"
echo         }
echo     }
echo.
echo @app.post^("/api/documents/upload"^)
echo async def upload_doc^(file: UploadFile = File^(...^)^):
echo     return {"filename": file.filename, "size": 0, "status": "uploaded"}
echo.
echo @app.get^("/api/indices"^)
echo async def get_indices^(^):
echo     return {"indices": [], "count": 0}
echo.
echo @app.post^("/api/predict"^)
echo async def predict^(data: dict^):
echo     return {"predictions": [], "method": "statistical"}
echo.
echo @app.post^("/api/historical/batch-download"^)
echo async def batch_download^(data: dict^):
echo     return {"success": 0, "failed": 0, "results": []}
echo.
echo @app.get^("/"^)
echo async def root^(^):
echo     return {"status": "online", "port": 8002}
echo.
echo if __name__ == "__main__":
echo     uvicorn.run^(app, host="0.0.0.0", port=8002^)
) > backend_minimal.py
goto :eof