@echo off
echo ========================================
echo GSMT Enhanced Stock Tracker Installation
echo Windows 11 Standalone Package v3.0
echo ========================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing dependencies...
pip install fastapi==0.104.1 uvicorn==0.24.0 yfinance==0.2.33 numpy==1.24.3 pandas==2.1.3 scikit-learn==1.3.2 aiofiles==23.2.1

echo [5/5] Creating shortcuts...
echo @echo off > start_server.bat
echo call venv\Scripts\activate.bat >> start_server.bat
echo echo Starting Enhanced ML Backend Server... >> start_server.bat
echo python enhanced_ml_backend.py >> start_server.bat
echo pause >> start_server.bat

echo @echo off > start_tracker.bat
echo echo Opening Stock Tracker in browser... >> start_tracker.bat
echo start http://localhost:8000/single_stock_tracker.html >> start_tracker.bat

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To use the application:
echo 1. Run 'start_server.bat' to start the backend server
echo 2. Run 'start_tracker.bat' to open the web interface
echo.
echo Or manually:
echo 1. Activate venv: venv\Scripts\activate.bat
echo 2. Start server: python enhanced_ml_backend.py
echo 3. Open browser: http://localhost:8000
echo.
pause