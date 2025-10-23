@echo off
cls
echo ================================================================
echo     TESTING HISTORICAL DATA MANAGER API ENDPOINTS
echo ================================================================
echo.

echo [1] Testing Basic API Status...
curl -s http://localhost:8002/api/status
echo.
echo.

echo [2] Testing Historical Data Endpoint (CBA.AX)...
curl -s "http://localhost:8002/api/historical/CBA.AX?period=1mo&interval=1d"
echo.
echo.

echo [3] Testing Batch Download Endpoint...
curl -X POST http://localhost:8002/api/historical/batch-download -H "Content-Type: application/json" -d "{\"symbols\":[\"AAPL\",\"CBA.AX\"]}"
echo.
echo.

echo [4] Testing Download Endpoint...
curl -X POST http://localhost:8002/api/historical/download -H "Content-Type: application/json" -d "{\"symbol\":\"AAPL\",\"period\":\"1mo\"}"
echo.
echo.

echo [5] Testing Statistics Endpoint...
curl -s http://localhost:8002/api/historical/statistics
echo.
echo.

echo ================================================================
echo     CHECK RESULTS ABOVE
echo ================================================================
echo.
echo If you see:
echo - "404" or "Method Not Allowed" = Endpoint missing in backend
echo - "500" = Backend error
echo - JSON data = Endpoint working
echo.
pause