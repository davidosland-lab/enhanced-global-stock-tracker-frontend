@echo off
REM ============================================================================
REM CHECK_LOGS.bat - Quick Log Viewer
REM ============================================================================
REM
REM This script helps you quickly view the most recent overnight screening log
REM and check for key indicators of successful execution.
REM
REM Usage: Double-click CHECK_LOGS.bat
REM ============================================================================

echo.
echo ================================================================================
echo OVERNIGHT SCREENER - LOG VIEWER
echo ================================================================================
echo.

REM Navigate to logs directory
cd models\screening\logs 2>nul

if errorlevel 1 (
    echo [ERROR] Log directory not found: models\screening\logs
    echo.
    echo Make sure you are running this from the project root directory.
    echo.
    pause
    exit /b 1
)

REM Find most recent log file
for /f "delims=" %%i in ('dir /b /o-d overnight_screening_*.log 2^>nul') do (
    set LATEST_LOG=%%i
    goto :found
)

echo [ERROR] No log files found in models\screening\logs
echo.
echo The pipeline may not have run yet, or logs were deleted.
echo.
pause
exit /b 1

:found
echo [INFO] Most recent log file: %LATEST_LOG%
echo.
echo ================================================================================
echo KEY INDICATORS
echo ================================================================================
echo.

REM Search for key indicators
echo [Checking] FinBERT Components...
findstr /C:"FinBERT LSTM Available" %LATEST_LOG% 2>nul
findstr /C:"FinBERT Sentiment Available" %LATEST_LOG% 2>nul
findstr /C:"FinBERT News Available" %LATEST_LOG% 2>nul
echo.

echo [Checking] PHASE 2.5 - Market Regime Engine...
findstr /C:"PHASE 2.5" %LATEST_LOG% 2>nul
findstr /C:"Market Regime Engine:" %LATEST_LOG% 2>nul
echo.

echo [Checking] PHASE 4.5 - LSTM Training...
findstr /C:"PHASE 4.5" %LATEST_LOG% 2>nul
findstr /C:"Training completed" %LATEST_LOG% 2>nul | findstr /V /C:"ERROR" | findstr /V /C:"failed" 2>nul
echo.

echo [Checking] LSTM Training Summary...
findstr /C:"Trained:" %LATEST_LOG% 2>nul
findstr /C:"Failed:" %LATEST_LOG% 2>nul
findstr /C:"Success Rate:" %LATEST_LOG% 2>nul
echo.

echo [Checking] Sentiment Analysis (sample)...
findstr /C:"Sentiment for" %LATEST_LOG% 2>nul | findstr /V /C:"neutral (0.0%%), 0 articles" 2>nul | more +1 | head -n 5
echo.

echo [Checking] Recent Errors...
findstr /C:"ERROR" %LATEST_LOG% 2>nul | more +1 | head -n 10
echo.

echo ================================================================================
echo FULL LOG LOCATION
echo ================================================================================
echo.
echo Full log path: models\screening\logs\%LATEST_LOG%
echo.
echo To view the complete log:
echo   1. Open File Explorer
echo   2. Navigate to: models\screening\logs
echo   3. Open: %LATEST_LOG%
echo.

echo ================================================================================
echo.

pause
