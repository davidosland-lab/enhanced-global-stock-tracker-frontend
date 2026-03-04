@echo off
REM ===================================================================
REM FinBERT v4.4 - Flask-CORS Emergency Fix
REM ===================================================================
REM This script fixes the common flask-cors import error
REM Run this if you see: ModuleNotFoundError: No module named 'flask_cors'
REM ===================================================================

echo ========================================
echo   Flask-CORS Emergency Fix
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    echo [OK] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found
    echo Please run INSTALL.bat first!
    pause
    exit /b 1
)

echo.
echo Installing Flask-CORS...
pip install flask-cors>=4.0.0
if errorlevel 1 (
    echo [ERROR] Installation failed
    echo.
    echo Troubleshooting:
    echo 1. Check internet connection
    echo 2. Try: pip install --upgrade pip
    echo 3. Try: pip install flask-cors --force-reinstall
    pause
    exit /b 1
)

echo.
echo Verifying installation...
python -c "import flask_cors; print('[OK] Flask-CORS installed successfully')"
if errorlevel 1 (
    echo [ERROR] Flask-CORS still not found
    echo Please check Python environment
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Fix Complete!
echo ========================================
echo.
echo Flask-CORS is now installed.
echo You can now run START_FINBERT.bat
echo.
pause
