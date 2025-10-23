@echo off
echo ================================================================================
echo STOCK TRACKER - WINDOWS 11 LOCAL DEPLOYMENT
echo Starting All Services on Local Machine
echo ================================================================================
echo.

REM Kill any existing Python processes on our ports
echo Cleaning up old processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8005') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8006') do taskkill /F /PID %%a 2>nul

timeout /t 3 /nobreak >nul

echo.
echo Starting services for Windows 11...
echo.

REM Start each service in a new minimized window
echo [1/6] Starting Main Backend (Port 8000)...
start "Main Backend" /min cmd /c "cd /d %cd% && python main_backend.py"
timeout /t 2 /nobreak >nul

echo [2/6] Starting Historical Backend (Port 8001)...
start "Historical Backend" /min cmd /c "cd /d %cd% && python historical_backend.py"
timeout /t 2 /nobreak >nul

echo [3/6] Starting ML Backend (Port 8002)...
start "ML Backend" /min cmd /c "cd /d %cd% && python ml_backend.py"
timeout /t 2 /nobreak >nul

echo [4/6] Starting FinBERT Backend (Port 8003)...
start "FinBERT Backend" /min cmd /c "cd /d %cd% && python finbert_backend.py"
timeout /t 2 /nobreak >nul

echo [5/6] Starting Backtesting Backend (Port 8005)...
start "Backtesting Backend" /min cmd /c "cd /d %cd% && python backtesting_backend.py"
timeout /t 2 /nobreak >nul

echo [6/6] Starting Web Scraper Backend (Port 8006)...
REM Try the real scraper first, fallback to simple if it fails
start "Web Scraper" /min cmd /c "cd /d %cd% && python web_scraper_real.py || python web_scraper_simple.py || python web_scraper_backend.py"
timeout /t 3 /nobreak >nul

echo.
echo Waiting for services to initialize...
timeout /t 5 /nobreak >nul

echo.
echo ================================================================================
echo CHECKING SERVICE STATUS
echo ================================================================================
echo.

REM Check each service
powershell -Command "(Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing -TimeoutSec 2).StatusCode" 2>nul | findstr "200" >nul
if %errorlevel% equ 0 (
    echo [OK] Main Backend:      http://localhost:8000
) else (
    echo [!!] Main Backend:      NOT RESPONDING
)

powershell -Command "(Invoke-WebRequest -Uri http://localhost:8001/health -UseBasicParsing -TimeoutSec 2).StatusCode" 2>nul | findstr "200" >nul
if %errorlevel% equ 0 (
    echo [OK] Historical:        http://localhost:8001
) else (
    echo [!!] Historical:        NOT RESPONDING
)

powershell -Command "(Invoke-WebRequest -Uri http://localhost:8002/health -UseBasicParsing -TimeoutSec 2).StatusCode" 2>nul | findstr "200" >nul
if %errorlevel% equ 0 (
    echo [OK] ML Backend:        http://localhost:8002
) else (
    echo [!!] ML Backend:        NOT RESPONDING
)

powershell -Command "(Invoke-WebRequest -Uri http://localhost:8003/health -UseBasicParsing -TimeoutSec 2).StatusCode" 2>nul | findstr "200" >nul
if %errorlevel% equ 0 (
    echo [OK] FinBERT:          http://localhost:8003
) else (
    echo [!!] FinBERT:          NOT RESPONDING - May need transformers library
)

powershell -Command "(Invoke-WebRequest -Uri http://localhost:8005/health -UseBasicParsing -TimeoutSec 2).StatusCode" 2>nul | findstr "200" >nul
if %errorlevel% equ 0 (
    echo [OK] Backtesting:      http://localhost:8005
) else (
    echo [!!] Backtesting:      NOT RESPONDING
)

powershell -Command "(Invoke-WebRequest -Uri http://localhost:8006/health -UseBasicParsing -TimeoutSec 2).StatusCode" 2>nul | findstr "200" >nul
if %errorlevel% equ 0 (
    echo [OK] Web Scraper:      http://localhost:8006
) else (
    echo [!!] Web Scraper:      NOT RESPONDING - Check web_scraper_real.py
)

echo.
echo ================================================================================
echo READY TO USE - WINDOWS 11
echo ================================================================================
echo.
echo Open in your browser:
echo.
echo Main Dashboard:      http://localhost:8000
echo Prediction Center:   http://localhost:8000/prediction_center.html  
echo Sentiment Scraper:   http://localhost:8000/sentiment_scraper.html
echo.
echo If Web Scraper not working, check:
echo 1. Python dependencies: pip install yfinance beautifulsoup4 feedparser aiohttp
echo 2. Try running manually: python web_scraper_real.py
echo 3. Check Windows Firewall - may need to allow Python through firewall
echo.
echo Press any key to open the main dashboard in your browser...
pause >nul

start http://localhost:8000

echo.
echo Services are running. Close this window to stop all services.
echo.
pause