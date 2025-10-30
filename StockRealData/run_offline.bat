@echo off
cls
echo ============================================================
echo    STOCK ANALYSIS - OFFLINE MODE
echo ============================================================
echo.
echo This will create offline data and run the app with it.
echo Use this when Yahoo Finance and Alpha Vantage are blocked.
echo.

REM Use venv Python if available
if exist "venv\Scripts\python.exe" (
    set PYTHON_EXE=venv\Scripts\python.exe
) else (
    set PYTHON_EXE=python
)

REM Check if offline data exists
if not exist "offline_data" (
    echo Creating offline sample data...
    echo.
    %PYTHON_EXE% offline_data.py
    echo.
)

echo Starting server with offline data support...
echo.
echo Server URL: http://localhost:8000
echo.

REM Open browser
start "" "http://localhost:8000"

REM Run app with offline support
%PYTHON_EXE% app_with_offline.py

pause