@echo off
title Windows 11 Stock Tracker - Enterprise Edition
color 0A

echo ============================================================
echo     WINDOWS 11 STOCK TRACKER - ENTERPRISE EDITION
echo ============================================================
echo.
echo Initializing SQLite Database for 100x faster backtesting...
echo.

REM Initialize SQLite database
python -c "from historical_data_manager import HistoricalDataManager; hdm = HistoricalDataManager(); print('SQLite database ready at:', hdm.data_dir)"

echo.
echo Starting backend server...
echo.
echo ============================================================
echo     Backend running on: http://localhost:8002
echo     Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the backend
python backend.py

pause