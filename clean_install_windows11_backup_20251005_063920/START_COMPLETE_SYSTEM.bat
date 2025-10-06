@echo off
echo ============================================
echo    COMPLETE STOCK TRACKER SYSTEM
echo ============================================
echo.
echo Starting both Backend API and Frontend...
echo.

:: Start backend in new window
start "Stock Tracker Backend" cmd /k "cd /d C:\StockTrack\Complete_Stock_Tracker_Windows11 && python backend.py"

:: Wait for backend to start
timeout /t 3 /nobreak > nul

:: Start frontend server
echo Starting Frontend Server on http://localhost:8080
python SERVE_FRONTEND.py

pause