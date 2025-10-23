@echo off
REM Test Stock Tracker Services

echo Testing Stock Tracker Services...
echo.

echo Testing Frontend (http://localhost:8000)...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8000
echo.

echo Testing Backend Health (http://localhost:8002/api/health)...
curl -s http://localhost:8002/api/health
echo.
echo.

echo Testing ML Backend Health (http://localhost:8003/health)...
curl -s http://localhost:8003/health
echo.
echo.

echo Testing Stock Data (CBA.AX)...
curl -s http://localhost:8002/api/stock/CBA.AX
echo.
echo.

pause
