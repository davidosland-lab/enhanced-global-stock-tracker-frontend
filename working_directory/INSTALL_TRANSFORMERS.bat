@echo off
REM ============================================================================
REM FIX FINBERT TRANSFORMERS - Quick Install
REM ============================================================================

echo.
echo ========================================================================
echo   INSTALLING TRANSFORMERS FOR FINBERT
echo ========================================================================
echo.

REM Try different possible locations for pip
echo [1/3] Checking for pip...
echo.

IF EXIST "venv\Scripts\pip.exe" (
    echo Found: venv\Scripts\pip.exe
    set PIP_CMD=venv\Scripts\pip
    goto install
)

IF EXIST ".venv\Scripts\pip.exe" (
    echo Found: .venv\Scripts\pip.exe
    set PIP_CMD=.venv\Scripts\pip
    goto install
)

IF EXIST "env\Scripts\pip.exe" (
    echo Found: env\Scripts\pip.exe
    set PIP_CMD=env\Scripts\pip
    goto install
)

REM Try system pip
where pip >nul 2>&1
IF NOT ERRORLEVEL 1 (
    echo Using system pip
    set PIP_CMD=pip
    goto install
)

echo [ERROR] Could not find pip
echo.
echo Please run this command manually:
echo   python -m pip install transformers
echo.
pause
exit /b 1

:install
echo.
echo [2/3] Installing transformers package...
echo This may take 1-2 minutes...
echo.

%PIP_CMD% install transformers

IF ERRORLEVEL 1 (
    echo.
    echo [ERROR] Installation failed
    echo.
    echo Try this command instead:
    echo   python -m pip install transformers
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying installation...
python -c "import transformers; print('[OK] transformers version:', transformers.__version__)"

IF ERRORLEVEL 1 (
    echo [WARN] Verification failed
) ELSE (
    echo.
    echo ========================================================================
    echo   SUCCESS!
    echo ========================================================================
    echo.
    echo Transformers package installed successfully.
    echo.
    echo NEXT STEP:
    echo   1. Stop the dashboard (Ctrl+C in dashboard window)
    echo   2. Restart: python unified_trading_dashboard.py
    echo   3. FinBERT will now load at 95%% accuracy!
    echo.
)

pause
