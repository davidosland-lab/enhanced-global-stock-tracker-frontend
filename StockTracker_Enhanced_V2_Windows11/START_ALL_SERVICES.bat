@echo off
title Stock Tracker Enhanced v2.0 - Complete System
cls

echo ================================================================================
echo              STOCK TRACKER ENHANCED v2.0 - COMPLETE SYSTEM
echo              Research-Based ML with 50x Performance Boost
echo ================================================================================
echo.
echo Starting all services...
echo.

REM Start Enhanced ML Service (Port 8000)
echo [1/3] Starting Enhanced ML Prediction System...
start /min cmd /c "python ml_prediction_backtesting_enhanced.py"
timeout /t 3 >nul

REM Start Indices Tracker (Port 8004) 
echo [2/3] Starting Global Indices Tracker...
start /min cmd /c "python indices_tracker_backend.py"
timeout /t 2 >nul

REM Start Performance Tracker (Port 8005)
echo [3/3] Starting Performance Tracker...
start /min cmd /c "python performance_tracker_backend.py"
timeout /t 2 >nul

echo.
echo ================================================================================
echo                         ALL SERVICES STARTED
echo ================================================================================
echo.
echo Services Running:
echo.
echo   [✓] Enhanced ML System    : http://localhost:8000
echo   [✓] Indices Tracker       : http://localhost:8004
echo   [✓] Performance Tracker   : http://localhost:8005
echo.
echo Features Available:
echo   • Support Vector Machines (SVM)
echo   • Neural Networks
echo   • Ensemble Learning
echo   • 50+ Technical Indicators
echo   • SQLite Cache (50x faster)
echo   • Real FinBERT Sentiment
echo   • $100K Backtesting
echo   • Market Regime Detection
echo.
echo ================================================================================
echo.
echo Opening main interface in browser...
timeout /t 2 >nul

REM Open the main interface
start http://localhost:8000

echo.
echo Press any key to stop all services...
pause >nul

REM Stop all Python processes (careful with this)
echo.
echo Stopping all services...
taskkill /F /IM python.exe >nul 2>&1

echo All services stopped.
pause