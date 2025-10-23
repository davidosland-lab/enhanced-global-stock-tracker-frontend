@echo off
echo ================================================================================
echo ML TRAINING FIX - Fixing Port Configuration Issue
echo ================================================================================
echo.

echo Step 1: Killing any processes on required ports...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8002"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8003"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8004"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8005"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8006"') do taskkill /F /PID %%a 2>nul
timeout /t 2 >nul

echo.
echo Step 2: Port Configuration has been fixed in prediction_center.html
echo - ML Backend: Port 8002 (was incorrectly set to 8003)
echo - Main Backend: Port 8000 (was incorrectly set to 8002)
echo.

echo Step 3: Starting all services with correct ports...
echo.

echo Starting Main Backend (Port 8000)...
start /min cmd /c "python main_backend.py"
timeout /t 3 >nul

echo Starting Historical Backend (Port 8001)...
start /min cmd /c "python historical_backend.py"
timeout /t 2 >nul

echo Starting ML Backend (Port 8002)...
start /min cmd /c "python ml_backend.py"
timeout /t 3 >nul

echo Starting FinBERT Backend (Port 8003)...
start /min cmd /c "python finbert_backend.py"
timeout /t 2 >nul

echo Starting Backtesting Backend (Port 8005)...
start /min cmd /c "python backtesting_backend.py"
timeout /t 2 >nul

echo Starting Web Scraper Backend (Port 8006)...
start /min cmd /c "python web_scraper_backend.py"
timeout /t 2 >nul

echo.
echo ================================================================================
echo SERVICES STARTED - Verifying Status...
echo ================================================================================
echo.

timeout /t 5 >nul

echo Testing ML Training Endpoint...
python test_ml_training.py

echo.
echo ================================================================================
echo FIX COMPLETE!
echo ================================================================================
echo.
echo Services Running:
echo - Main Backend:        http://localhost:8000
echo - Historical Backend:  http://localhost:8001  
echo - ML Backend:          http://localhost:8002
echo - FinBERT Backend:     http://localhost:8003
echo - Backtesting Backend: http://localhost:8005
echo - Web Scraper Backend: http://localhost:8006
echo.
echo Open in browser: http://localhost:8000
echo Go to Prediction Center to test ML training
echo.
pause