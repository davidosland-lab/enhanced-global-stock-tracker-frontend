@echo off
REM ============================================================================
REM FinBERT v4.0 - Parameter Optimization Quick Start
REM ============================================================================

echo.
echo ========================================================================
echo   FinBERT v4.0 - Parameter Optimization Quick Start
echo ========================================================================
echo.
echo This will start the FinBERT server with parameter optimization enabled.
echo.
echo Features available:
echo   - Parameter Optimization (Grid and Random Search)
echo   - Single Stock Backtesting
echo   - Portfolio Backtesting
echo   - LSTM Predictions
echo   - Technical Analysis
echo.
echo Starting server on http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Dependencies not installed!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

REM Start the application
echo Starting FinBERT v4.0 Parameter Optimization Edition...
echo.
python app_finbert_v4_dev.py

REM If server stops
echo.
echo Server stopped.
pause
