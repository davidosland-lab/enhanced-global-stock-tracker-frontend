@echo off
cls
echo ============================================================
echo    STOCK ANALYSIS SYSTEM - WINDOWS 11
echo ============================================================
echo.
echo Launching with PowerShell for better compatibility...
echo.

REM Run PowerShell script with bypass execution policy
powershell -ExecutionPolicy Bypass -File "%~dp0run_powershell.ps1"

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo PowerShell method failed. Trying standard method...
    echo ============================================================
    echo.
    
    REM Fallback to standard batch approach
    cd /d "%~dp0"
    
    REM Check if venv exists and has python
    if exist "venv\Scripts\python.exe" (
        set PYTHON_CMD=venv\Scripts\python.exe
    ) else (
        set PYTHON_CMD=python
    )
    
    REM Set environment
    set FLASK_SKIP_DOTENV=1
    
    REM Start server
    echo Starting server at http://localhost:8000
    start "" "http://localhost:8000"
    %PYTHON_CMD% app.py
)

pause