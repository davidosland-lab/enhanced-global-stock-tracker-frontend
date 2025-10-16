@echo off
echo ========================================
echo StockTracker V10 - Service Monitor
echo ========================================
echo.
echo Monitoring services in real-time...
echo Press Ctrl+C to stop monitoring
echo.

:loop
cls
echo ========================================
echo StockTracker V10 - Service Monitor
echo ========================================
echo Timestamp: %date% %time%
echo.

echo PORT STATUS:
echo ------------
netstat -an | findstr ":8000.*LISTENING" >nul && (
    echo [✓] Port 8000 - Main Backend: ACTIVE
) || (
    echo [✗] Port 8000 - Main Backend: NOT RUNNING
)

netstat -an | findstr ":8002.*LISTENING" >nul && (
    echo [✓] Port 8002 - ML Backend: ACTIVE
) || (
    echo [✗] Port 8002 - ML Backend: NOT RUNNING
)

netstat -an | findstr ":8003.*LISTENING" >nul && (
    echo [✓] Port 8003 - FinBERT Backend: ACTIVE
) || (
    echo [✗] Port 8003 - FinBERT Backend: NOT RUNNING
)

netstat -an | findstr ":8004.*LISTENING" >nul && (
    echo [✓] Port 8004 - Historical Backend: ACTIVE
) || (
    echo [✗] Port 8004 - Historical Backend: NOT RUNNING
)

netstat -an | findstr ":8005.*LISTENING" >nul && (
    echo [✓] Port 8005 - Backtesting Backend: ACTIVE
) || (
    echo [✗] Port 8005 - Backtesting Backend: NOT RUNNING
)

echo.
echo API HEALTH CHECKS:
echo ------------------

REM Check each service health endpoint
curl -s -o nul -w "Main Backend:        %%{http_code}\n" http://localhost:8000/health 2>nul || echo Main Backend:        OFFLINE
curl -s -o nul -w "ML Backend:          %%{http_code}\n" http://localhost:8002/health 2>nul || echo ML Backend:          OFFLINE
curl -s -o nul -w "FinBERT Backend:     %%{http_code}\n" http://localhost:8003/health 2>nul || echo FinBERT Backend:     OFFLINE
curl -s -o nul -w "Historical Backend:  %%{http_code}\n" http://localhost:8004/health 2>nul || echo Historical Backend:  OFFLINE
curl -s -o nul -w "Backtesting Backend: %%{http_code}\n" http://localhost:8005/health 2>nul || echo Backtesting Backend: OFFLINE

echo.
echo PYTHON PROCESSES:
echo -----------------
wmic process where "name='python.exe'" get ProcessId,WorkingSetSize,CommandLine 2>nul | findstr /i python | findstr /i backend

echo.
echo Refreshing in 5 seconds...
timeout /t 5 >nul
goto loop