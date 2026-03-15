@echo off
REM Pandas 2.x Compatibility Fix
REM Fixes: TypeError: NDFrame.fillna() got an unexpected keyword argument 'method'

echo ================================================================================
echo   PANDAS 2.x COMPATIBILITY FIX
echo ================================================================================
echo.
echo This will fix the error:
echo   TypeError: NDFrame.fillna() got an unexpected keyword argument 'method'
echo.
echo Press any key to continue or CTRL+C to cancel...
pause >nul

python FIX_PANDAS_2.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   FIX FAILED
    echo ================================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo   FIX COMPLETE
echo ================================================================================
echo.
echo Next steps:
echo   1. Restart Flask server (CTRL+C in Flask terminal, then restart)
echo   2. Try training again - it should work now!
echo.
pause
