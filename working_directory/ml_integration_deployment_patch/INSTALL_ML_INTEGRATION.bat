@echo off
REM ============================================================================
REM ML Pipeline Integration - Installation Script for Windows 11
REM ============================================================================
REM This script installs the ML pipeline integration on your Windows 11 machine
REM 
REM Target: C:\Users\david\AATelS\finbert_v4.4.4\
REM 
REM What this script does:
REM 1. Checks if target directory exists
REM 2. Creates backup of existing files
REM 3. Copies ML pipeline package
REM 4. Copies enhanced trading platform files
REM 5. Verifies installation
REM 
REM Author: Enhanced Global Stock Tracker
REM Version: 2.0 - ML Enhanced
REM Date: 2024-12-24
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo ML PIPELINE INTEGRATION - WINDOWS 11 INSTALLATION
echo ============================================================================
echo.
echo Version: 2.0 - ML Enhanced
echo Date: 2024-12-24
echo.
echo This will install the ML pipeline integration on your Windows 11 machine.
echo.
echo Target Directory: C:\Users\david\AATelS\finbert_v4.4.4\
echo.
echo What will be installed:
echo   - ML Pipeline Package (ml_pipeline/)
echo   - Enhanced Manual Trading Platform (manual_trading_phase3.py)
echo   - Enhanced Signal Generator (phase3_signal_generator.py)
echo   - Documentation
echo.
pause

REM ============================================================================
REM STEP 1: Verify Target Directory
REM ============================================================================

set "TARGET_DIR=C:\Users\david\AATelS\finbert_v4.4.4"

echo.
echo [STEP 1] Verifying target directory...
if not exist "%TARGET_DIR%" (
    echo [ERROR] Target directory not found: %TARGET_DIR%
    echo.
    echo Please ensure you are running this from the correct location.
    echo Expected directory: C:\Users\david\AATelS\finbert_v4.4.4\
    echo.
    pause
    exit /b 1
)
echo [SUCCESS] Target directory found: %TARGET_DIR%

REM Check if working_directory exists
if not exist "%TARGET_DIR%\working_directory" (
    echo [ERROR] working_directory not found in: %TARGET_DIR%
    echo.
    echo Please ensure the finbert_v4.4.4 directory structure is correct.
    echo.
    pause
    exit /b 1
)
echo [SUCCESS] working_directory found

REM ============================================================================
REM STEP 2: Backup Existing Files
REM ============================================================================

echo.
echo [STEP 2] Backing up existing files...
call backup_scripts\BACKUP_EXISTING_FILES.bat
if errorlevel 1 (
    echo [WARNING] Backup may have failed, but continuing...
)

REM ============================================================================
REM STEP 3: Install ML Pipeline Package
REM ============================================================================

echo.
echo [STEP 3] Installing ML Pipeline package...

REM Create ml_pipeline directory
if not exist "%TARGET_DIR%\working_directory\ml_pipeline" (
    echo [CREATE] Creating ml_pipeline directory...
    mkdir "%TARGET_DIR%\working_directory\ml_pipeline"
) else (
    echo [EXISTS] ml_pipeline directory already exists
)

REM Copy ML pipeline files
echo [COPY] Copying ML pipeline files...
xcopy "ml_pipeline\*.*" "%TARGET_DIR%\working_directory\ml_pipeline\" /Y /I >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to copy ML pipeline files
    pause
    exit /b 1
)

echo [SUCCESS] ML pipeline installed:
echo   - adaptive_ml_integration.py (19 KB)
echo   - prediction_engine.py (31 KB)
echo   - deep_learning_ensemble.py (17 KB)
echo   - neural_network_models.py (18 KB)
echo   - cba_enhanced_prediction_system.py (150 KB)

REM ============================================================================
REM STEP 4: Install Enhanced Platform Files
REM ============================================================================

echo.
echo [STEP 4] Installing enhanced platform files...

REM Copy enhanced files
echo [COPY] manual_trading_phase3.py (46 KB)
copy "working_directory\manual_trading_phase3.py" "%TARGET_DIR%\working_directory\" /Y >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to copy manual_trading_phase3.py
    pause
    exit /b 1
)

