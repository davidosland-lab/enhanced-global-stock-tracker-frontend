@echo off
REM Quick Log Checker - Check if LSTM and Regime Engine ran

echo ========================================
echo Checking Pipeline Logs
echo ========================================
echo.

if not exist "logs\screening\overnight_pipeline.log" (
    echo [ERROR] Log file not found!
    echo The pipeline may not have run yet.
    echo.
    echo Run: RUN_PIPELINE.bat
    pause
    exit /b 1
)

echo Checking logs\screening\overnight_pipeline.log
echo.

echo ========================================
echo 1. CHECKING FOR PHASE 4.5 (LSTM TRAINING)
echo ========================================
findstr /C:"PHASE 4.5: LSTM MODEL TRAINING" logs\screening\overnight_pipeline.log
if %ERRORLEVEL% EQU 0 (
    echo [FOUND] PHASE 4.5 exists in logs
) else (
    echo [NOT FOUND] PHASE 4.5 not in logs yet
    echo The pipeline may still be running or hasn't reached this phase.
)
echo.

echo ========================================
echo 2. CHECKING FOR LSTM TRAINING DEBUG LOGS
echo ========================================
findstr /C:"[DEBUG] LSTM Training Check" logs\screening\overnight_pipeline.log
if %ERRORLEVEL% EQU 0 (
    echo [FOUND] LSTM training check logged
) else (
    echo [NOT FOUND] LSTM training check not logged yet
)
echo.

echo ========================================
echo 3. CHECKING FOR REGIME ENGINE
echo ========================================
findstr /C:"Market Regime Engine" logs\screening\overnight_pipeline.log
if %ERRORLEVEL% EQU 0 (
    echo [FOUND] Regime engine mentioned in logs
) else (
    echo [NOT FOUND] Regime engine not in logs
)
echo.

findstr /C:"Market Regime:" logs\screening\overnight_pipeline.log
if %ERRORLEVEL% EQU 0 (
    echo [FOUND] Regime detection output found
) else (
    echo [NOT FOUND] Regime detection output not found yet
)
echo.

echo ========================================
echo 4. CHECKING PIPELINE PROGRESS
echo ========================================
echo Last 20 lines of log:
echo.
powershell -Command "Get-Content logs\screening\overnight_pipeline.log -Tail 20"
echo.

echo ========================================
echo 5. PIPELINE STATUS
echo ========================================
findstr /C:"PIPELINE COMPLETE" logs\screening\overnight_pipeline.log
if %ERRORLEVEL% EQU 0 (
    echo [STATUS] Pipeline has COMPLETED
) else (
    echo [STATUS] Pipeline is STILL RUNNING or INCOMPLETE
    echo.
    echo The pipeline may still be processing stocks.
    echo Expected runtime: 70-110 minutes for first run
    echo.
    echo To monitor in real-time, open:
    echo   logs\screening\overnight_pipeline.log
)
echo.

pause
