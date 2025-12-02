@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: Keras 3 Model Save Fix - Patch Installer
:: ============================================================================

color 0B
cls

echo.
echo ================================================================================
echo           KERAS 3 MODEL SAVE FIX - PATCH INSTALLER
echo ================================================================================
echo.
echo This fixes models saving to same file causing overwrites.
echo.
pause

:: Determine if we're running from inside KERAS3_MODEL_SAVE_PATCH or from parent
set "CURRENT_DIR=%cd%"
echo Current directory: %CURRENT_DIR%
echo.

:: Check if we're inside KERAS3_MODEL_SAVE_PATCH folder
echo %CURRENT_DIR% | findstr /C:"KERAS3_MODEL_SAVE_PATCH" >nul
if %errorlevel% equ 0 (
    echo [INFO] Running from inside KERAS3_MODEL_SAVE_PATCH folder
    echo [INFO] Moving to parent directory...
    cd ..
    set "PATCH_DIR=KERAS3_MODEL_SAVE_PATCH"
) else (
    echo [INFO] Running from main directory
    set "PATCH_DIR=KERAS3_MODEL_SAVE_PATCH"
)

echo Working directory: %cd%
echo Patch directory: %PATCH_DIR%
echo.

:: Check if finbert_v4.4.4 directory exists
if not exist "finbert_v4.4.4\models" (
    echo.
    echo [ERROR] finbert_v4.4.4\models directory not found!
    echo.
    echo You must be in: C:\Users\david\AATelS
    echo Current location: %cd%
    echo.
    echo CORRECT SETUP:
    echo   C:\Users\david\AATelS\
    echo   ├─ finbert_v4.4.4\models\  ← Must exist
    echo   └─ KERAS3_MODEL_SAVE_PATCH\  ← Patch folder
    echo.
    pause
    exit /b 1
)

echo [OK] finbert_v4.4.4\models directory found
echo.

:: Check if patch files exist
if not exist "%PATCH_DIR%\finbert_v4.4.4\models\lstm_predictor.py" (
    echo.
    echo [ERROR] Patch files not found!
    echo.
    echo Expected: %PATCH_DIR%\finbert_v4.4.4\models\lstm_predictor.py
    echo.
    echo Make sure you extracted the ZIP file completely.
    echo.
    pause
    exit /b 1
)

echo [OK] Patch files found
echo.

:: Create backup
echo ================================================================================
echo Step 1: Creating backup...
echo ================================================================================
echo.

set "BACKUP_DIR=finbert_v4.4.4\models\BACKUP_%date:~-4,4%%date:~-7,2%%date:~-10,2%"
set "BACKUP_DIR=%BACKUP_DIR: =0%"

echo Backup location: %BACKUP_DIR%
mkdir "%BACKUP_DIR%" 2>nul

if exist "finbert_v4.4.4\models\lstm_predictor.py" (
    copy "finbert_v4.4.4\models\lstm_predictor.py" "%BACKUP_DIR%\lstm_predictor.py.backup" >nul
    echo [OK] Backed up lstm_predictor.py
)

if exist "finbert_v4.4.4\models\train_lstm.py" (
    copy "finbert_v4.4.4\models\train_lstm.py" "%BACKUP_DIR%\train_lstm.py.backup" >nul
    echo [OK] Backed up train_lstm.py
)

echo.
echo Backup complete!
echo.

:: Install fixed files
echo ================================================================================
echo Step 2: Installing fixed files...
echo ================================================================================
echo.

copy /Y "%PATCH_DIR%\finbert_v4.4.4\models\lstm_predictor.py" "finbert_v4.4.4\models\lstm_predictor.py" >nul
if %errorlevel% equ 0 (
    echo [OK] Installed lstm_predictor.py
) else (
    echo [ERROR] Failed to install lstm_predictor.py
)

copy /Y "%PATCH_DIR%\finbert_v4.4.4\models\train_lstm.py" "finbert_v4.4.4\models\train_lstm.py" >nul
if %errorlevel% equ 0 (
    echo [OK] Installed train_lstm.py
) else (
    echo [ERROR] Failed to install train_lstm.py
)

echo.
echo Files installed!
echo.

:: Clear Python cache
echo ================================================================================
echo Step 3: Clearing Python cache...
echo ================================================================================
echo.

del /s /q finbert_v4.4.4\__pycache__ >nul 2>&1
echo [OK] Python cache cleared
echo.

:: Verify installation
echo ================================================================================
echo Step 4: Verifying installation...
echo ================================================================================
echo.

if exist "%PATCH_DIR%\verification\verify_fix.py" (
    python "%PATCH_DIR%\verification\verify_fix.py"
) else (
    echo [WARNING] Verification script not found, checking manually...
    echo.
    
    set "VERIFY_PASSED=1"
    
    findstr /C:"symbol: str = None" "finbert_v4.4.4\models\lstm_predictor.py" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] lstm_predictor.py has symbol parameter
    ) else (
        echo [FAIL] lstm_predictor.py missing symbol parameter
        set "VERIFY_PASSED=0"
    )
    
    findstr /C:"symbol}_lstm_model.keras" "finbert_v4.4.4\models\lstm_predictor.py" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] lstm_predictor.py uses symbol-specific paths
    ) else (
        echo [FAIL] lstm_predictor.py not using symbol-specific paths
        set "VERIFY_PASSED=0"
    )
    
    findstr /C:"symbol=symbol" "finbert_v4.4.4\models\train_lstm.py" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] train_lstm.py passes symbol parameter
    ) else (
        echo [FAIL] train_lstm.py doesn't pass symbol parameter
        set "VERIFY_PASSED=0"
    )
    
    echo.
    
    if "!VERIFY_PASSED!"=="1" (
        echo [SUCCESS] All checks passed!
    ) else (
        echo [WARNING] Some checks failed
    )
)

echo.

:: Final message
echo ================================================================================
echo Installation complete!
echo ================================================================================
echo.
echo WHAT CHANGED:
echo   - Models now save as: models/{symbol}_lstm_model.keras
echo   - Example: models/BHP.AX_lstm_model.keras
echo   - 139 separate files instead of 1 overwritten file
echo.
echo NEXT STEPS:
echo   1. Test with one stock:
echo      python finbert_v4.4.4\models\train_lstm.py --symbol BHP.AX --epochs 5
echo.
echo   2. Expected output:
echo      "Model saved to models/BHP.AX_lstm_model.keras"
echo.
echo   3. Verify file exists:
echo      dir models\BHP.AX_lstm_model.keras
echo.
echo   4. Run full pipeline:
echo      RUN_PIPELINE.bat
echo.
echo BACKUP LOCATION:
echo   %BACKUP_DIR%
echo.
echo ================================================================================
pause
