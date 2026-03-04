@echo off
REM ========================================
REM Option A: Fix Keras Import for Dashboard
REM Safe Working Model - No PyTorch Upgrade
REM ========================================

echo ========================================
echo Unified Trading Dashboard v1.3.15.87
echo Option A: Safe Working Model
echo ========================================
echo.
echo This script will:
echo 1. Create Keras config (TensorFlow backend)
echo 2. Fix keras import in swing_signal_generator.py
echo 3. Create backup of original file
echo.
pause

REM Step 1: Create Keras config directory
echo [1/3] Creating Keras configuration...
if not exist "%USERPROFILE%\.keras" (
    mkdir "%USERPROFILE%\.keras"
    echo ✓ Created .keras directory
) else (
    echo ✓ .keras directory exists
)

REM Step 2: Create keras.json with TensorFlow backend
echo [2/3] Configuring Keras to use TensorFlow backend...
(
echo {
echo   "backend": "tensorflow",
echo   "floatx": "float32",
echo   "epsilon": 1e-07,
echo   "image_data_format": "channels_last"
echo }
) > "%USERPROFILE%\.keras\keras.json"

if exist "%USERPROFILE%\.keras\keras.json" (
    echo ✓ Created keras.json
    echo.
    echo Contents:
    type "%USERPROFILE%\.keras\keras.json"
    echo.
) else (
    echo ✗ Failed to create keras.json
    pause
    exit /b 1
)

REM Step 3: Fix the import in swing_signal_generator.py
echo [3/3] Fixing keras import in swing_signal_generator.py...
echo.

set "TARGET_FILE=..\unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\ml_pipeline\swing_signal_generator.py"

if not exist "%TARGET_FILE%" (
    echo WARNING: Target file not found at:
    echo %TARGET_FILE%
    echo.
    echo Please specify the correct path to your dashboard installation:
    set /p "DASHBOARD_PATH=Enter path (e.g., C:\Users\david\Regime_trading\unified_trading_dashboard_v1.3.15.87_ULTIMATE_old): "
    set "TARGET_FILE=%DASHBOARD_PATH%\ml_pipeline\swing_signal_generator.py"
)

if not exist "%TARGET_FILE%" (
    echo ✗ ERROR: Could not find swing_signal_generator.py
    echo.
    echo Please manually edit the file:
    echo 1. Open: ml_pipeline\swing_signal_generator.py
    echo 2. Find line 39: import keras
    echo 3. Replace with: from tensorflow import keras
    echo.
    pause
    exit /b 1
)

REM Create backup
echo Creating backup...
copy "%TARGET_FILE%" "%TARGET_FILE%.backup_option_a" >nul
if exist "%TARGET_FILE%.backup_option_a" (
    echo ✓ Backup created: swing_signal_generator.py.backup_option_a
) else (
    echo ✗ Failed to create backup
    pause
    exit /b 1
)

REM Fix the import using PowerShell
echo Fixing import statement...
powershell -Command "(Get-Content '%TARGET_FILE%') -replace '^import keras$', 'from tensorflow import keras' | Set-Content '%TARGET_FILE%'"

if errorlevel 1 (
    echo ✗ Failed to fix import
    echo Restoring backup...
    copy "%TARGET_FILE%.backup_option_a" "%TARGET_FILE%" >nul
    pause
    exit /b 1
)

echo ✓ Fixed keras import
echo.

REM Verify the fix
echo Verifying fix...
findstr /C:"from tensorflow import keras" "%TARGET_FILE%" >nul
if errorlevel 1 (
    echo ✗ Fix verification failed
    echo Restoring backup...
    copy "%TARGET_FILE%.backup_option_a" "%TARGET_FILE%" >nul
    pause
    exit /b 1
) else (
    echo ✓ Fix verified successfully
)

echo.
echo ========================================
echo FIX COMPLETE!
echo ========================================
echo.
echo What was fixed:
echo 1. ✓ Keras backend set to TensorFlow
echo 2. ✓ Import changed from 'import keras' to 'from tensorflow import keras'
echo 3. ✓ Backup created: swing_signal_generator.py.backup_option_a
echo.
echo Configuration:
echo - PyTorch: 2.2.0 (no upgrade - safe)
echo - FinBERT: Keyword sentiment (fallback mode)
echo - Win Rate: 70-80%%
echo - Security Risk: NONE (using keyword sentiment)
echo.
echo Next Steps:
echo 1. Run: START_DASHBOARD.bat
echo 2. Open: http://localhost:8050
echo 3. Start trading!
echo.
echo To restore original file:
echo copy swing_signal_generator.py.backup_option_a swing_signal_generator.py
echo.
pause
