@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo EVENT RISK GUARD - WEB UI
echo ================================================================================
echo.
echo Starting web interface...
echo.
echo Once started, access the dashboard at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [WARNING] Flask not installed. Installing now...
    echo.
    python -m pip install flask flask-cors
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install Flask
        echo Please run: pip install flask flask-cors
        pause
        exit /b 1
    )
)

echo [INFO] Starting Flask web server...
echo.

REM Start the web UI
python web_ui.py

if errorlevel 1 (
    echo.
    echo [ERROR] Web UI failed to start
    echo.
    echo Common issues:
    echo   - Port 5000 already in use (close other applications)
    echo   - Python modules missing (run INSTALL.bat)
    echo   - Configuration file errors
    echo.
    pause
    exit /b 1
)
