@echo off
REM FinBERT v4.0 - Configuration Check Script
REM This script verifies your Windows 11 setup

echo ============================================================================
echo   FinBERT v4.0 - Windows 11 Configuration Check
echo ============================================================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python --version
    echo    ^> Python: OK
) else (
    echo    ^> Python: NOT FOUND
    echo    ^> Please install Python from https://www.python.org/downloads/
    echo    ^> Make sure to check "Add Python to PATH" during installation
    goto :end
)
echo.

REM Check if we're in the correct directory
echo [2/5] Checking installation directory...
if exist app_finbert_v4_dev.py (
    echo    ^> Location: OK
) else (
    echo    ^> Location: ERROR
    echo    ^> Please run this script from the FinBERT installation directory
    goto :end
)
echo.

REM Check if virtual environment exists
echo [3/5] Checking virtual environment...
if exist venv (
    echo    ^> Virtual Environment: OK
) else if exist scripts\venv (
    echo    ^> Virtual Environment: OK (in scripts directory)
) else (
    echo    ^> Virtual Environment: NOT FOUND
    echo    ^> Please run scripts\INSTALL_WINDOWS11.bat first
    goto :end
)
echo.

REM Check configuration
echo [4/5] Checking configuration...
if exist config_dev.py (
    echo    ^> Config File: OK
    findstr /C:"HOST = '127.0.0.1'" config_dev.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo    ^> Host Setting: 127.0.0.1 (Localhost) - CORRECT for Windows 11
    ) else (
        findstr /C:"HOST = '0.0.0.0'" config_dev.py >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            echo    ^> Host Setting: 0.0.0.0 - WARNING: Should be 127.0.0.1
            echo    ^> This may cause connection issues on Windows 11
        )
    )
    
    findstr /C:"PORT = " config_dev.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        for /f "tokens=3" %%a in ('findstr /C:"PORT = " config_dev.py') do (
            echo    ^> Port Setting: %%a
        )
    )
) else (
    echo    ^> Config File: NOT FOUND
    goto :end
)
echo.

REM Check if port is available
echo [5/5] Checking port availability...
netstat -ano | findstr ":5001" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    ^> Port 5001: IN USE
    echo    ^> Another application is using port 5001
    echo    ^> Either close that application or change PORT in config_dev.py
) else (
    echo    ^> Port 5001: AVAILABLE
)
echo.

echo ============================================================================
echo   Configuration Check Complete!
echo ============================================================================
echo.
echo Next steps:
echo   1. If all checks passed: Run START_FINBERT_V4.bat
echo   2. Open browser to: http://127.0.0.1:5001
echo   3. Test with stock symbol: AAPL
echo.
echo If you see any errors above, please fix them before starting the server.
echo.

:end
pause
