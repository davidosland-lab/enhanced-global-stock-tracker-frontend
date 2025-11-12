@echo off
cls
echo ============================================================
echo    CLEAN INSTALLATION - STOCK ANALYSIS SYSTEM
echo ============================================================
echo.
echo This will remove any existing installation and start fresh.
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Removing old virtual environment...
if exist "venv\" (
    rmdir /s /q venv 2>nul
    echo [OK] Old environment removed
)

echo.
echo Creating new virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to create virtual environment!
    echo.
    echo Try running these commands manually:
    echo   1. python -m pip install --upgrade pip
    echo   2. python -m pip install virtualenv
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

echo Activating environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing required packages...
echo This will take 2-3 minutes...
echo.

REM Install packages one by one for better error handling
echo Installing Flask...
pip install flask==3.0.0

echo Installing Flask-CORS...
pip install flask-cors==4.0.0

echo Installing yfinance...
pip install yfinance==0.2.33

echo Installing pandas...
pip install pandas==2.1.4

echo Installing numpy...
pip install numpy==1.26.2

echo Installing plotly...
pip install plotly==5.18.0

echo Installing requests...
pip install requests==2.31.0

echo Installing scikit-learn...
pip install scikit-learn==1.3.2

echo.
echo ============================================================
echo    INSTALLATION COMPLETE!
echo ============================================================
echo.
echo You can now run start.bat to launch the application.
echo.
pause