@echo off
cls
echo ================================================================
echo     DIAGNOSTIC TOOL - Finding Why Backend Won't Start
echo ================================================================
echo.

echo [1] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH!
    echo Please install Python or fix PATH
    pause
    exit
)

echo.
echo [2] Checking current directory...
cd
echo.
dir backend*.py 2>nul
if errorlevel 1 (
    echo WARNING: No backend files found in current directory!
)

echo.
echo [3] Checking if port 8002 is in use...
netstat -ano | findstr :8002
if not errorlevel 1 (
    echo Port 8002 is already in use!
    echo.
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002 ^| findstr LISTENING') do (
        echo Process using port 8002: PID %%a
        tasklist /FI "PID eq %%a"
    )
)

echo.
echo [4] Checking Python packages...
echo.
python -c "import fastapi; print('fastapi: INSTALLED')" 2>nul
if errorlevel 1 (
    echo fastapi: NOT INSTALLED
    echo Fix: pip install fastapi
)

python -c "import uvicorn; print('uvicorn: INSTALLED')" 2>nul
if errorlevel 1 (
    echo uvicorn: NOT INSTALLED
    echo Fix: pip install uvicorn
)

python -c "import yfinance; print('yfinance: INSTALLED')" 2>nul
if errorlevel 1 (
    echo yfinance: NOT INSTALLED
    echo Fix: pip install yfinance
)

echo.
echo [5] Testing simple Python server...
echo Creating test server...
(
echo import socket
echo s = socket.socket^(socket.AF_INET, socket.SOCK_STREAM^)
echo try:
echo     s.bind^(^('', 8002^)^)
echo     print^('Port 8002 is available'^)
echo     s.close^(^)
echo except:
echo     print^('Port 8002 is blocked or in use'^)
) > test_port.py

python test_port.py
del test_port.py

echo.
echo [6] Testing yfinance directly...
python -c "import yfinance as yf; t=yf.Ticker('AAPL'); h=t.history(period='1d'); print(f'AAPL Price: ${h[\"Close\"].iloc[-1]:.2f}')" 2>&1

echo.
echo [7] Trying to import and run backend...
if exist backend.py (
    echo Testing backend.py imports...
    python -c "import backend; print('Backend imports OK')" 2>&1
    if errorlevel 1 (
        echo.
        echo Backend has import errors. See above for details.
    )
)

echo.
echo ================================================================
echo     RECOMMENDED FIXES
echo ================================================================
echo.
echo 1. Install missing packages:
echo    pip install fastapi uvicorn yfinance pandas numpy python-multipart aiofiles
echo.
echo 2. If port 8002 is blocked, try a different port:
echo    Edit backend.py and change port from 8002 to 8082
echo.
echo 3. Run backend directly to see errors:
echo    python backend.py
echo.
echo 4. If yfinance fails, downgrade urllib3:
echo    pip install urllib3==1.26.18
echo.
echo ================================================================
pause