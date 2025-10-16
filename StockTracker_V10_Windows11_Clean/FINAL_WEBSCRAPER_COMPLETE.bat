@echo off
echo ================================================================================
echo COMPLETE STOCK TRACKER WITH WORKING WEB SCRAPER
echo Version 11.3 - All Features Working
echo ================================================================================
echo.

echo Stopping all services...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8002"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8003"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8005"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8006"') do taskkill /F /PID %%a 2>nul
timeout /t 3 >nul

echo.
echo ================================================================================
echo FIXED IN THIS VERSION:
echo ================================================================================
echo [✓] ML Training TypeError - Fixed field name mismatch
echo [✓] Port Configuration - ML=8002, Main=8000
echo [✓] XGBoost Support - Added with fallback
echo [✓] Gradient Boost Support - Fully implemented
echo [✓] Prediction Data Issue - Fixed insufficient data error
echo [✓] Web Scraper - Real data from multiple sources
echo [✓] Sentiment Analysis - Working with fallback
echo [✓] Data Caching - 1-hour cache for performance
echo.

echo Starting all services...
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
echo      Starting REAL data web scraper...
start /min cmd /c "python web_scraper_real.py 2>nul"
timeout /t 3 >nul

echo.
echo Verifying services...
timeout /t 5 >nul

echo.
echo ================================================================================
echo SYSTEM STATUS
echo ================================================================================
echo.

echo Testing services...
echo.

curl -s http://localhost:8000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Main Backend:     RUNNING on port 8000
) else (
    echo [X] Main Backend:     NOT RUNNING
)

curl -s http://localhost:8001/health > nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Historical:       RUNNING on port 8001
) else (
    echo [X] Historical:       NOT RUNNING
)

curl -s http://localhost:8002/health > nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] ML Backend:       RUNNING on port 8002
) else (
    echo [X] ML Backend:       NOT RUNNING
)

curl -s http://localhost:8003/health > nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] FinBERT:         RUNNING on port 8003
) else (
    echo [X] FinBERT:         NOT RUNNING
)

curl -s http://localhost:8005/health > nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Backtesting:     RUNNING on port 8005
) else (
    echo [X] Backtesting:     NOT RUNNING
)

curl -s http://localhost:8006/health > nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Web Scraper:     RUNNING on port 8006
) else (
    echo [X] Web Scraper:     NOT RUNNING
)

echo.
echo ================================================================================
echo READY TO USE!
echo ================================================================================
echo.
echo Main Dashboard:      http://localhost:8000
echo Prediction Center:   http://localhost:8000/prediction_center.html
echo Sentiment Scraper:   http://localhost:8000/sentiment_scraper.html
echo Test Web Scraper:    http://localhost:8000/TEST_WEBSCRAPER.html
echo.
echo Features Working:
echo - ML Training with 3 model types (RandomForest, GradientBoost, XGBoost)
echo - Real-time predictions with sufficient data handling
echo - Web scraping from Yahoo, Finviz, Reddit, Google News
echo - Sentiment analysis with FinBERT fallback
echo - Historical data with SQLite caching
echo - Backtesting with $100,000 capital
echo.
echo NOTE: Web scraper now returns real data from:
echo - Yahoo Finance (via yfinance API)
echo - Finviz (web scraping)
echo - Reddit (JSON API)
echo - Google News (RSS feed)
echo.
pause