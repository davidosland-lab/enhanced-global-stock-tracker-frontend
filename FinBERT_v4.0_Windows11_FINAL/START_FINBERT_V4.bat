@echo off
echo ========================================
echo FinBERT v4.0 - Stock Analysis System
echo ========================================
echo.

REM Check if virtual environment exists in main directory or scripts directory
if exist venv (
    set VENV_PATH=venv
) else if exist scripts\venv (
    set VENV_PATH=scripts\venv
) else (
    echo ERROR: Virtual environment not found!
    echo.
    echo Looked in:
    echo   - venv\
    echo   - scripts\venv\
    echo.
    echo Please run scripts\INSTALL_WINDOWS11.bat first.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment from %VENV_PATH%...
call %VENV_PATH%\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if main application exists
if not exist app_finbert_v4_dev.py (
    echo ERROR: app_finbert_v4_dev.py not found!
    echo.
    echo Make sure you're in the FinBERT_v4.0_Windows11_CLEAN directory.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo Starting FinBERT v4.0 server...
echo.
echo The application will be available at:
echo   http://127.0.0.1:5001
echo.
echo Press CTRL+C to stop the server
echo.

REM Start the Flask application
python app_finbert_v4_dev.py

REM If the server stops, show this message
echo.
echo Server stopped.
pause
