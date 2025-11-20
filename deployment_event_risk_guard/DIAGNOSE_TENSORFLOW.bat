@echo off
REM ====================================================================
REM TensorFlow Diagnostic Script
REM Determines why TensorFlow import is failing in batch context
REM ====================================================================

echo.
echo ========================================================================
echo   TENSORFLOW DIAGNOSTIC TOOL
echo ========================================================================
echo.
echo This will help diagnose why TensorFlow import is failing.
echo.
pause
echo.

REM Test 1: Check Python
echo [TEST 1] Checking Python installation...
python --version
if errorlevel 1 (
    echo [FAIL] Python not found or not in PATH
    echo.
    pause
    exit /b 1
) else (
    echo [PASS] Python is accessible
)
echo.

REM Test 2: Check Python can run simple command
echo [TEST 2] Testing Python execution...
python -c "print('Python execution works')"
if errorlevel 1 (
    echo [FAIL] Python cannot execute commands
    echo.
    pause
    exit /b 1
) else (
    echo [PASS] Python can execute commands
)
echo.

REM Test 3: Try importing TensorFlow (show output)
echo [TEST 3] Testing TensorFlow import (WITH output)...
python -c "import tensorflow"
if errorlevel 1 (
    echo [FAIL] TensorFlow import failed
    echo The error above shows why TensorFlow cannot be imported.
) else (
    echo [PASS] TensorFlow import succeeded
)
echo.

REM Test 4: Try importing TensorFlow (silent - same as batch file)
echo [TEST 4] Testing TensorFlow import (SILENT - like batch file)...
python -c "import tensorflow" 2>nul
set IMPORT_RESULT=%ERRORLEVEL%
if %IMPORT_RESULT% neq 0 (
    echo [FAIL] TensorFlow import failed (errorlevel: %IMPORT_RESULT%)
    echo.
    echo This is why the batch file thinks TensorFlow is not installed.
) else (
    echo [PASS] TensorFlow import succeeded (errorlevel: %IMPORT_RESULT%)
)
echo.

REM Test 5: Check TensorFlow version
echo [TEST 5] Checking TensorFlow version...
python -c "import tensorflow; print('TensorFlow version:', tensorflow.__version__)"
if errorlevel 1 (
    echo [FAIL] Cannot get TensorFlow version
) else (
    echo [PASS] TensorFlow version retrieved
)
echo.

REM Test 6: Check where TensorFlow is installed
echo [TEST 6] Checking TensorFlow installation location...
python -c "import tensorflow; import os; print('TensorFlow location:', os.path.dirname(tensorflow.__file__))"
echo.

REM Test 7: Check for import warnings/errors
echo [TEST 7] Checking for TensorFlow import warnings...
python -c "import sys; import tensorflow as tf; print('Import completed without errors')" 2>&1
echo.

REM Test 8: Check available Python packages
echo [TEST 8] Checking installed packages...
echo Running: pip list | findstr /I "tensorflow"
pip list | findstr /I "tensorflow"
echo.

REM Summary
echo ========================================================================
echo   DIAGNOSTIC SUMMARY
echo ========================================================================
echo.
echo Based on the tests above:
echo.
echo If TEST 3 showed an error message:
echo   - Read the error carefully (missing DLL, version conflict, etc.)
echo   - This is the actual problem preventing TensorFlow from loading
echo.
echo If TEST 3 passed but TEST 4 failed:
echo   - TensorFlow imports successfully when showing output
echo   - But fails when output is suppressed (2^>nul)
echo   - This is a batch file quirk - we need to fix the script
echo.
echo If all tests passed:
echo   - TensorFlow is working fine
echo   - The batch file check needs to be modified
echo.
echo ========================================================================
echo.
echo Press any key to close and review the results above...
pause >nul
