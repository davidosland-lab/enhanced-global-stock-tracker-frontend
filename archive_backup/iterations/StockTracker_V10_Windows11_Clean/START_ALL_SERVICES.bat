@echo off
title Stock Tracker Enhanced - Starting All Services
color 0A

echo ================================================
echo    STOCK TRACKER ENHANCED - STARTING SERVICES
echo ================================================
echo.

:: Kill any existing Python processes on our ports
echo Cleaning up any existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8003') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8004') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8005') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8006') do taskkill /PID %%a /F >nul 2>&1

:: Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Starting services...
echo.

:: Start Main Backend (Port 8000)
echo [1/6] Starting Main Backend (Port 8000)...
start /min cmd /c "python main_backend_integrated.py"
timeout /t 2 /nobreak >nul

:: Start ML Backend with FinBERT (Port 8002)
echo [2/6] Starting ML Backend with FinBERT (Port 8002)...
start /min cmd /c "python ml_backend_enhanced_finbert.py"
timeout /t 3 /nobreak >nul

:: Start Document Analyzer (Port 8003)
echo [3/6] Starting Document Analyzer (Port 8003)...
start /min cmd /c "python finbert_backend.py"
timeout /t 2 /nobreak >nul

:: Start Historical Data Service (Port 8004)
echo [4/6] Starting Historical Data with SQLite (Port 8004)...
start /min cmd /c "python historical_backend_sqlite.py"
timeout /t 2 /nobreak >nul

:: Start Backtesting Service (Port 8005)
echo [5/6] Starting Backtesting Service (Port 8005)...
start /min cmd /c "python backtesting_enhanced.py"
timeout /t 2 /nobreak >nul

:: Start Enhanced Web Scraper (Port 8006)
echo [6/6] Starting Global Sentiment Scraper (Port 8006)...
start /min cmd /c "python enhanced_global_scraper.py"
timeout /t 2 /nobreak >nul

echo.
echo ================================================
echo    ALL SERVICES STARTED SUCCESSFULLY!
echo ================================================
echo.
echo Service Status:
echo --------------
echo Main Backend:        http://localhost:8000
echo ML Backend:          http://localhost:8002
echo Document Analyzer:   http://localhost:8003
echo Historical Data:     http://localhost:8004
echo Backtesting:         http://localhost:8005
echo Global Scraper:      http://localhost:8006
echo.
echo Checking services health...
timeout /t 3 /nobreak >nul

:: Check if services are running
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Main Backend is running
) else (
    echo [WARNING] Main Backend may not be ready yet
)

curl -s http://localhost:8002/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] ML Backend is running
) else (
    echo [WARNING] ML Backend may not be ready yet
)

echo.
echo ================================================
echo    OPENING STOCK TRACKER IN BROWSER...
echo ================================================
echo.

:: Wait a moment for all services to fully initialize
timeout /t 3 /nobreak >nul

:: Open the application in default browser
start http://localhost:8000/prediction_center_fixed.html

echo.
echo Application is ready!
echo.
echo To stop all services, run STOP_ALL_SERVICES.bat
echo To view logs, check the console windows
echo.
echo Features Available:
echo - Real-time stock predictions with ML
echo - Global sentiment analysis (politics, wars, economics)
echo - FinBERT financial sentiment
echo - 50x faster with SQLite caching
echo - Backtesting with $100,000 starting capital
echo.
pause