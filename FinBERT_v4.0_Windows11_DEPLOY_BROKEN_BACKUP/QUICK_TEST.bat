@echo off
REM ============================================================================
REM FinBERT v4.0 - Quick Test Script
REM Tests installation and basic functionality
REM ============================================================================

echo.
echo ========================================================================
echo   FinBERT v4.0 - Quick Test Script
echo ========================================================================
echo.

cd /d "%~dp0"

echo [1/5] Testing Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ FAIL: Python not found
    echo Please install Python 3.8+ and add to PATH
    goto :end
) else (
    python --version
    echo ✅ PASS: Python installed
)
echo.

echo [2/5] Testing Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ FAIL: Python 3.8+ required
    python --version
    goto :end
) else (
    echo ✅ PASS: Python version OK
)
echo.

echo [3/5] Testing core dependencies...
python -c "import flask, pandas, numpy" >nul 2>&1
if errorlevel 1 (
    echo ❌ FAIL: Dependencies not installed
    echo Please run INSTALL.bat first
    goto :end
) else (
    echo ✅ PASS: Core dependencies installed
)
echo.

echo [4/5] Testing parameter optimizer module...
python -c "from models.backtesting.parameter_optimizer import ParameterOptimizer" >nul 2>&1
if errorlevel 1 (
    echo ❌ FAIL: Parameter optimizer not found
    echo Please check models/backtesting/parameter_optimizer.py exists
    goto :end
) else (
    echo ✅ PASS: Parameter optimizer module found
)
echo.

echo [5/5] Testing application startup (dry run)...
python -c "import app_finbert_v4_dev; print('App module loaded successfully')" >nul 2>&1
if errorlevel 1 (
    echo ❌ FAIL: Application module failed to load
    echo Check error messages above
    goto :end
) else (
    echo ✅ PASS: Application module loads correctly
)
echo.

echo ========================================================================
echo   All Tests Passed! ✅
echo ========================================================================
echo.
echo Your installation is ready to use.
echo.
echo Next steps:
echo   1. Run START_FINBERT_V4.bat to start the server
echo   2. Open http://localhost:5001 in your browser
echo   3. Click "Optimize Parameters" to test the new feature
echo.
goto :success

:end
echo.
echo ========================================================================
echo   Tests Failed ❌
echo ========================================================================
echo.
echo Please fix the issues above and try again.
echo Run INSTALL.bat if dependencies are missing.
echo.
pause
exit /b 1

:success
echo ========================================================================
pause
exit /b 0
