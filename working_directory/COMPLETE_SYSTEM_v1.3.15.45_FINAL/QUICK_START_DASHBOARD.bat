@echo off
REM ============================================================================
REM SIMPLE AUTO-DEPS LAUNCHER - v1.3.15.58
REM ============================================================================
REM Simplified launcher that installs dependencies then starts dashboard directly
REM ============================================================================

echo.
echo ============================================================================
echo   AUTO-DEPENDENCY INSTALLER + DASHBOARD LAUNCHER
echo ============================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo [1/2] Checking and installing dependencies...
echo.

REM Detect virtual environment
set PIP_CMD=pip
IF EXIST "venv\Scripts\pip.exe" (
    echo [INFO] Using virtual environment: venv
    set PIP_CMD=venv\Scripts\pip
) ELSE (
    echo [INFO] Using system Python
)

REM Quick dependency check and install
echo.
echo Checking dependencies...

REM Check scikit-learn (most likely missing)
%PIP_CMD% show scikit-learn >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Installing scikit-learn...
    %PIP_CMD% install scikit-learn --quiet
    IF ERRORLEVEL 1 (
        echo [WARN] Failed to install scikit-learn
    ) ELSE (
        echo [OK] scikit-learn installed
    )
) ELSE (
    echo [OK] scikit-learn already installed
)

REM Check Keras
%PIP_CMD% show keras >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Installing Keras...
    %PIP_CMD% install keras --quiet
    IF ERRORLEVEL 1 (
        echo [WARN] Failed to install Keras
    ) ELSE (
        echo [OK] Keras installed
    )
) ELSE (
    echo [OK] Keras already installed
)

REM Check PyTorch
%PIP_CMD% show torch >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Installing PyTorch (this may take 2-5 minutes)...
    %PIP_CMD% install torch --index-url https://download.pytorch.org/whl/cpu --quiet
    IF ERRORLEVEL 1 (
        echo [WARN] Failed to install PyTorch
    ) ELSE (
        echo [OK] PyTorch installed
    )
) ELSE (
    echo [OK] PyTorch already installed
)

REM Set KERAS_BACKEND
IF NOT "%KERAS_BACKEND%"=="torch" (
    echo [*] Setting KERAS_BACKEND=torch...
    set KERAS_BACKEND=torch
    setx KERAS_BACKEND torch >nul 2>&1
    echo [OK] KERAS_BACKEND set
) ELSE (
    echo [OK] KERAS_BACKEND already set
)

echo.
echo ============================================================================
echo [2/2] Starting Unified Trading Dashboard...
echo ============================================================================
echo.
echo Dashboard will open at: http://localhost:8050
echo Press Ctrl+C to stop
echo.

REM Activate venv if it exists
IF EXIST "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Start the dashboard directly
python unified_trading_dashboard.py

echo.
echo Dashboard stopped.
pause
