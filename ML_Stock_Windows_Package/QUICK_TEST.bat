@echo off
REM ============================================================
REM QUICK TEST - Check if server is working
REM ============================================================

title Quick Server Test
color 0B
cls

echo ============================================================
echo    QUICK SERVER TEST
echo ============================================================
echo.

echo Testing server connection...
echo.

REM Test with curl if available
curl --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using curl to test server...
    echo.
    
    echo 1. Testing /api/status endpoint:
    curl -s http://localhost:8000/api/status
    echo.
    echo.
    
    echo 2. Testing stock fetch (CBA):
    curl -s -X POST http://localhost:8000/api/fetch -H "Content-Type: application/json" -d "{\"symbol\":\"CBA\",\"period\":\"1mo\"}"
    echo.
    echo.
) else (
    echo curl not found. Testing with PowerShell...
    echo.
    
    echo 1. Testing /api/status endpoint:
    powershell -Command "Invoke-WebRequest -Uri http://localhost:8000/api/status -UseBasicParsing | Select-Object -ExpandProperty Content"
    echo.
    echo.
    
    echo 2. Testing stock fetch (CBA):
    powershell -Command "$body = '{\"symbol\":\"CBA\",\"period\":\"1mo\"}'; Invoke-WebRequest -Uri http://localhost:8000/api/fetch -Method POST -Body $body -ContentType 'application/json' -UseBasicParsing | Select-Object -ExpandProperty Content"
    echo.
)

echo.
echo ============================================================
echo Test complete!
echo.
echo If you see JSON data above, the server is working correctly.
echo If you see errors, the server may not be running.
echo ============================================================
echo.
pause