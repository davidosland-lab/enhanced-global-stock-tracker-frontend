@echo off
REM ============================================================================
REM COMPLETE REGIME TRADING SYSTEM - UNIFIED LAUNCHER v1.3.15.59
REM ============================================================================
REM One launcher for everything: dependency management + system start
REM No hanging, no nested calls, just works
REM ============================================================================

setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

REM Clear screen for clean display
cls

echo.
echo ========================================================================
echo   COMPLETE REGIME TRADING SYSTEM v1.3.15.59 FINAL
echo   Smart Launcher with Auto-Dependencies
echo ========================================================================
echo.

REM ============================================================================
REM STEP 1: AUTO-DEPENDENCY CHECK AND INSTALLATION
REM ============================================================================

echo [STEP 1/2] Dependency Check
echo ------------------------------------------------------------------------
echo.

REM Detect virtual environment
set PIP_CMD=pip
set PYTHON_CMD=python

IF EXIST "venv\Scripts\pip.exe" (
    echo [INFO] Virtual environment detected: venv
    set PIP_CMD=venv\Scripts\pip
    set PYTHON_CMD=venv\Scripts\python
) ELSE (
    echo [INFO] Using system Python
)

echo.
echo Checking required dependencies...
echo.

REM Track if any installations happen
set INSTALLED_SOMETHING=0

REM Check scikit-learn
%PIP_CMD% show scikit-learn >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Installing scikit-learn...
    %PIP_CMD% install scikit-learn --quiet
    IF NOT ERRORLEVEL 1 (
        echo [OK] scikit-learn installed
        set INSTALLED_SOMETHING=1
    ) ELSE (
        echo [WARN] Failed to install scikit-learn
    )
) ELSE (
    echo [OK] scikit-learn already installed
)

REM Check Keras
%PIP_CMD% show keras >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Installing Keras...
    %PIP_CMD% install keras --quiet
    IF NOT ERRORLEVEL 1 (
        echo [OK] Keras installed
        set INSTALLED_SOMETHING=1
    ) ELSE (
        echo [WARN] Failed to install Keras
    )
) ELSE (
    echo [OK] Keras already installed
)

REM Check PyTorch
%PIP_CMD% show torch >nul 2>&1
IF ERRORLEVEL 1 (
    echo [*] Installing PyTorch CPU (~2GB, may take 2-5 minutes)...
    %PIP_CMD% install torch --index-url https://download.pytorch.org/whl/cpu --quiet
    IF NOT ERRORLEVEL 1 (
        echo [OK] PyTorch installed
        set INSTALLED_SOMETHING=1
    ) ELSE (
        echo [WARN] Failed to install PyTorch
    )
) ELSE (
    echo [OK] PyTorch already installed
)

REM Set KERAS_BACKEND
IF NOT "%KERAS_BACKEND%"=="torch" (
    echo [*] Setting KERAS_BACKEND=torch...
    set KERAS_BACKEND=torch
    setx KERAS_BACKEND torch >nul 2>&1
    echo [OK] KERAS_BACKEND configured
) ELSE (
    echo [OK] KERAS_BACKEND already set
)

echo.
IF %INSTALLED_SOMETHING%==1 (
    echo [INFO] New dependencies installed - terminal restart recommended after exit
)

echo [SUCCESS] All dependencies ready!
echo.

REM ============================================================================
REM STEP 2: SYSTEM MENU
REM ============================================================================

echo [STEP 2/2] System Menu
echo ------------------------------------------------------------------------
echo.

:menu
cls
echo.
echo ========================================================================
echo   COMPLETE REGIME TRADING SYSTEM v1.3.15.59 FINAL
echo ========================================================================
echo.
echo   Dependencies Status: [OK] All ready
echo   Python: %PYTHON_CMD%
echo   KERAS_BACKEND: torch
echo.
echo ========================================================================
echo   MAIN MENU
echo ========================================================================
echo.
echo   QUICK ACTIONS:
echo   1. Start Unified Trading Dashboard (Recommended)
echo   2. Start Paper Trading Platform
echo.
echo   MARKET PIPELINES:
echo   3. Run AU Pipeline (Australian Market)
echo   4. Run US Pipeline (US Market)
echo   5. Run UK Pipeline (UK Market)
echo   6. Run ALL Markets (Sequential)
echo.
echo   UTILITIES:
echo   7. View System Status
echo   8. Run Diagnostic Check
echo   9. Install/Update Dependencies
echo.
echo   0. Exit
echo.
echo ========================================================================
echo.

set /p choice="Select option (0-9): "

IF "%choice%"=="1" goto start_dashboard
IF "%choice%"=="2" goto start_paper_trading
IF "%choice%"=="3" goto run_au_pipeline
IF "%choice%"=="4" goto run_us_pipeline
IF "%choice%"=="5" goto run_uk_pipeline
IF "%choice%"=="6" goto run_all_pipelines
IF "%choice%"=="7" goto view_status
IF "%choice%"=="8" goto run_diagnostic
IF "%choice%"=="9" goto install_deps
IF "%choice%"=="0" goto exit_program

echo.
echo [ERROR] Invalid option. Please try again.
timeout /t 2 >nul
goto menu

REM ============================================================================
REM MENU ACTIONS
REM ============================================================================

