@echo off
cls
echo ============================================================
echo Stock Tracker - Installing Python Requirements
echo ============================================================
echo.
echo This will install all required Python packages.
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Installing required packages...
echo ============================================================
echo.

echo Installing core packages...
pip install fastapi uvicorn python-multipart aiofiles

echo.
echo Installing data packages...
pip install yfinance pandas numpy

echo.
echo Installing ML packages (optional but recommended)...
pip install scikit-learn

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo All required packages have been installed.
echo You can now run START_FIXED_SERVICES.bat to start the application.
echo.
pause