@echo off
REM ============================================================================
REM QUICK FIX: Install Missing yahooquery Dependency
REM ============================================================================

echo.
echo ============================================================================
echo  Installing Missing yahooquery Dependency
echo ============================================================================
echo.
echo  This will install yahooquery required for pipeline operations.
echo.
echo  Estimated time: ~1 minute
echo.
echo ============================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run INSTALL_COMPLETE.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install yahooquery
echo.
echo [2/2] Installing yahooquery...
echo.
python -m pip install --no-cache-dir yahooquery>=2.3.0

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to install yahooquery
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo  yahooquery Installation Complete!
echo ============================================================================
echo.
echo  You can now run pipelines:
echo    - Option 4: Run All Pipelines
echo    - Option 5: Run AU Pipeline Only
echo    - Option 6: Run US Pipeline Only  
echo    - Option 7: Run UK Pipeline Only
echo.
echo  Start the system with START.bat
echo.
echo ============================================================================
echo.
pause
