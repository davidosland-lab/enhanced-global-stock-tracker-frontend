@echo off
REM ========================================================================
REM Macro News Monitor - Pipeline Integration
REM ========================================================================

echo.
echo ========================================================================
echo MACRO NEWS MONITOR - PIPELINE INTEGRATION
echo ========================================================================
echo.
echo This will integrate macro news monitoring into your pipeline files.
echo.
echo What it does:
echo   - Adds MacroNewsMonitor import to pipelines
echo   - Adds initialization code
echo   - Adds sentiment adjustment code
echo   - Creates automatic backups
echo.
pause

cd ..

python MACRO_NEWS_STANDALONE_PATCH\integrate_pipelines.py

if errorlevel 1 (
    echo.
    echo Integration failed! Check error messages above.
    pause
    exit /b 1
)

echo.
pause
