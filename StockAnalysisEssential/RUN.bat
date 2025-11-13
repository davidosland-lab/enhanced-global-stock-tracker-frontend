@echo off
echo ======================================================================
echo             STOCK ANALYSIS SYSTEM - WINDOWS 11
echo ======================================================================
echo.

REM Check if first run
if not exist "venv\" (
    echo First time setup detected. Installing...
    call install.bat
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment
set FLASK_SKIP_DOTENV=1

REM Start server
echo Starting server at: http://localhost:8000
echo.
start http://localhost:8000
python app.py

pause