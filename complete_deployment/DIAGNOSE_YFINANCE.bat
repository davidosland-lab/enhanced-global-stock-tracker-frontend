@echo off
REM ===============================================================================
REM   FinBERT v4.4.4 - yfinance Diagnostic Tool
REM   Comprehensive diagnostic to identify yfinance connectivity issues
REM ===============================================================================

echo ================================================================================
echo   FinBERT v4.4.4 - YFINANCE DIAGNOSTIC TOOL
echo ================================================================================
echo.
echo This diagnostic will test:
echo   1. Python library imports (yfinance, curl_cffi, requests)
echo   2. Network connectivity to Yahoo Finance
echo   3. DNS resolution
echo   4. curl_cffi browser impersonation
echo   5. Direct Yahoo Finance API calls
echo   6. yfinance Ticker object creation
echo   7. yfinance fast_info method
echo   8. yfinance history method
echo   9. yfinance info method
echo   10. Environment variables (proxy, SSL)
echo.
echo Duration: ~30-60 seconds
echo.

REM Set the working directory to script location
cd /d "%~dp0"

echo ================================================================================
echo   System Information
echo ================================================================================
echo.
echo Current Directory: %CD%
echo Python Version:
python --version 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo   ERROR: Python is not installed!
    echo ================================================================================
    echo.
    echo Python is required to run this diagnostic.
    echo.
    echo Please install Python 3.8+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
echo.

echo ================================================================================
echo   Running Diagnostic
echo ================================================================================
echo.

REM Run the diagnostic script
python diagnose_yfinance.py

if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo   DIAGNOSTIC FAILED
    echo ================================================================================
    echo.
    echo The diagnostic script encountered an error.
    echo Check the error messages above for details.
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   DIAGNOSTIC COMPLETE
echo ================================================================================
echo.
echo Results have been saved to: yfinance_diagnostic_results.json
echo.
echo Please review the diagnosis and recommendations above.
echo.
echo If you need help interpreting the results:
echo   1. Share yfinance_diagnostic_results.json with support
echo   2. Look for tests marked with X (failed)
echo   3. Follow the recommended solutions
echo.

pause
