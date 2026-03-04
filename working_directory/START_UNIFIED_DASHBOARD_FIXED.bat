@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  START UNIFIED TRADING DASHBOARD - FIXED
REM  Finds and activates virtual environment automatically
REM ═══════════════════════════════════════════════════════════════════════════

REM Change to script directory
cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   STARTING UNIFIED TRADING DASHBOARD
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Try multiple possible virtual environment locations
set "VENV_FOUND=0"

REM Check location 1: venv\Scripts\activate.bat
if exist "venv\Scripts\activate.bat" (
    echo [*] Found virtual environment at: venv\Scripts\
    call venv\Scripts\activate.bat
    set "VENV_FOUND=1"
    goto :venv_activated
)

REM Check location 2: .venv\Scripts\activate.bat
if exist ".venv\Scripts\activate.bat" (
    echo [*] Found virtual environment at: .venv\Scripts\
    call .venv\Scripts\activate.bat
    set "VENV_FOUND=1"
    goto :venv_activated
)

REM Check location 3: env\Scripts\activate.bat
if exist "env\Scripts\activate.bat" (
    echo [*] Found virtual environment at: env\Scripts\
    call env\Scripts\activate.bat
    set "VENV_FOUND=1"
    goto :venv_activated
)

REM Check location 4: Try without virtual environment (use system Python)
echo [!] No virtual environment found - trying system Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH
    echo.
    echo Please ensure Python is installed and added to PATH
    echo Or create a virtual environment in one of these locations:
    echo   - venv\
    echo   - .venv\
    echo   - env\
    echo.
    pause
    exit /b 1
)
echo [OK] Using system Python
set "VENV_FOUND=1"
goto :venv_activated

:venv_activated
echo [OK] Python environment ready
echo.

REM Set Keras backend
echo [2/3] Setting environment variables...
set KERAS_BACKEND=torch
echo [OK] KERAS_BACKEND=torch
echo.

REM Check if dashboard file exists
if not exist "unified_trading_dashboard.py" (
    echo [ERROR] unified_trading_dashboard.py not found!
    echo.
    echo Current directory: %CD%
    echo.
    echo Please ensure you are running this from the correct directory.
    echo Expected file: unified_trading_dashboard.py
    echo.
    pause
    exit /b 1
)

REM Start dashboard
echo [3/3] Starting unified trading dashboard...
echo.
echo ───────────────────────────────────────────────────────────────────────────
echo   Dashboard will open at: http://localhost:8050
echo   Press Ctrl+C to stop the dashboard
echo ───────────────────────────────────────────────────────────────────────────
echo.

python unified_trading_dashboard.py

REM If dashboard exits with error
if errorlevel 1 (
    echo.
    echo ═══════════════════════════════════════════════════════════════════════════
    echo   Dashboard stopped with errors
    echo ═══════════════════════════════════════════════════════════════════════════
    echo.
    echo Common issues:
    echo   1. Missing dependencies - run: pip install dash plotly transformers
    echo   2. Port 8050 already in use - close other dashboard windows
    echo   3. Check logs above for specific error messages
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   Dashboard stopped successfully
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
