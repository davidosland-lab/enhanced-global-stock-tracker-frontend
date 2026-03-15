@echo off
REM ============================================================================
REM DIAGNOSTIC LAUNCHER - Shows exactly what's happening
REM ============================================================================

echo.
echo ============================================================================
echo   DIAGNOSTIC LAUNCHER
echo ============================================================================
echo.

REM Show current directory
echo Current directory: %CD%
echo.

REM Check for files
echo Checking for required files...
echo.

IF EXIST "AUTO_INSTALL_DEPENDENCIES.bat" (
    echo [OK] AUTO_INSTALL_DEPENDENCIES.bat found
) ELSE (
    echo [MISSING] AUTO_INSTALL_DEPENDENCIES.bat
)

IF EXIST "LAUNCH_COMPLETE_SYSTEM.bat" (
    echo [OK] LAUNCH_COMPLETE_SYSTEM.bat found
) ELSE (
    echo [MISSING] LAUNCH_COMPLETE_SYSTEM.bat
)

IF EXIST "unified_trading_dashboard.py" (
    echo [OK] unified_trading_dashboard.py found
) ELSE (
    echo [MISSING] unified_trading_dashboard.py
)

IF EXIST "complete_workflow.py" (
    echo [OK] complete_workflow.py found
) ELSE (
    echo [MISSING] complete_workflow.py
)

IF EXIST "venv\Scripts\python.exe" (
    echo [OK] Virtual environment found
) ELSE (
    echo [MISSING] Virtual environment
)

echo.
echo ============================================================================
echo   AVAILABLE .BAT FILES
echo ============================================================================
echo.
dir /b *.bat 2>nul

echo.
echo ============================================================================
echo   AVAILABLE .PY FILES
echo ============================================================================
echo.
dir /b *.py 2>nul

echo.
echo ============================================================================
echo   PYTHON VERSION
echo ============================================================================
echo.
python --version

echo.
echo ============================================================================
echo   VIRTUAL ENV PYTHON
echo ============================================================================
echo.
IF EXIST "venv\Scripts\python.exe" (
    venv\Scripts\python.exe --version
) ELSE (
    echo Virtual environment not found
)

echo.
echo ============================================================================
echo.
echo What would you like to do?
echo.
echo 1. Install dependencies only
echo 2. Start dashboard directly (no dependency check)
echo 3. Install dependencies then start dashboard
echo 4. Exit
echo.
set /p choice="Enter choice (1-4): "

IF "%choice%"=="1" (
    echo.
    echo Installing dependencies...
    call AUTO_INSTALL_DEPENDENCIES.bat
    pause
) ELSE IF "%choice%"=="2" (
    echo.
    echo Starting dashboard...
    IF EXIST "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
    python unified_trading_dashboard.py
) ELSE IF "%choice%"=="3" (
    echo.
    echo Installing dependencies...
    call AUTO_INSTALL_DEPENDENCIES.bat
    echo.
    echo Starting dashboard...
    IF EXIST "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
    python unified_trading_dashboard.py
) ELSE (
    echo Exiting...
)
