@echo off
REM ============================================================================
REM Complete Overnight Pipeline Workflow
REM ============================================================================

echo.
echo ================================================================================
echo COMPLETE OVERNIGHT PIPELINE WORKFLOW
echo ================================================================================
echo.
echo This will run overnight pipelines for all three markets:
echo   - AU Market: 268 stocks
echo   - US Market: 212 stocks  
echo   - UK Market: 240 stocks
echo.
echo Total: 720 stocks
echo Estimated time: ~60 minutes
echo.
pause

echo.
echo [1/3] Running AU Pipeline...
python scripts\run_au_pipeline_v1.3.13.py --full-scan
if %errorlevel% neq 0 (
    echo WARNING: AU pipeline failed
)

echo.
echo [2/3] Running US Pipeline...
python scripts\run_us_full_pipeline.py --full-scan
if %errorlevel% neq 0 (
    echo WARNING: US pipeline failed
)

echo.
echo [3/3] Running UK Pipeline...
python scripts\run_uk_full_pipeline.py --full-scan
if %errorlevel% neq 0 (
    echo WARNING: UK pipeline failed
)

echo.
echo ================================================================================
echo PIPELINE WORKFLOW COMPLETE
echo ================================================================================
echo.
echo Morning reports generated:
echo   - reports\screening\au_morning_report.json
echo   - reports\screening\us_morning_report.json
echo   - reports\screening\uk_morning_report.json
echo.
echo Next: Run paper trading with fresh data
echo   cd core
echo   python paper_trading_coordinator.py --symbols AAPL,MSFT --capital 100000
echo.
pause
