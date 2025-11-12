@echo off
REM ============================================================================
REM LSTM Issue Diagnostic Script
REM 
REM This script helps diagnose why LSTM training is failing
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo LSTM ISSUE DIAGNOSTIC
echo ============================================================================
echo.
echo This script will check all requirements for LSTM training
echo.
timeout /t 2 /nobreak >nul

cd /d "%~dp0"

echo.
echo [STEP 1/7] Checking Current Directory
echo ============================================================================
echo Current Directory: %CD%
echo.
timeout /t 2 /nobreak >nul

echo.
echo [STEP 2/7] Checking Python Installation
echo ============================================================================
python --version
if errorlevel 1 (
    echo [ERROR] Python not found!
    goto :error_end
) else (
    echo [OK] Python is installed
)
echo.
timeout /t 2 /nobreak >nul

echo.
echo [STEP 3/7] Checking Required Python Packages
echo ============================================================================
echo.

echo Checking numpy...
python -c "import numpy; print('numpy version:', numpy.__version__)" 2>nul
if errorlevel 1 (
    echo [ERROR] numpy not installed
    set MISSING_DEPS=1
) else (
    echo [OK] numpy installed
)
timeout /t 1 /nobreak >nul

echo.
echo Checking pandas...
python -c "import pandas; print('pandas version:', pandas.__version__)" 2>nul
if errorlevel 1 (
    echo [ERROR] pandas not installed
    set MISSING_DEPS=1
) else (
    echo [OK] pandas installed
)
timeout /t 1 /nobreak >nul

echo.
echo Checking TensorFlow...
python -c "import tensorflow; print('TensorFlow version:', tensorflow.__version__)" 2>nul
if errorlevel 1 (
    echo [ERROR] TensorFlow not installed - REQUIRED FOR LSTM!
    set MISSING_DEPS=1
    set MISSING_TF=1
) else (
    echo [OK] TensorFlow installed
)
timeout /t 1 /nobreak >nul

echo.
echo Checking yfinance...
python -c "import yfinance; print('yfinance version:', yfinance.__version__)" 2>nul
if errorlevel 1 (
    echo [ERROR] yfinance not installed
    set MISSING_DEPS=1
) else (
    echo [OK] yfinance installed
)
timeout /t 1 /nobreak >nul

echo.
if defined MISSING_DEPS (
    echo.
    echo [WARNING] Some required packages are missing!
    echo.
    if defined MISSING_TF (
        echo TensorFlow is REQUIRED for LSTM training.
        echo.
    )
    echo To install all dependencies, run: INSTALL_DEPENDENCIES.bat
    echo.
    timeout /t 5 /nobreak >nul
) else (
    echo [OK] All required packages are installed
)

echo.
timeout /t 2 /nobreak >nul

echo.
echo [STEP 4/7] Checking Directory Structure
echo ============================================================================
echo.

if exist "models" (
    echo [OK] models\ directory exists
) else (
    echo [ERROR] models\ directory NOT FOUND
    goto :error_end
)

if exist "models\screening" (
    echo [OK] models\screening\ directory exists
) else (
    echo [ERROR] models\screening\ directory NOT FOUND
    goto :error_end
)

if exist "models\screening\lstm_trainer.py" (
    echo [OK] lstm_trainer.py exists
) else (
    echo [ERROR] lstm_trainer.py NOT FOUND
    goto :error_end
)

echo.
timeout /t 2 /nobreak >nul

echo.
echo [STEP 5/7] Checking Configuration Files
echo ============================================================================
echo.

if exist "models\config" (
    echo [OK] models\config\ directory exists
) else (
    echo [WARNING] models\config\ directory NOT FOUND
    echo [FIX] Creating directory...
    mkdir "models\config"
)

if exist "models\config\asx_sectors.json" (
    echo [OK] asx_sectors.json exists
    echo Location: %CD%\models\config\asx_sectors.json
) else (
    echo [ERROR] asx_sectors.json NOT FOUND
    echo Expected: %CD%\models\config\asx_sectors.json
    echo.
    
    if exist "finbert_v4.4.4\models\config\asx_sectors.json" (
        echo [FIX] Found source file, attempting to copy...
        copy "finbert_v4.4.4\models\config\asx_sectors.json" "models\config\asx_sectors.json" >nul 2>&1
        if errorlevel 0 (
            echo [SUCCESS] Configuration file copied!
        ) else (
            echo [ERROR] Failed to copy configuration file
            echo Please copy manually:
            echo   copy finbert_v4.4.4\models\config\asx_sectors.json models\config\
            goto :error_end
        )
    ) else (
        echo [ERROR] Source configuration file also not found
        echo Expected: %CD%\finbert_v4.4.4\models\config\asx_sectors.json
        echo.
        echo Please ensure you have the complete deployment package.
        goto :error_end
    )
)

if exist "models\config\screening_config.json" (
    echo [OK] screening_config.json exists
) else (
    echo [WARNING] screening_config.json NOT FOUND (optional)
)

echo.
timeout /t 2 /nobreak >nul

echo.
echo [STEP 6/7] Checking FinBERT Integration
echo ============================================================================
echo.

if exist "finbert_v4.4.4" (
    echo [OK] finbert_v4.4.4\ directory exists
) else (
    echo [WARNING] finbert_v4.4.4\ directory NOT FOUND
    echo LSTM training can still work without it.
)

if exist "models\screening\finbert_bridge.py" (
    echo [OK] finbert_bridge.py exists (integration active)
) else (
    echo [WARNING] finbert_bridge.py NOT FOUND (integration inactive)
)

echo.
timeout /t 2 /nobreak >nul

echo.
echo [STEP 7/7] Checking Output Directories
echo ============================================================================
echo.

if exist "logs" (
    echo [OK] logs\ directory exists
) else (
    echo [INFO] Creating logs\ directory...
    mkdir "logs"
)

if exist "logs\lstm_training" (
    echo [OK] logs\lstm_training\ directory exists
) else (
    echo [INFO] Creating logs\lstm_training\ directory...
    mkdir "logs\lstm_training"
)

if exist "models\trained" (
    echo [OK] models\trained\ directory exists
) else (
    echo [INFO] Creating models\trained\ directory...
    mkdir "models\trained"
)

echo.
timeout /t 2 /nobreak >nul

echo.
echo ============================================================================
echo DIAGNOSTIC SUMMARY
echo ============================================================================
echo.

if defined MISSING_DEPS (
    echo [ACTION REQUIRED] Install missing dependencies:
    echo   Run: INSTALL_DEPENDENCIES.bat
    echo.
)

if defined MISSING_TF (
    echo [CRITICAL] TensorFlow is required for LSTM training!
    echo   Install: pip install tensorflow>=2.13.0
    echo.
)

if not exist "models\config\asx_sectors.json" (
    echo [ACTION REQUIRED] Configuration file missing
    echo   Copy manually or run this script again
    echo.
)

if not defined MISSING_DEPS (
    if exist "models\config\asx_sectors.json" (
        echo.
        echo [SUCCESS] All diagnostics passed!
        echo.
        echo You should now be able to run:
        echo   - CHECK_MODEL_STATUS_FIXED.bat
        echo   - RUN_LSTM_TRAINING_FIXED.bat
        echo.
    )
)

echo ============================================================================
echo.

goto :end

:error_end
echo.
echo [ERROR] Critical issue found - see above for details
echo.

:end
pause
