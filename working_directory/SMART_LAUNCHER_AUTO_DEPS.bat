@echo off
REM ============================================================================
REM SMART LAUNCHER WITH AUTO-DEPENDENCIES - v1.3.15.58
REM ============================================================================
REM This launcher automatically checks and installs missing dependencies
REM before starting the system, ensuring LSTM neural networks work properly
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo   COMPLETE REGIME TRADING SYSTEM - SMART LAUNCHER v1.3.15.58
echo ============================================================================
echo.

REM Step 1: Auto-install dependencies if needed
echo [STEP 1] Checking dependencies...
echo.

IF EXIST "AUTO_INSTALL_DEPENDENCIES.bat" (
    call AUTO_INSTALL_DEPENDENCIES.bat
    IF ERRORLEVEL 1 (
        echo.
        echo [ERROR] Dependency check failed
        echo [INFO] System will continue but LSTM may use fallback mode
        echo.
        pause
    )
) ELSE (
    echo [WARN] AUTO_INSTALL_DEPENDENCIES.bat not found
    echo [INFO] Skipping automatic dependency installation
    echo.
)

echo.
echo ============================================================================
echo   STARTING SYSTEM
echo ============================================================================
echo.

REM Step 2: Run the original launcher
IF EXIST "LAUNCH_COMPLETE_SYSTEM.bat" (
    call LAUNCH_COMPLETE_SYSTEM.bat
) ELSE IF EXIST "complete_workflow.py" (
    python complete_workflow.py
) ELSE IF EXIST "unified_trading_dashboard.py" (
    echo [INFO] Launching Unified Trading Dashboard directly...
    python unified_trading_dashboard.py
) ELSE (
    echo [ERROR] Could not find system launcher
    echo.
    echo Available options:
    dir /b *.bat 2>nul
    dir /b *.py 2>nul
    echo.
    pause
    exit /b 1
)

endlocal