echo [COPY] phase3_signal_generator.py (18 KB)
copy "working_directory\phase3_signal_generator.py" "%TARGET_DIR%\working_directory\" /Y >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to copy phase3_signal_generator.py
    pause
    exit /b 1
)

echo [SUCCESS] Enhanced platform files installed

REM ============================================================================
REM STEP 5: Install Documentation
REM ============================================================================

echo.
echo [STEP 5] Installing documentation...

REM Create documentation directory if needed
if not exist "%TARGET_DIR%\working_directory\documentation" (
    mkdir "%TARGET_DIR%\working_directory\documentation"
)

REM Copy documentation
xcopy "documentation\*.md" "%TARGET_DIR%\working_directory\documentation\" /Y /I >nul 2>&1

echo [SUCCESS] Documentation installed

REM ============================================================================
REM STEP 6: Verify Installation
REM ============================================================================

echo.
echo [STEP 6] Verifying installation...

set "INSTALL_OK=1"

REM Check ML pipeline files
if not exist "%TARGET_DIR%\working_directory\ml_pipeline\adaptive_ml_integration.py" (
    echo [ERROR] adaptive_ml_integration.py not found
    set "INSTALL_OK=0"
) else (
    echo [OK] adaptive_ml_integration.py
)

if not exist "%TARGET_DIR%\working_directory\ml_pipeline\prediction_engine.py" (
    echo [ERROR] prediction_engine.py not found
    set "INSTALL_OK=0"
) else (
    echo [OK] prediction_engine.py
)

REM Check enhanced platform files
if not exist "%TARGET_DIR%\working_directory\manual_trading_phase3.py" (
    echo [ERROR] manual_trading_phase3.py not found
    set "INSTALL_OK=0"
) else (
    echo [OK] manual_trading_phase3.py
)

if not exist "%TARGET_DIR%\working_directory\phase3_signal_generator.py" (
    echo [ERROR] phase3_signal_generator.py not found
    set "INSTALL_OK=0"
) else (
    echo [OK] phase3_signal_generator.py
)

REM ============================================================================
REM STEP 7: Installation Complete
REM ============================================================================

echo.
echo ============================================================================
if "%INSTALL_OK%"=="1" (
    echo INSTALLATION COMPLETE - SUCCESS!
) else (
    echo INSTALLATION COMPLETE - WITH WARNINGS
)
echo ============================================================================
echo.

if "%INSTALL_OK%"=="1" (
    echo All files successfully installed to:
    echo %TARGET_DIR%\working_directory\
    echo.
    echo NEW FEATURES INSTALLED:
    echo   [+] ML Pipeline Package (ml_pipeline/)
    echo   [+] Enhanced Manual Trading Platform
    echo   [+] ML-Enhanced Signal Generation
    echo   [+] New Command: recommend_buy_ml()
    echo.
    echo ML MODELS INTEGRATED:
    echo   - LSTM Neural Networks
    echo   - Transformer Models
    echo   - Ensemble Models (XGBoost, LightGBM, CatBoost, RF, GBR)
    echo   - Graph Neural Networks (GNN)
    echo   - Reinforcement Learning (RL)
    echo   - Sentiment Analysis
    echo.
    echo NEXT STEPS:
    echo   1. Open Command Prompt
    echo   2. Navigate to: cd %TARGET_DIR%\working_directory
    echo   3. Run: python manual_trading_phase3.py --port 5004
    echo   4. In console, try: recommend_buy_ml()
    echo.
    echo DOCUMENTATION:
    echo   %TARGET_DIR%\working_directory\documentation\
    echo   - ML_INTEGRATION_FINAL_DELIVERY.md (Quick Start)
    echo   - ML_PIPELINE_INTEGRATION_COMPLETE.md (Complete Guide)
    echo.
) else (
    echo [WARNING] Some files may not have been installed correctly.
    echo Please check the errors above.
    echo.
    echo You can try running the installation script again, or
    echo manually copy files from the deployment package.
    echo.
)

echo ============================================================================
echo.
echo Press any key to exit...
pause >nul

exit /b 0
