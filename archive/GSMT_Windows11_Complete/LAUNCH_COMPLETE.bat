@echo off
title GSMT Complete Phase 4 Launcher
color 0A
cls

echo ================================================================
echo        GSMT STOCK TRACKER v8.1.3 - COMPLETE EDITION
echo            WITH ALL PHASE 3 & 4 MODULES RESTORED
echo ================================================================
echo.
echo This launcher will start the complete system with all modules:
echo.
echo   ✓ Global Indices Tracker (Ver-106)
echo   ✓ Single Stock Track & Predict (Phase 3 & 4)
echo   ✓ CBA Banking Intelligence 
echo   ✓ Technical Analysis Engine
echo   ✓ Unified Prediction Centre
echo   ✓ Document Intelligence
echo   ✓ API & Integration
echo   ✓ Performance Dashboard
echo   ✓ Phase 4 Technical Implementation
echo.
echo ================================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed!
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo Starting GSMT Complete System...
echo.

:: Start the main server in background
echo [1] Starting backend server...
start /min cmd /c "python backend\main_server.py"

:: Wait for server to start
echo [2] Waiting for server to initialize...
timeout /t 3 /nobreak >nul

:: Check if server is running
echo [3] Checking server status...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Server might be starting slowly.
    echo Please wait a moment and refresh the browser.
    echo.
)

:: Open the comprehensive dashboard
echo [4] Opening Complete Dashboard...
start "" "frontend\comprehensive_dashboard.html"

echo.
echo ================================================================
echo                    SYSTEM LAUNCHED SUCCESSFULLY!
echo ================================================================
echo.
echo The Complete Dashboard is now open in your browser.
echo.
echo Server running at: http://localhost:8000
echo Dashboard opened: frontend\comprehensive_dashboard.html
echo.
echo All modules are now accessible from the dashboard!
echo.
echo To stop the server: Close this window or press Ctrl+C
echo ================================================================
echo.
pause