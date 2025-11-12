@echo off
REM ============================================================================
REM LSTM Model Status Checker - FIXED VERSION
REM 
REM Displays statistics about LSTM model training status.
REM Shows fresh models, stale models, and training recommendations.
REM 
REM FIXED: Slower output, better error handling, pauses for errors
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo LSTM MODEL STATUS CHECKER
echo ============================================================================
echo.

REM Change to script directory
cd /d "%~dp0"
echo Current Directory: %CD%
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Failed to activate virtual environment
        timeout /t 3 /nobreak >nul
    )
) else (
    echo [INFO] No virtual environment found - using system Python
)

echo.
echo [INFO] Checking Python installation...
python --version
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Verifying required files...
timeout /t 1 /nobreak >nul

REM Check if config file exists
if not exist "models\config\asx_sectors.json" (
    echo.
    echo [ERROR] Configuration file not found!
    echo Expected: %CD%\models\config\asx_sectors.json
    echo.
    echo This file should contain the list of ASX stocks for screening.
    echo.
    echo SOLUTION: Copy from finbert_v4.4.4\models\config\asx_sectors.json
    echo Command: copy finbert_v4.4.4\models\config\asx_sectors.json models\config\
    echo.
    
    REM Try to auto-fix
    if exist "finbert_v4.4.4\models\config\asx_sectors.json" (
        echo [FIX] Found source file, copying automatically...
        if not exist "models\config" mkdir "models\config"
        copy "finbert_v4.4.4\models\config\asx_sectors.json" "models\config\asx_sectors.json" >nul 2>&1
        if errorlevel 0 (
            echo [SUCCESS] Configuration file copied successfully!
            echo.
            timeout /t 2 /nobreak >nul
        ) else (
            echo [ERROR] Failed to copy configuration file
            echo Please copy manually.
            echo.
            pause
            exit /b 1
        )
    ) else (
        echo [ERROR] Source configuration file not found either!
        echo Expected: %CD%\finbert_v4.4.4\models\config\asx_sectors.json
        echo.
        echo Please extract the complete deployment package.
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Configuration file exists
timeout /t 1 /nobreak >nul

REM Check if screening config exists
if not exist "models\config\screening_config.json" (
    echo [WARNING] Screening configuration not found
    echo Expected: models\config\screening_config.json
    timeout /t 2 /nobreak >nul
) else (
    echo [OK] Screening configuration exists
    timeout /t 1 /nobreak >nul
)

echo.
echo ============================================================================
echo STEP 1: MODEL STATISTICS
echo ============================================================================
echo.
timeout /t 1 /nobreak >nul

REM Show model statistics
python -u models/screening/lstm_trainer.py --mode stats
set STATS_EXIT=%ERRORLEVEL%

if !STATS_EXIT! neq 0 (
    echo.
    echo [ERROR] Failed to get model statistics (Exit code: !STATS_EXIT!)
    echo.
    echo Possible issues:
    echo - Missing Python dependencies ^(run INSTALL_DEPENDENCIES.bat^)
    echo - Missing configuration files
    echo - Permission issues
    echo.
    timeout /t 5 /nobreak >nul
    pause
    exit /b !STATS_EXIT!
)

echo.
timeout /t 2 /nobreak >nul

echo.
echo ============================================================================
echo STEP 2: CHECKING FOR STALE MODELS
echo ============================================================================
echo.
echo [INFO] This checks which LSTM models are more than 7 days old...
echo.
timeout /t 2 /nobreak >nul

REM Check for stale models
python -u models/screening/lstm_trainer.py --mode check
set CHECK_EXIT=%ERRORLEVEL%

if !CHECK_EXIT! neq 0 (
    echo.
    echo [ERROR] Failed to check stale models (Exit code: !CHECK_EXIT!)
    echo.
    timeout /t 5 /nobreak >nul
) else (
    echo.
    echo [SUCCESS] Stale model check completed
    timeout /t 2 /nobreak >nul
)

echo.
echo ============================================================================
echo NEXT STEPS
echo ============================================================================
echo.
echo To train stale models, run: RUN_LSTM_TRAINING.bat
echo To train specific stocks: RUN_LSTM_TRAINING.bat --symbols CBA.AX BHP.AX
echo.
echo Note: LSTM training can take 5-15 minutes per stock
echo       Ensure you have TensorFlow installed (INSTALL_DEPENDENCIES.bat)
echo.
echo ============================================================================
echo.

pause
