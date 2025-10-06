@echo off
cls
echo ================================================================
echo     EMERGENCY BACKEND START - FIXING CONNECTION REFUSED
echo ================================================================
echo.

:: Kill any stuck processes first
echo Killing any stuck processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *Backend*" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul

:: Try different backend files in order of preference
echo Starting backend server...
echo.

:: Option 1: Try backend_real_only.py
if exist backend_real_only.py (
    echo Attempting to start backend_real_only.py...
    start "Backend Server" cmd /k "python backend_real_only.py"
    goto :wait
)

:: Option 2: Try backend_fixed_final.py
if exist backend_fixed_final.py (
    echo Attempting to start backend_fixed_final.py...
    start "Backend Server" cmd /k "python backend_fixed_final.py"
    goto :wait
)

:: Option 3: Try backend.py
if exist backend.py (
    echo Attempting to start backend.py...
    start "Backend Server" cmd /k "python backend.py"
    goto :wait
)

:: Option 4: Create minimal backend
echo No backend found! Creating minimal backend...
(
echo from fastapi import FastAPI, HTTPException
echo from fastapi.middleware.cors import CORSMiddleware
echo import uvicorn
echo import yfinance as yf
echo from datetime import datetime
echo.
echo app = FastAPI^(^)
echo.
echo app.add_middleware^(
echo     CORSMiddleware,
echo     allow_origins=["*"],
echo     allow_methods=["*"],
echo     allow_headers=["*"]
echo ^)
echo.
echo @app.get^("/"^)
echo def root^(^):
echo     return {"status": "online", "port": 8002}
echo.
echo @app.get^("/api/status"^)
echo def status^(^):
echo     return {"status": "online", "backend": "connected", "timestamp": datetime.now^(^).isoformat^(^)}
echo.
echo @app.get^("/api/stock/{symbol}"^)
echo def get_stock^(symbol: str, period: str = "1d", interval: str = "5m"^):
echo     try:
echo         ticker = yf.Ticker^(symbol^)
echo         hist = ticker.history^(period=period, interval=interval^)
echo         if hist.empty:
echo             return {"symbol": symbol, "price": 100, "error": "No data"}
echo         latest = hist.iloc[-1]
echo         return {
echo             "symbol": symbol,
echo             "price": float^(latest['Close']^),
echo             "volume": int^(latest['Volume']^),
echo             "high": float^(latest['High']^),
echo             "low": float^(latest['Low']^),
echo             "timestamp": datetime.now^(^).isoformat^(^)
echo         }
echo     except Exception as e:
echo         return {"symbol": symbol, "price": 100, "error": str^(e^)}
echo.
echo @app.get^("/api/historical/{symbol}"^)
echo def get_historical^(symbol: str, period: str = "1mo", interval: str = "1d"^):
echo     try:
echo         ticker = yf.Ticker^(symbol^)
echo         hist = ticker.history^(period=period, interval=interval^)
echo         data = []
echo         for idx, row in hist.iterrows^(^):
echo             data.append^({
echo                 "date": idx.strftime^('%%Y-%%m-%%d %%H:%%M:%%S'^),
echo                 "close": float^(row['Close']^),
echo                 "volume": int^(row['Volume']^)
echo             }^)
echo         return {"symbol": symbol, "data": data}
echo     except:
echo         return {"symbol": symbol, "data": []}
echo.
echo @app.get^("/api/indices"^)
echo def indices^(^):
echo     return {"indices": [], "count": 0}
echo.
echo @app.get^("/api/technical/{symbol}"^)
echo def technical^(symbol: str^):
echo     return {"symbol": symbol, "indicators": {}, "signals": {}}
echo.
echo @app.post^("/api/predict"^)
echo def predict^(data: dict^):
echo     return {"predictions": []}
echo.
echo @app.post^("/api/documents/upload"^)
echo def upload^(^):
echo     return {"status": "uploaded"}
echo.
echo @app.post^("/api/historical/batch-download"^)
echo def batch^(^):
echo     return {"results": []}
echo.
echo @app.post^("/api/phase4/backtest"^)
echo def backtest^(data: dict^):
echo     return {"metrics": {}}
echo.
echo if __name__ == "__main__":
echo     print^("Starting backend on http://localhost:8002"^)
echo     uvicorn.run^(app, host="0.0.0.0", port=8002^)
) > emergency_backend.py

start "Backend Server" cmd /k "python emergency_backend.py"

:wait
echo.
echo Waiting for backend to start...
timeout /t 5 >nul

:: Test if backend is running
echo.
echo Testing backend connection...
curl -s http://localhost:8002/api/status >test_result.txt 2>&1
if errorlevel 1 (
    echo.
    echo Backend failed to start. Checking Python installation...
    python --version
    echo.
    echo Checking if packages are installed...
    python -c "import fastapi; print('fastapi: OK')" 2>nul
    if errorlevel 1 (
        echo fastapi NOT installed! Installing now...
        pip install fastapi uvicorn yfinance
    )
    
    python -c "import yfinance; print('yfinance: OK')" 2>nul
    if errorlevel 1 (
        echo yfinance NOT installed! Installing now...
        pip install yfinance
    )
    
    echo.
    echo Trying to start backend again...
    if exist emergency_backend.py (
        start "Backend Server" cmd /k "python emergency_backend.py"
    )
    timeout /t 5 >nul
) else (
    echo Backend is running!
    type test_result.txt
)

del test_result.txt >nul 2>&1

echo.
echo ================================================================
echo     BACKEND STATUS
echo ================================================================
echo.
echo The backend should now be running on: http://localhost:8002
echo.
echo You should see a NEW command window with the backend server.
echo If you don't see it, the backend failed to start.
echo.
echo To test manually, open a new command prompt and run:
echo   python backend.py
echo.
echo Or try:
echo   python -m uvicorn backend:app --host 0.0.0.0 --port 8002
echo.
echo ================================================================
echo.
pause