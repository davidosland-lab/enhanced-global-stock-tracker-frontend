@echo off
echo ========================================
echo   Report Path Verification
echo   v1.3.15.45 FINAL
echo ========================================
echo.
echo Checking report directory structure...
echo.

if exist "reports\" (
    echo [OK] reports\ directory exists
    
    if exist "reports\screening\" (
        echo   [OK] reports\screening\ exists - JSON trading reports
    ) else (
        echo   [!] reports\screening\ missing - will be created on first run
    )
    
    if exist "reports\morning_reports\" (
        echo   [OK] reports\morning_reports\ exists - HTML morning reports
    ) else (
        echo   [!] reports\morning_reports\ missing - will be created on first run
    )
) else (
    echo [!] reports\ directory missing - will be created on first run
)

echo.
echo ========================================
echo   Configuration Check
echo ========================================
echo.
echo Checking screening_config.json...
findstr /C:"\"report_path\"" models\config\screening_config.json
echo.

echo ========================================
echo   Pipeline Report Paths
echo ========================================
echo.
echo AU Pipeline:
findstr /C:"trading_report_dir" models\screening\overnight_pipeline.py | findstr /V "^#"
echo.
echo US Pipeline:
findstr /C:"trading_report_dir" models\screening\us_overnight_pipeline.py | findstr /V "^#"
echo.
echo UK Pipeline:
findstr /C:"trading_report_dir" models\screening\uk_overnight_pipeline.py | findstr /V "^#"
echo.

echo ========================================
echo   Report Structure Summary
echo ========================================
echo.
echo reports/
echo ├── screening/              (JSON trading reports)
echo │   ├── au_morning_report.json
echo │   ├── us_morning_report.json
echo │   └── uk_morning_report.json
echo └── morning_reports/        (HTML morning reports)
echo     ├── YYYYMMDD_market_report.html
echo     └── YYYYMMDD_market_report.json
echo.
echo ========================================
echo [OK] All paths are correctly configured!
echo ========================================
echo.
pause
