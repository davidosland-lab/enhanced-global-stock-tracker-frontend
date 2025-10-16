@echo off
title Stock Tracker - Starting All Original Enhanced Modules
color 0A

echo ===============================================================
echo    STARTING ALL ORIGINAL ENHANCED MODULES
echo    This will load each module from its separate Python file
echo ===============================================================
echo.

:: Check if the enhanced module files exist
if not exist ml_backend_enhanced_finbert.py (
    echo ERROR: ml_backend_enhanced_finbert.py not found!
    echo Please ensure all module files are in this directory
    pause
    exit /b 1
)

:: Kill any existing processes on our ports
echo Cleaning up any existing services...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8003') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8004') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8005') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8006') do taskkill /PID %%a /F >nul 2>&1

echo.
echo Starting all enhanced modules...
echo ===============================================================
echo.

:: Start ML Backend with FinBERT (Port 8002)
echo [1/6] Starting ML Backend with FinBERT (Port 8002)
echo      File: ml_backend_enhanced_finbert.py
start /min cmd /c "title ML Backend && python ml_backend_enhanced_finbert.py"
timeout /t 3 /nobreak >nul

:: Start Document Analyzer (Port 8003)
echo [2/6] Starting Document Analyzer (Port 8003)
echo      File: finbert_backend.py
start /min cmd /c "title Document Analyzer && python finbert_backend.py"
timeout /t 2 /nobreak >nul

:: Start Historical Data with SQLite (Port 8004)
echo [3/6] Starting Historical Data Backend (Port 8004)
echo      File: historical_backend_sqlite.py
start /min cmd /c "title Historical Data && python historical_backend_sqlite.py"
timeout /t 2 /nobreak >nul

:: Start Backtesting Engine (Port 8005)
echo [4/6] Starting Backtesting Engine (Port 8005)
echo      File: backtesting_enhanced.py
start /min cmd /c "title Backtesting && python backtesting_enhanced.py"
timeout /t 2 /nobreak >nul

:: Start Enhanced Global Scraper (Port 8006)
echo [5/6] Starting Global Sentiment Scraper (Port 8006)
echo      File: enhanced_global_scraper.py
start /min cmd /c "title Web Scraper && python enhanced_global_scraper.py"
timeout /t 2 /nobreak >nul

:: Start Orchestrator (Port 8000)
echo [6/6] Starting Orchestrator (Port 8000)
echo      File: orchestrator_backend.py
echo      This connects all modules together
start /min cmd /c "title Orchestrator && python orchestrator_backend.py"
timeout /t 3 /nobreak >nul

echo.
echo ===============================================================
echo    ALL ORIGINAL MODULES STARTED
echo ===============================================================
echo.
echo Module Status:
echo --------------
echo ML Backend:       http://localhost:8002 (ml_backend_enhanced_finbert.py)
echo Document:         http://localhost:8003 (finbert_backend.py)
echo Historical:       http://localhost:8004 (historical_backend_sqlite.py)
echo Backtesting:      http://localhost:8005 (backtesting_enhanced.py)
echo Scraper:          http://localhost:8006 (enhanced_global_scraper.py)
echo ORCHESTRATOR:     http://localhost:8000 (orchestrator_backend.py)
echo.
echo The orchestrator at port 8000 connects all modules together
echo.
echo Waiting for all services to initialize...
timeout /t 5 /nobreak >nul

:: Open browser
echo Opening browser...
start http://localhost:8000/prediction_center_fixed.html

echo.
echo ===============================================================
echo    SYSTEM READY - Using Original Enhanced Modules
echo ===============================================================
echo.
echo All your original enhanced Python modules are now running:
echo - Real FinBERT from ml_backend_enhanced_finbert.py
echo - Global scraping from enhanced_global_scraper.py
echo - SQLite caching from historical_backend_sqlite.py
echo - $100k backtesting from backtesting_enhanced.py
echo.
echo To stop all services, run STOP_ALL_SERVICES.bat
echo.
pause