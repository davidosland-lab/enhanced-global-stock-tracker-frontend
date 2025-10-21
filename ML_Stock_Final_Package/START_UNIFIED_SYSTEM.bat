@echo off
echo ============================================================
echo         ML STOCK PREDICTOR - UNIFIED SYSTEM LAUNCHER
echo ============================================================
echo.
echo Starting unified ML Stock Prediction system...
echo.
echo Features:
echo   - Yahoo Finance (Primary)
echo   - Alpha Vantage (Backup with your API key)
echo   - Automatic source switching on failure
echo   - ML Models: Random Forest, XGBoost, Gradient Boosting
echo   - MCP Server for AI Assistant integration
echo   - Web Interface on http://localhost:8000
echo.
echo ============================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

:: Clear any corrupted cache
echo [1/4] Clearing cache...
rmdir /s /q "%LOCALAPPDATA%\py-cache" 2>nul
del /q *.db 2>nul
echo        Cache cleared

:: Check for required packages
echo [2/4] Checking dependencies...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo.
    echo Installing required packages...
    pip install -r requirements_windows_py312.txt
)

:: Test configuration
echo [3/4] Testing configuration...
python -c "from config import ALPHA_VANTAGE_API_KEY; print(f'       API Key configured: {ALPHA_VANTAGE_API_KEY[:8]}...')" 2>nul
if errorlevel 1 (
    echo        Warning: Config file issue, using defaults
) else (
    echo        Configuration loaded successfully
)

:: Start the unified system
echo [4/4] Launching unified ML system...
echo.
echo ============================================================
echo System starting on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

:: Launch the unified system
python unified_ml_system.py

:: If server exits, show message
echo.
echo ============================================================
echo Server stopped. 
echo ============================================================
pause