@echo off
cls
echo ============================================================
echo    TESTING SERVER ENDPOINTS
echo ============================================================
echo.

REM Check if server is running
echo Checking if server is running on port 8000...
netstat -an | findstr :8000 | findstr LISTENING >nul
if %errorlevel% neq 0 (
    echo [ERROR] Server is not running on port 8000!
    echo Please run setup_and_run.bat first
    echo.
    pause
    exit /b 1
)

echo [OK] Server is running
echo.

echo Testing endpoints with curl...
echo.

REM Test root endpoint
echo Testing: http://localhost:8000/
curl -s -o nul -w "Root endpoint (/) - Status: %%{http_code}\n" http://localhost:8000/
echo.

REM Test API endpoints
echo Testing: http://localhost:8000/api/stock/AAPL
curl -s -o nul -w "Stock API endpoint - Status: %%{http_code}\n" http://localhost:8000/api/stock/AAPL
echo.

REM Test with PowerShell as alternative
echo.
echo Testing with PowerShell...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/' -UseBasicParsing; Write-Host '[OK] Main page accessible' -ForegroundColor Green } catch { Write-Host '[ERROR] Cannot access main page' -ForegroundColor Red }"

powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/stock/AAPL?period=1mo' -UseBasicParsing; Write-Host '[OK] API endpoint accessible' -ForegroundColor Green; $data = $response.Content | ConvertFrom-Json; Write-Host 'Data source:' $data.source } catch { Write-Host '[ERROR] API endpoint not working' -ForegroundColor Red; Write-Host $_.Exception.Message }"

echo.
echo ============================================================
echo.
echo If you see 404 errors, the server routes may not be loading.
echo Try these solutions:
echo   1. Stop the server (Ctrl+C)
echo   2. Run setup_and_run.bat
echo   3. Make sure app.py is in the current directory
echo.
pause