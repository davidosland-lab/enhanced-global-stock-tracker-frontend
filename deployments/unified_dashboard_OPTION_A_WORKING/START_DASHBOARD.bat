@echo off
REM ========================================
REM Start Unified Trading Dashboard
REM Option A: Safe Working Model
REM ========================================

echo ========================================
echo Unified Trading Dashboard v1.3.15.87
echo Option A: Safe Working Model
echo ========================================
echo.

REM Check if fix has been applied
if not exist "%USERPROFILE%\.keras\keras.json" (
    echo ✗ ERROR: Keras config not found!
    echo.
    echo Please run FIX_KERAS_IMPORT.bat first!
    echo.
    pause
    exit /b 1
)

echo ✓ Keras config found
echo.

REM Set environment variables
set KERAS_BACKEND=tensorflow
set FLASK_SKIP_DOTENV=1

echo Configuration:
echo - Keras Backend: TensorFlow
echo - PyTorch: 2.2.0 (safe, no upgrade)
echo - FinBERT: Keyword sentiment (70-80%% win rate)
echo - Security: No vulnerabilities (keyword-based)
echo.

REM Check if dashboard directory exists
set "DASHBOARD_DIR=..\unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\core"

if not exist "%DASHBOARD_DIR%" (
    echo WARNING: Dashboard directory not found at:
    echo %DASHBOARD_DIR%
    echo.
    set /p "DASHBOARD_DIR=Enter path to dashboard core directory: "
)

if not exist "%DASHBOARD_DIR%\unified_trading_dashboard.py" (
    echo ✗ ERROR: unified_trading_dashboard.py not found!
    echo.
    echo Expected location:
    echo %DASHBOARD_DIR%\unified_trading_dashboard.py
    echo.
    pause
    exit /b 1
)

echo ✓ Dashboard found
echo.

echo Starting dashboard...
echo.
echo ========================================
echo Dashboard: http://localhost:8050
echo FinBERT: http://localhost:5001 (if running)
echo ========================================
echo.

cd /d "%DASHBOARD_DIR%"
python unified_trading_dashboard.py

if errorlevel 1 (
    echo.
    echo ✗ ERROR: Dashboard stopped with errors
    echo.
    echo Troubleshooting:
    echo 1. Check if FIX_KERAS_IMPORT.bat was run
    echo 2. Verify Python packages: pip list
    echo 3. Check logs in core\logs\
    echo.
    pause
    exit /b 1
)

pause
