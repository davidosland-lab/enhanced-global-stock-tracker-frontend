@echo off
echo ================================================================================
echo RESTARTING WEB SCRAPER WITH COMPLETE VERSION
echo For Windows 11 Local Deployment
echo ================================================================================
echo.

echo Step 1: Stopping any existing web scraper...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8006') do (
    echo Killing process %%a on port 8006...
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Starting complete web scraper (all endpoints working)...
start "Web Scraper Complete" /min cmd /c "python web_scraper_complete.py"

echo.
echo Waiting for service to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 3: Testing web scraper endpoints...
echo.

echo Testing /health endpoint...
curl -s http://localhost:8006/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Health endpoint working
) else (
    echo [!!] Health endpoint not responding
)

echo.
echo Testing /sources endpoint...
curl -s http://localhost:8006/sources >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Sources endpoint working
) else (
    echo [!!] Sources endpoint not responding
)

echo.
echo ================================================================================
echo WEB SCRAPER RESTARTED
echo ================================================================================
echo.
echo The web scraper should now be working with all endpoints:
echo - http://localhost:8006/health    (Service health check)
echo - http://localhost:8006/sources   (List available sources)
echo - http://localhost:8006/scrape    (Scrape sentiment data)
echo - http://localhost:8006/test      (Test endpoint)
echo.
echo Test it at: http://localhost:8000/sentiment_scraper.html
echo.
pause