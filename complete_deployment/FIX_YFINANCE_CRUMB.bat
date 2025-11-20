@echo off
echo ================================================================================
echo   yfinance Crumb/Cookie Fix
echo ================================================================================
echo.
echo This will:
echo   1. Clear yfinance cache
echo   2. Force re-authentication with Yahoo Finance
echo   3. Test connection
echo.
pause

cd /d "%~dp0"

echo.
echo Step 1: Clearing yfinance cache...
echo.

REM Clear Windows cache locations
if exist "%USERPROFILE%\AppData\Local\py-yfinance" (
    rmdir /s /q "%USERPROFILE%\AppData\Local\py-yfinance"
    echo   v Cleared: %%USERPROFILE%%\AppData\Local\py-yfinance
)

if exist "%USERPROFILE%\.cache\py-yfinance" (
    rmdir /s /q "%USERPROFILE%\.cache\py-yfinance"
    echo   v Cleared: %%USERPROFILE%%\.cache\py-yfinance
)

if exist ".yfinance_cache" (
    rmdir /s /q ".yfinance_cache"
    echo   v Cleared: .yfinance_cache
)

echo.
echo Step 2: Testing fresh connection...
echo.

python FIX_YFINANCE_CRUMB_ISSUE.py

if %errorlevel% equ 0 (
    echo.
    echo ================================================================================
    echo   SUCCESS - yfinance is working
    echo ================================================================================
    echo.
    echo You can now run the stock screener:
    echo   RUN_STOCK_SCREENER.bat
    echo.
) else (
    echo.
    echo ================================================================================
    echo   STILL HAVING ISSUES
    echo ================================================================================
    echo.
    echo See: YFINANCE_CRUMB_ISSUE_EXPLAINED.md for additional solutions
    echo.
    echo Quick fix: Downgrade yfinance
    echo   pip uninstall yfinance -y
    echo   pip install yfinance==0.1.96
    echo.
)

pause
