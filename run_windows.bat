@echo off
REM Quick run script for Windows 11
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set FLASK_SKIP_DOTENV=1

if exist venv (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Running setup first...
    call setup_windows.bat
    exit /b
)

echo Starting Unified Stock Analysis System...
echo Access at: http://localhost:8000
echo.
python unified_stock_professional.py