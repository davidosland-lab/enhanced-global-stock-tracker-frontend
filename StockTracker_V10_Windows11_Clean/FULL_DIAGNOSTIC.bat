@echo off
echo ========================================
echo StockTracker V10 - Full System Diagnostic
echo ========================================
echo.
echo This will run a complete diagnostic and generate a report.
echo.

REM Create diagnostic folder
if not exist "diagnostic_results" mkdir diagnostic_results

REM Set timestamp for report
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do set mydate=%%c-%%a-%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a-%%b
set timestamp=%mydate%_%mytime%
set report_file=diagnostic_results\diagnostic_report_%timestamp%.txt

echo Starting diagnostic at %date% %time% > %report_file%
echo ======================================== >> %report_file%
echo. >> %report_file%

REM Run Python diagnostic script
echo Running comprehensive diagnostic...
echo.

REM Check if venv exists
if exist "venv\Scripts\python.exe" (
    call venv\Scripts\activate.bat
    python comprehensive_diagnostic_fixed.py >> %report_file% 2>&1
) else (
    echo ERROR: Virtual environment not found! >> %report_file%
    echo Please run INSTALL.bat first >> %report_file%
    python comprehensive_diagnostic_fixed.py >> %report_file% 2>&1
)

echo.
echo ========================================
echo Diagnostic Complete!
echo ========================================
echo.
echo Report saved to: %report_file%
echo.
type %report_file%
echo.
pause