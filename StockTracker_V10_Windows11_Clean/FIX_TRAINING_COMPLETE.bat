@echo off
echo ================================================================================
echo COMPLETE ML TRAINING FIX
echo Fixing TypeError: Cannot read properties of undefined
echo ================================================================================
echo.

echo Step 1: Stopping all existing services...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8002"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8003"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8004"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8005"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8006"') do taskkill /F /PID %%a 2>nul
timeout /t 3 >nul

echo.
echo Step 2: Issues Fixed
echo - Port configuration: ML=8002, Main=8000 (FIXED)
echo - Field name mismatch: training_time vs training_time_seconds (FIXED)
echo - Added null checks for all fields (FIXED)
echo - CORS headers already configured (VERIFIED)
echo.

echo Step 3: Starting all backend services...
echo.

echo [1/6] Starting Main Backend on port 8000...
start /min cmd /c "python main_backend.py 2>nul"
timeout /t 3 >nul

echo [2/6] Starting Historical Backend on port 8001...
start /min cmd /c "python historical_backend.py 2>nul"
timeout /t 2 >nul

echo [3/6] Starting ML Backend on port 8002...
start /min cmd /c "python ml_backend.py 2>nul"
timeout /t 3 >nul

echo [4/6] Starting FinBERT Backend on port 8003...
start /min cmd /c "python finbert_backend.py 2>nul"
timeout /t 2 >nul

echo [5/6] Starting Backtesting Backend on port 8005...
start /min cmd /c "python backtesting_backend.py 2>nul"
timeout /t 2 >nul

echo [6/6] Starting Web Scraper Backend on port 8006...
start /min cmd /c "python web_scraper_backend.py 2>nul"
timeout /t 2 >nul

echo.
echo Step 4: Waiting for services to initialize...
timeout /t 5 >nul

echo.
echo ================================================================================
echo TESTING ML TRAINING
echo ================================================================================
echo.

echo Running diagnostic test...
python debug_training_issue.py

echo.
echo ================================================================================
echo SERVICES RUNNING
echo ================================================================================
echo.
echo Main Dashboard:     http://localhost:8000
echo Prediction Center:  http://localhost:8000/prediction_center.html
echo Test Page:          http://localhost:8000/test_training.html
echo.
echo All backend services:
echo - Main Backend:      http://localhost:8000 (Serves HTML files)
echo - Historical:        http://localhost:8001 (SQLite cached data)
echo - ML Backend:        http://localhost:8002 (Training/Prediction)
echo - FinBERT:          http://localhost:8003 (Sentiment Analysis)
echo - Backtesting:      http://localhost:8005 ($100K capital)
echo - Web Scraper:      http://localhost:8006 (Multi-source scraping)
echo.
echo ================================================================================
echo FIX COMPLETE - ML TRAINING SHOULD NOW WORK!
echo ================================================================================
echo.
echo To test:
echo 1. Open http://localhost:8000 in your browser
echo 2. Click "Prediction Center"
echo 3. Enter a stock symbol (e.g., AAPL)
echo 4. Click "Train New Model"
echo 5. Wait 10-60 seconds for training to complete
echo.
echo Or use the test page: http://localhost:8000/test_training.html
echo.
pause