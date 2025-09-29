@echo off
title GSMT Complete System - All Modules Working
color 0A
cls

echo ================================================================
echo          GSMT STOCK TRACKER v8.1.3 - COMPLETE SYSTEM
echo              ALL MODULES WITH MARKET DATA SERVER
echo ================================================================
echo.
echo This will start the complete GSMT system with:
echo.
echo   ✓ Market Data Server (Real-time simulation)
echo   ✓ Global Indices Tracker (Asia, Europe, Americas)
echo   ✓ Single Stock Track & Predict
echo   ✓ CBA Banking Intelligence
echo   ✓ Technical Analysis Engine
echo   ✓ ML Predictions (LSTM, GRU, Transformer, GNN)
echo   ✓ Document Intelligence
echo   ✓ Performance Dashboard
echo   ✓ API Integration
echo.
echo ================================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo [✓] Python detected
python --version
echo.

:: Install dependencies if needed
echo Checking dependencies...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install fastapi uvicorn --quiet --no-warn-script-location
)

echo.
echo ================================================================
echo Starting GSMT Complete System...
echo ================================================================
echo.

:: Kill any existing Python processes on port 8000
echo [1] Clearing port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start the market data server
echo [2] Starting Market Data Server...
start "GSMT Market Server" /min cmd /c "python backend\market_data_server.py"

:: Wait for server to initialize
echo [3] Waiting for server initialization...
timeout /t 5 /nobreak >nul

:: Test server connection
echo [4] Testing server connection...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing | Out-Null; Write-Host '[✓] Server is running' -ForegroundColor Green } catch { Write-Host '[!] Server starting slowly, please wait...' -ForegroundColor Yellow }"
) else (
    echo [✓] Server is running
)

echo.
echo [5] Opening Complete Dashboard...
timeout /t 2 /nobreak >nul

:: Open the comprehensive dashboard
start "" "frontend\comprehensive_dashboard.html"

:: Also open the indices tracker
timeout /t 1 /nobreak >nul
start "" "frontend\indices_tracker.html"

echo.
echo ================================================================
echo           ✓ GSMT COMPLETE SYSTEM LAUNCHED SUCCESSFULLY!
echo ================================================================
echo.
echo Server Status:
echo   - Market Data Server: http://localhost:8000
echo   - Health Check: http://localhost:8000/health
echo   - API Docs: http://localhost:8000/docs
echo.
echo Dashboards Opened:
echo   - Comprehensive Dashboard (All Modules)
echo   - Global Indices Tracker (Real-time Markets)
echo.
echo Available Modules:
echo   ✓ Global Indices - Track 18 major indices
echo   ✓ Single Stock - ML predictions with Phase 3 & 4
echo   ✓ CBA Banking - Central bank analysis
echo   ✓ Technical Analysis - RSI, MACD, Bollinger Bands
echo   ✓ ML Predictions - 5 models including GNN
echo   ✓ Performance Metrics - Real-time accuracy tracking
echo.
echo Tips:
echo   - Data updates every 5 minutes automatically
echo   - All modules work offline with simulated data
echo   - Markets show correct open/close status by timezone
echo.
echo To stop: Close this window or press Ctrl+C
echo ================================================================
echo.
pause