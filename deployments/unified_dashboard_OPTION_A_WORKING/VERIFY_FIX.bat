@echo off
REM ========================================
REM Verify Option A Fix
REM ========================================

echo ========================================
echo Option A Fix Verification
echo ========================================
echo.

set "PASS=0"
set "FAIL=0"

REM Test 1: Check Keras config
echo [1/5] Checking Keras configuration...
if exist "%USERPROFILE%\.keras\keras.json" (
    echo ✓ PASS: keras.json exists
    set /a PASS+=1
    echo.
    echo Contents:
    type "%USERPROFILE%\.keras\keras.json"
    echo.
    findstr /C:"tensorflow" "%USERPROFILE%\.keras\keras.json" >nul
    if errorlevel 1 (
        echo ✗ WARNING: Backend not set to tensorflow
        set /a FAIL+=1
    ) else (
        echo ✓ Backend correctly set to tensorflow
        set /a PASS+=1
    )
) else (
    echo ✗ FAIL: keras.json not found
    echo Expected: %USERPROFILE%\.keras\keras.json
    set /a FAIL+=1
)
echo.

REM Test 2: Check if backup exists
echo [2/5] Checking backup file...
set "BACKUP_FILE=..\unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\ml_pipeline\swing_signal_generator.py.backup_option_a"
if exist "%BACKUP_FILE%" (
    echo ✓ PASS: Backup file exists
    set /a PASS+=1
) else (
    echo ✗ FAIL: Backup file not found
    echo This means FIX_KERAS_IMPORT.bat hasn't been run yet
    set /a FAIL+=1
)
echo.

REM Test 3: Check if import was fixed
echo [3/5] Checking import fix in swing_signal_generator.py...
set "TARGET_FILE=..\unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\ml_pipeline\swing_signal_generator.py"
if exist "%TARGET_FILE%" (
    findstr /C:"from tensorflow import keras" "%TARGET_FILE%" >nul
    if errorlevel 1 (
        echo ✗ FAIL: Import not fixed
        echo.
        echo Current import:
        findstr /N "import keras" "%TARGET_FILE%" | findstr /V "^#"
        set /a FAIL+=1
    ) else (
        echo ✓ PASS: Import fixed correctly
        echo.
        echo Current import:
        findstr /N "from tensorflow import keras" "%TARGET_FILE%"
        set /a PASS+=1
    )
) else (
    echo ✗ FAIL: swing_signal_generator.py not found
    echo Expected: %TARGET_FILE%
    set /a FAIL+=1
)
echo.

REM Test 4: Check Python packages
echo [4/5] Checking Python packages...
python -c "import tensorflow; print('✓ TensorFlow:', tensorflow.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ FAIL: TensorFlow not installed
    set /a FAIL+=1
) else (
    set /a PASS+=1
)

python -c "import torch; print('✓ PyTorch:', torch.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ WARNING: PyTorch not installed (optional for Option A)
) else (
    set /a PASS+=1
)

python -c "from tensorflow import keras; print('✓ Keras via TensorFlow:', keras.__version__)" 2>nul
if errorlevel 1 (
    echo ✗ FAIL: Keras (TensorFlow) not accessible
    set /a FAIL+=1
) else (
    set /a PASS+=1
)
echo.

REM Test 5: Check dashboard file
echo [5/5] Checking dashboard file...
set "DASHBOARD_FILE=..\unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\core\unified_trading_dashboard.py"
if exist "%DASHBOARD_FILE%" (
    echo ✓ PASS: Dashboard file exists
    set /a PASS+=1
) else (
    echo ✗ FAIL: Dashboard file not found
    echo Expected: %DASHBOARD_FILE%
    set /a FAIL+=1
)
echo.

REM Summary
echo ========================================
echo VERIFICATION SUMMARY
echo ========================================
echo.
echo Tests Passed: %PASS%
echo Tests Failed: %FAIL%
echo.

if %FAIL% EQU 0 (
    echo ✓ ALL TESTS PASSED!
    echo.
    echo Your system is ready to run the dashboard.
    echo.
    echo Next step:
    echo   START_DASHBOARD.bat
    echo.
) else (
    echo ✗ SOME TESTS FAILED
    echo.
    echo Please run: FIX_KERAS_IMPORT.bat
    echo.
    if %FAIL% GTR 3 (
        echo Critical errors detected. Please check:
        echo 1. Dashboard installation path
        echo 2. Python packages installed
        echo 3. File permissions
    )
    echo.
)

pause
