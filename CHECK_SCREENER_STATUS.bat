@echo off
REM ===================================================================
REM Check Overnight Screener Status
REM Displays last execution results and scheduled task status
REM ===================================================================

echo ========================================
echo   Overnight Screener Status
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if scheduled task exists
echo [1] SCHEDULED TASK STATUS
echo ----------------------------------------
schtasks /Query /TN "OvernightStockScreener" /FO LIST /V 2>nul
if errorlevel 1 (
    echo Task Status: NOT SCHEDULED
    echo Run SCHEDULE_SCREENER.bat to set up automation
) else (
    echo Task Status: SCHEDULED ✓
)
echo.

REM Check last execution
echo [2] LAST EXECUTION
echo ----------------------------------------
if exist "logs\screening\overnight_pipeline.log" (
    echo Log File: logs\screening\overnight_pipeline.log
    echo.
    echo Last 20 lines:
    echo ----------------------------------------
    powershell -Command "Get-Content logs\screening\overnight_pipeline.log -Tail 20"
) else (
    echo No execution log found
    echo The screener has not been run yet
)
echo.

REM Check latest report
echo [3] LATEST REPORT
echo ----------------------------------------
if exist "reports\morning_reports" (
    echo Reports Directory: reports\morning_reports\
    echo.
    echo Recent reports:
    dir /B /O-D "reports\morning_reports\*_market_report.html" 2>nul | findstr /R ".*" >nul
    if errorlevel 1 (
        echo No reports found yet
    ) else (
        dir /B /O-D "reports\morning_reports\*_market_report.html" | head -5
    )
) else (
    echo Reports directory does not exist
)
echo.

REM Check pipeline state
echo [4] PIPELINE STATE
echo ----------------------------------------
if exist "logs\screening" (
    dir /B /O-D "logs\screening\*_pipeline_state.json" 2>nul | findstr /R ".*" >nul
    if errorlevel 1 (
        echo No pipeline state files found
    ) else (
        echo Latest state file:
        for /F %%i in ('dir /B /O-D "logs\screening\*_pipeline_state.json"') do (
            echo   %%i
            goto :found_state
        )
        :found_state
    )
) else (
    echo Logs directory does not exist
)
echo.

REM Check for errors
echo [5] ERROR CHECK
echo ----------------------------------------
if exist "logs\screening\errors" (
    dir /B "logs\screening\errors\error_*.json" 2>nul | findstr /R ".*" >nul
    if errorlevel 1 (
        echo No errors found ✓
    ) else (
        echo Recent errors found:
        dir /B /O-D "logs\screening\errors\error_*.json" | head -3
        echo.
        echo Check error files for details
    )
) else (
    echo No error logs ✓
)
echo.

REM System info
echo [6] SYSTEM INFO
echo ----------------------------------------
echo Current Time: %TIME%
echo Current Date: %DATE%
if exist "venv\Scripts\python.exe" (
    echo Python: venv\Scripts\python.exe ✓
) else (
    echo Python: System Python (venv not found)
)
echo.

echo ========================================
echo   Status Check Complete
echo ========================================
echo.
echo To run the screener manually:
echo   RUN_OVERNIGHT_SCREENER.bat (full)
echo   RUN_OVERNIGHT_SCREENER_TEST.bat (test)
echo.
echo To view latest report in browser:
echo   start reports\morning_reports\[latest_date]_market_report.html
echo.

pause
