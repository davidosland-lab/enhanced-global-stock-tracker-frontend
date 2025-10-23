@echo off
echo ============================================
echo   Complete Stock Tracker - Windows 11
echo   Starting on http://localhost:8002
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

echo.
echo [2/4] Installing/Updating dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
echo [3/4] Initializing Historical Data Manager...
python -c "from historical_data_manager import HistoricalDataManager; print('Historical Data Manager: OK')" 2>nul
if errorlevel 1 (
    echo Note: Historical Data Manager will initialize on first run
)

echo.
echo [4/4] Starting backend server on port 8002...
echo.
echo ============================================
echo   Server starting on http://localhost:8002
echo   Press Ctrl+C to stop the server
echo ============================================
echo.

REM Start the backend server
python backend.py

pause