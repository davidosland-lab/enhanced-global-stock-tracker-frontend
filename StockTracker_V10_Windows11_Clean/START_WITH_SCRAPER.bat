@echo off
echo ========================================
echo StockTracker V10 with Web Sentiment Scraper
echo ========================================
echo.

REM Kill existing processes
echo Cleaning up existing processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

REM Clear SSL
set SSL_CERT_FILE=
set SSL_CERT_DIR=
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install web scraping dependencies if needed
echo Checking web scraping dependencies...
pip show beautifulsoup4 >nul 2>&1 || pip install beautifulsoup4
pip show feedparser >nul 2>&1 || pip install feedparser
pip show lxml >nul 2>&1 || pip install lxml

echo.
echo Starting all services...
echo.

REM Start Main Backend on 8000
echo [1/6] Starting Main Backend (Port 8000)...
start "Main Backend - 8000" cmd /c "python main_backend.py"
timeout /t 3 >nul

REM Start ML Backend on 8002
echo [2/6] Starting ML Backend (Port 8002)...
start "ML Backend - 8002" cmd /c "python ml_backend.py"
timeout /t 3 >nul

REM Start FinBERT on 8003
echo [3/6] Starting FinBERT Backend (Port 8003)...
start "FinBERT - 8003" cmd /c "python finbert_backend.py"
timeout /t 3 >nul

REM Start Historical on 8004
echo [4/6] Starting Historical Backend (Port 8004)...
start "Historical - 8004" cmd /c "python historical_backend.py"
timeout /t 3 >nul

REM Start Backtesting on 8005
echo [5/6] Starting Backtesting Backend (Port 8005)...
start "Backtesting - 8005" cmd /c "python backtesting_backend.py"
timeout /t 3 >nul

REM Start Web Scraper on 8006
echo [6/6] Starting Web Scraper Backend (Port 8006)...
start "Web Scraper - 8006" cmd /c "python web_scraper_backend.py"
timeout /t 5 >nul

echo.
echo ========================================
echo All Services Started!
echo ========================================
echo.
echo Service URLs:
echo - Main Dashboard:      http://localhost:8000
echo - ML Backend:          http://localhost:8002
echo - FinBERT:            http://localhost:8003
echo - Historical:         http://localhost:8004
echo - Backtesting:        http://localhost:8005
echo - Web Scraper:        http://localhost:8006
echo.
echo Features:
echo - Sentiment Scraper:  http://localhost:8000/sentiment_scraper.html
echo - ML Predictions:     http://localhost:8000/prediction_center.html
echo.
echo Opening dashboard...
start http://localhost:8000
echo.
echo Press any key to exit...
pause >nul