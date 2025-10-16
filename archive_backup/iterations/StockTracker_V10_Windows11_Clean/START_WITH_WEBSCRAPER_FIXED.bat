@echo off
echo ================================================================================
echo STARTING ALL SERVICES INCLUDING WEB SCRAPER
echo ================================================================================
echo.

echo Stopping any existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8002"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8003"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8005"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8006"') do taskkill /F /PID %%a 2>nul
timeout /t 3 >nul

echo.
echo Starting services...
echo.

echo [1/6] Main Backend (Port 8000)...
start /min cmd /c "python main_backend.py 2>nul"
timeout /t 2 >nul

echo [2/6] Historical Backend (Port 8001)...
start /min cmd /c "python historical_backend.py 2>nul"
timeout /t 2 >nul

echo [3/6] ML Backend (Port 8002)...
start /min cmd /c "python ml_backend.py 2>nul"
timeout /t 2 >nul

echo [4/6] FinBERT Backend (Port 8003)...
start /min cmd /c "python finbert_backend.py 2>nul"
timeout /t 2 >nul

echo [5/6] Backtesting Backend (Port 8005)...
start /min cmd /c "python backtesting_backend.py 2>nul"
timeout /t 2 >nul

echo [6/6] Web Scraper Backend (Port 8006)...
echo      Trying simplified version first...
start /min cmd /c "python web_scraper_simple.py 2>nul"
timeout /t 3 >nul

echo.
echo Testing Web Scraper...
curl -s http://localhost:8006/health > nul 2>&1
if %errorlevel% neq 0 (
    echo Web scraper simple failed, trying original...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq web_scraper_simple.py*" 2>nul
    start /min cmd /c "python web_scraper_backend.py 2>nul"
    timeout /t 3 >nul
)

echo.
echo ================================================================================
echo ALL SERVICES STARTED
echo ================================================================================
echo.
echo Services Running:
echo - Main Backend:      http://localhost:8000
echo - Historical:        http://localhost:8001
echo - ML Backend:        http://localhost:8002
echo - FinBERT:          http://localhost:8003
echo - Backtesting:      http://localhost:8005
echo - Web Scraper:      http://localhost:8006
echo.
echo Testing Web Scraper...
echo.

python -c "import requests; r=requests.get('http://localhost:8006/health', timeout=5); print('Web Scraper Status:', r.json() if r.status_code==200 else 'NOT RUNNING')" 2>nul

echo.
echo Open in browser:
echo - Main Dashboard:    http://localhost:8000
echo - Sentiment Scraper: http://localhost:8000/sentiment_scraper.html
echo.
pause