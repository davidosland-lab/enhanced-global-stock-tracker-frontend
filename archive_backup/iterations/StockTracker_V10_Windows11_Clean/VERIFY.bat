@echo off
echo ========================================
echo StockTracker V10 - System Verification
echo ========================================
echo.

REM Activate virtual environment first
call venv\Scripts\activate.bat

echo Running diagnostics inside virtual environment...
python diagnose.py

pause