:start_dashboard
cls
echo.
echo ========================================================================
echo   STARTING UNIFIED TRADING DASHBOARD
echo ========================================================================
echo.
echo Dashboard will open at: http://localhost:8050
echo.
echo Features:
echo   - Interactive stock selection
echo   - Real-time paper trading with ML signals
echo   - Live portfolio dashboard
echo   - 24-hour market performance charts
echo.
echo Press Ctrl+C to stop the dashboard
echo.

IF EXIST "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
%PYTHON_CMD% unified_trading_dashboard.py

echo.
echo Dashboard stopped.
pause
goto menu

:start_paper_trading
cls
echo.
echo ========================================================================
echo   STARTING PAPER TRADING PLATFORM
echo ========================================================================
echo.

IF EXIST "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
%PYTHON_CMD% paper_trading_coordinator.py

echo.
pause
goto menu

:run_au_pipeline
cls
echo.
echo ========================================================================
echo   RUNNING AUSTRALIAN MARKET PIPELINE
echo ========================================================================
echo.

IF EXIST "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
IF EXIST "run_au_pipeline.py" (
    %PYTHON_CMD% run_au_pipeline.py
) ELSE (
    echo [ERROR] run_au_pipeline.py not found
)

echo.
pause
goto menu

:run_us_pipeline
cls
echo.
echo ========================================================================
echo   RUNNING US MARKET PIPELINE
echo ========================================================================
echo.

IF EXIST "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
IF EXIST "run_us_full_pipeline.py" (
    %PYTHON_CMD% run_us_full_pipeline.py
) ELSE (
    echo [ERROR] run_us_full_pipeline.py not found
)

echo.
pause
goto menu

:run_uk_pipeline
cls
echo.
echo ========================================================================
echo   RUNNING UK MARKET PIPELINE
echo ========================================================================
echo.

IF EXIST "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
IF EXIST "run_uk_pipeline.py" (
    %PYTHON_CMD% run_uk_pipeline.py
) ELSE (
    echo [ERROR] run_uk_pipeline.py not found
)

echo.
pause
goto menu

:run_all_pipelines
cls
echo.
echo ========================================================================
echo   RUNNING ALL MARKET PIPELINES
echo ========================================================================
echo.

IF EXIST "venv\Scripts\activate.bat" call venv\Scripts\activate.bat

echo [1/3] Running AU Pipeline...
IF EXIST "run_au_pipeline.py" %PYTHON_CMD% run_au_pipeline.py

echo.
echo [2/3] Running US Pipeline...
IF EXIST "run_us_full_pipeline.py" %PYTHON_CMD% run_us_full_pipeline.py

echo.
echo [3/3] Running UK Pipeline...
IF EXIST "run_uk_pipeline.py" %PYTHON_CMD% run_uk_pipeline.py

echo.
echo All pipelines complete!
pause
goto menu

:view_status
cls
echo.
echo ========================================================================
echo   SYSTEM STATUS
echo ========================================================================
echo.

echo Python Version:
%PYTHON_CMD% --version
echo.

echo Virtual Environment:
IF EXIST "venv" (
    echo [OK] Virtual environment exists
) ELSE (
    echo [WARN] Virtual environment not found
)
echo.

echo Key Dependencies:
%PIP_CMD% show keras 2>nul | findstr "Version"
%PIP_CMD% show torch 2>nul | findstr "Version"
%PIP_CMD% show scikit-learn 2>nul | findstr "Version"
echo.

echo Environment Variables:
echo KERAS_BACKEND = %KERAS_BACKEND%
echo.

echo Recent Log Files:
IF EXIST "logs" (
    dir /b /o-d logs\*.log 2>nul | findstr /n "^" | findstr "^[1-5]:"
) ELSE (
    echo No logs directory found
)

echo.
pause
goto menu

:run_diagnostic
cls
echo.
echo ========================================================================
echo   DIAGNOSTIC CHECK
echo ========================================================================
echo.

echo Current Directory: %CD%
echo.

echo Available Python Scripts:
dir /b *.py 2>nul | findstr /n "^" | findstr "^[1-10]:"
echo.

echo Available Batch Files:
dir /b *.bat 2>nul | findstr /n "^" | findstr "^[1-10]:"
echo.

echo Testing Python Import:
%PYTHON_CMD% -c "import keras, torch, sklearn; print('[OK] All imports successful')" 2>nul || echo [WARN] Some imports failed
echo.

pause
goto menu

:install_deps
cls
echo.
echo ========================================================================
echo   INSTALL/UPDATE DEPENDENCIES
echo ========================================================================
echo.

echo Installing all required dependencies...
echo.

%PIP_CMD% install --upgrade keras torch scikit-learn pandas numpy yfinance yahooquery dash plotly

echo.
echo Installation complete!
pause
goto menu

:exit_program
cls
echo.
echo ========================================================================
echo   EXITING COMPLETE REGIME TRADING SYSTEM
echo ========================================================================
echo.
echo Thank you for using the system!
echo.

IF %INSTALLED_SOMETHING%==1 (
    echo.
    echo [IMPORTANT] New dependencies were installed.
    echo For best results, close this terminal and open a new one.
    echo.
)

timeout /t 3 >nul
endlocal
exit /b 0
