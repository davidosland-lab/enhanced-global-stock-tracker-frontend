@echo off
REM ============================================================================
REM SIMPLE WORKING LAUNCHER - v1.3.15.59.2
REM ============================================================================

cls
echo.
echo ========================================================================
echo   COMPLETE REGIME TRADING SYSTEM v1.3.15.59
echo ========================================================================
echo.

REM Detect virtual environment
IF EXIST "venv\Scripts\pip.exe" (
    set PIP_CMD=venv\Scripts\pip
    set PYTHON_CMD=venv\Scripts\python
    echo [INFO] Using virtual environment
) ELSE (
    set PIP_CMD=pip
    set PYTHON_CMD=python
    echo [INFO] Using system Python
)

echo.
echo ========================================================================
echo   DEPENDENCY CHECK
echo ========================================================================
echo.

REM Check and install scikit-learn
%PIP_CMD% show scikit-learn >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Installing scikit-learn...
    %PIP_CMD% install scikit-learn --quiet
    echo [OK] Installed
) ELSE (
    echo [OK] scikit-learn ready
)

REM Check Keras
%PIP_CMD% show keras >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Installing Keras...
    %PIP_CMD% install keras --quiet
    echo [OK] Installed
) ELSE (
    echo [OK] Keras ready
)

REM Check PyTorch
%PIP_CMD% show torch >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Installing PyTorch (2GB, takes 2-5 min)...
    %PIP_CMD% install torch --index-url https://download.pytorch.org/whl/cpu --quiet
    echo [OK] Installed
) ELSE (
    echo [OK] PyTorch ready
)

REM Set KERAS_BACKEND
IF NOT "%KERAS_BACKEND%"=="torch" (
    set KERAS_BACKEND=torch
    setx KERAS_BACKEND torch >nul 2>&1
)

echo.
echo [SUCCESS] All dependencies ready!
echo.

:menu
cls
echo.
echo ========================================================================
echo   MAIN MENU
echo ========================================================================
echo.
echo   1. Start Dashboard (Recommended)
echo   2. Run AU Pipeline
echo   3. Run US Pipeline
echo   4. Run UK Pipeline
echo   5. View System Status
echo   0. Exit
echo.
echo ========================================================================
echo.

set /p choice="Select option (0-5): "

IF "%choice%"=="1" goto dashboard
IF "%choice%"=="2" goto au_pipeline
IF "%choice%"=="3" goto us_pipeline
IF "%choice%"=="4" goto uk_pipeline
IF "%choice%"=="5" goto status
IF "%choice%"=="0" goto exit
echo Invalid option!
timeout /t 2 >nul
goto menu

:dashboard
cls
echo.
echo ========================================================================
echo   STARTING DASHBOARD
echo ========================================================================
echo.
echo URL: http://localhost:8050
echo Press Ctrl+C to stop
echo.
%PYTHON_CMD% unified_trading_dashboard.py
pause
goto menu

:au_pipeline
cls
echo.
echo ========================================================================
echo   AU PIPELINE
echo ========================================================================
echo.
IF EXIST "run_au_pipeline.py" (
    %PYTHON_CMD% run_au_pipeline.py
) ELSE (
    echo File not found: run_au_pipeline.py
)
pause
goto menu

:us_pipeline
cls
echo.
echo ========================================================================
echo   US PIPELINE
echo ========================================================================
echo.
IF EXIST "run_us_full_pipeline.py" (
    %PYTHON_CMD% run_us_full_pipeline.py
) ELSE (
    echo File not found: run_us_full_pipeline.py
)
pause
goto menu

:uk_pipeline
cls
echo.
echo ========================================================================
echo   UK PIPELINE
echo ========================================================================
echo.
IF EXIST "run_uk_pipeline.py" (
    %PYTHON_CMD% run_uk_pipeline.py
) ELSE (
    echo File not found: run_uk_pipeline.py
)
pause
goto menu

:status
cls
echo.
echo ========================================================================
echo   SYSTEM STATUS
echo ========================================================================
echo.
echo Python: 
%PYTHON_CMD% --version
echo.
echo Dependencies:
%PIP_CMD% show keras 2>nul | findstr Version
%PIP_CMD% show torch 2>nul | findstr Version
%PIP_CMD% show scikit-learn 2>nul | findstr Version
echo.
echo KERAS_BACKEND: %KERAS_BACKEND%
echo.
pause
goto menu

:exit
cls
echo.
echo Exiting...
echo.
timeout /t 2 >nul
exit /b 0
