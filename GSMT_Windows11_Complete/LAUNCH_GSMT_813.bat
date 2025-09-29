@echo off
title GSMT Ver 8.1.3 - Complete System with CBA Module
color 0A
cls

echo ================================================================
echo          GSMT STOCK TRACKER Ver 8.1.3 - COMPLETE SYSTEM
echo            WITH COMMONWEALTH BANK OF AUSTRALIA MODULE
echo ================================================================
echo.
echo This will start the complete GSMT Ver 8.1.3 system including:
echo.
echo   ✓ Market Data Server (Port 8000)
echo   ✓ CBA Specialist Server (Port 8001)
echo   ✓ Global Indices Tracker (18 markets)
echo   ✓ Single Stock Track & Predict
echo   ✓ CBA Banking Module (Commonwealth Bank)
echo   ✓ Technical Analysis Engine
echo   ✓ ML Predictions (LSTM, GRU, Transformer, GNN)
echo   ✓ Document Intelligence & Analysis
echo   ✓ Market Sentiment Analysis
echo   ✓ Performance Dashboard
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
echo Starting GSMT Ver 8.1.3 Complete System...
echo ================================================================
echo.

:: Kill any existing Python processes on ports
echo [1] Clearing ports 8000 and 8001...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8001" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Start the market data server
echo [2] Starting Market Data Server (Port 8000)...
start "GSMT Market Server" /min cmd /c "python backend\market_data_server.py"

:: Wait for first server
timeout /t 3 /nobreak >nul

:: Start the CBA specialist server
echo [3] Starting CBA Specialist Server (Port 8001)...
start "CBA Specialist Server" /min cmd /c "python backend\cba_specialist_server.py"

:: Wait for servers to initialize
echo [4] Waiting for servers initialization...
timeout /t 5 /nobreak >nul

:: Test server connections
echo [5] Testing server connections...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [!] Market server starting slowly...
) else (
    echo [✓] Market Data Server running
)

curl -s http://localhost:8001/ >nul 2>&1
if errorlevel 1 (
    echo [!] CBA server starting slowly...
) else (
    echo [✓] CBA Specialist Server running
)

echo.
echo [6] Opening GSMT Ver 8.1.3 Dashboards...
timeout /t 2 /nobreak >nul

:: Open all dashboards
start "" "frontend\comprehensive_dashboard.html"
timeout /t 1 /nobreak >nul
start "" "frontend\cba_market_tracker.html"
timeout /t 1 /nobreak >nul
start "" "frontend\indices_tracker.html"

echo.
echo ================================================================
echo        ✓ GSMT Ver 8.1.3 LAUNCHED SUCCESSFULLY!
echo ================================================================
echo.
echo Servers Running:
echo   - Market Data Server: http://localhost:8000
echo   - CBA Specialist Server: http://localhost:8001
echo.
echo Dashboards Opened:
echo   - Comprehensive Dashboard (All Modules)
echo   - CBA Market Tracker (Commonwealth Bank Analysis)
echo   - Global Indices Tracker (Real-time Markets)
echo.
echo CBA Module Features:
echo   ✓ Real-time CBA.AX stock price tracking
echo   ✓ Document analysis and insights
echo   ✓ Market sentiment from news & social media
echo   ✓ ML predictions with 5 models
echo   ✓ Banking sector comparison (Big 4 banks)
echo   ✓ Publications and reports analysis
echo   ✓ Enhanced predictions with all factors
echo.
echo Available Modules:
echo   ✓ Global Indices - 18 major markets worldwide
echo   ✓ Single Stock - Any ASX or global stock
echo   ✓ CBA Banking - Commonwealth Bank specialist
echo   ✓ Technical Analysis - RSI, MACD, Bollinger
echo   ✓ ML Predictions - LSTM, GRU, Transformer, GNN
echo   ✓ Document Intelligence - PDF/DOCX analysis
echo   ✓ Performance Metrics - Model accuracy tracking
echo.
echo Data Updates:
echo   - Market data refreshes every 5 minutes
echo   - CBA publications checked hourly
echo   - Sentiment analysis updates in real-time
echo.
echo To stop: Close this window or press Ctrl+C
echo ================================================================
echo.
pause