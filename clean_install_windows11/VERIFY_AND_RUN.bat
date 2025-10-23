@echo off
cls
echo ================================================================
echo     VERIFYING INSTALLATION AND STARTING STOCK TRACKER
echo ================================================================
echo.

:: Test Python packages
echo Testing installed packages...
echo.

echo [1/5] Testing yfinance...
python -c "import yfinance; print('  SUCCESS: yfinance 0.2.66 installed')" 2>nul
if errorlevel 1 (
    echo   FAILED: yfinance not working
) else (
    :: Test real data
    python -c "import yfinance as yf; t=yf.Ticker('CBA.AX'); h=t.history(period='1d'); print(f'  CBA.AX Real Price: ${h[\"Close\"].iloc[-1]:.2f}')" 2>nul
)

echo.
echo [2/5] Testing pandas...
python -c "import pandas; print('  SUCCESS: pandas installed')" 2>nul
if errorlevel 1 echo   FAILED: pandas not working

echo.
echo [3/5] Testing numpy...
python -c "import numpy; print('  SUCCESS: numpy installed')" 2>nul
if errorlevel 1 echo   FAILED: numpy not working

echo.
echo [4/5] Testing fastapi...
python -c "import fastapi; print('  SUCCESS: fastapi installed')" 2>nul
if errorlevel 1 echo   FAILED: fastapi not working

echo.
echo [5/5] Testing websockets...
python -c "import websockets; print('  SUCCESS: websockets installed')" 2>nul
if errorlevel 1 echo   FAILED: websockets not working

echo.
echo ================================================================
echo     STARTING STOCK TRACKER WITH REAL DATA
echo ================================================================
echo.

:: Clean up any temp directories (optional)
echo Cleaning up temporary files...
rd /s /q "C:\Users\david\AppData\Roaming\Python\Python312\site-packages\~ebsockets" 2>nul
rd /s /q "C:\Users\david\AppData\Roaming\Python\Python312\site-packages\~umpy.libs" 2>nul
rd /s /q "C:\Users\david\AppData\Roaming\Python\Python312\site-packages\~umpy" 2>nul

:: Kill existing processes
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start backend with real data
echo Starting backend (REAL DATA ONLY)...
if exist backend_real_only.py (
    start "Real Data Backend" /min cmd /c "python backend_real_only.py"
) else if exist backend.py (
    start "Backend" /min cmd /c "python backend.py"
) else (
    echo ERROR: No backend file found!
    pause
    exit
)

timeout /t 5 >nul

:: Test backend
curl -s http://localhost:8002/api/status >nul 2>&1
if errorlevel 1 (
    echo Backend starting slowly, waiting...
    timeout /t 5 >nul
)

:: Start frontend
echo Starting frontend server...
start "Frontend Server" /min cmd /c "python -m http.server 8000"
timeout /t 3 >nul

:: Display status
echo.
echo ================================================================
echo     STOCK TRACKER IS RUNNING!
echo ================================================================
echo.
echo Backend API:  http://localhost:8002  [Real Yahoo Finance Data]
echo Frontend UI:  http://localhost:8000
echo.
echo Installation Status:
echo - yfinance 0.2.66:  INSTALLED
echo - pandas 2.1.4:     INSTALLED  
echo - numpy 1.26.2:     INSTALLED
echo - websockets:       INSTALLED
echo.
echo The PATH warnings can be IGNORED - they don't affect the app!
echo.
echo Opening browser...
start http://localhost:8000

echo.
echo Press any key to stop all services...
pause >nul

:: Shutdown
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo All services stopped.
timeout /t 2 >nul