@echo off
echo ========================================
echo FinBERT v4.0 - Stock Analysis System
echo ========================================
echo.

REM Remove problematic .env file if it exists
if exist .env (
    echo Removing problematic .env file...
    del .env
)

REM Set environment variable to disable .env file loading
set FLASK_SKIP_DOTENV=1

REM Check if virtual environment exists in main directory or scripts directory
if exist venv (
    set VENV_PATH=venv
) else if exist scripts\venv (
    set VENV_PATH=scripts\venv
) else (
    echo WARNING: Virtual environment not found!
    echo.
    echo Looked in:
    echo   - venv\
    echo   - scripts\venv\
    echo.
    echo Attempting to run with system Python...
    echo If this fails, please run INSTALL.bat first.
    echo.
    goto :SKIP_VENV
)

REM Activate virtual environment
echo Activating virtual environment from %VENV_PATH%...
call %VENV_PATH%\Scripts\activate.bat
if errorlevel 1 (
    echo WARNING: Failed to activate virtual environment
    echo Attempting to run with system Python...
    echo.
)

:SKIP_VENV

REM Check if main application exists
if not exist app_finbert_v4_dev.py (
    echo ERROR: app_finbert_v4_dev.py not found!
    echo.
    echo Make sure you're in the correct directory.
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

echo Starting FinBERT v4.0 server...
echo.
echo The application will be available at:
echo   http://127.0.0.1:5001
echo   http://localhost:5001
echo.
echo Press CTRL+C to stop the server
echo.

REM Start the Flask application
python app_finbert_v4_dev.py

REM If the server stops, show this message
echo.
echo Server stopped.
pause
