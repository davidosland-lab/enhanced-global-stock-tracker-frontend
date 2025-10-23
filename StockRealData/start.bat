@echo off
cls
echo ============================================================
echo    STOCK ANALYSIS SYSTEM - QUICK START
echo ============================================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run install_and_run.bat first.
    echo.
    pause
    exit /b 1
)

REM Activate environment
call venv\Scripts\activate.bat

REM Set environment
set FLASK_SKIP_DOTENV=1

REM Start server
echo Starting server at http://localhost:8000
start "" "http://localhost:8000"
python app.py

pause