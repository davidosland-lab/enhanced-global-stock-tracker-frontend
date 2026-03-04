@echo off
REM ============================================================================
REM  HTML Morning Report Generator - Patch v193
REM  Adds HTML report generation to UK and US pipelines
REM  Date: 2026-03-01
REM ============================================================================

echo.
echo ========================================================================
echo  HTML Morning Report Generator - Patch v193
echo ========================================================================
echo.
echo This patch adds beautiful HTML morning reports to UK and US pipelines
echo (AU pipeline already has them)
echo.
echo What you'll get:
echo   - Professional HTML reports in addition to JSON
echo   - Easy to read in browser
echo   - Top opportunities, market sentiment, sector breakdown
echo   - System statistics and performance metrics
echo.
echo Installation: 10 seconds
echo.
pause

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.7+ and add to PATH
    pause
    exit /b 1
)

REM Run the patch script
python add_html_reports.py

echo.
echo ========================================================================
echo  Installation complete!
echo ========================================================================
echo.
echo Next: Run tonight's UK/US pipelines to generate HTML reports
echo   Command: python scripts/run_us_full_pipeline.py --full-scan
echo   Command: python scripts/run_uk_full_pipeline.py --full-scan
echo.
pause
