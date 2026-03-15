@echo off
REM ============================================================================
REM PIPELINE-ENHANCED TRADING DEPLOYMENT PACKAGE CREATOR
REM Version: 1.4.0 - Pipeline Integration Edition
REM Date: 2026-01-03
REM ============================================================================

echo.
echo ============================================================================
echo   CREATING PIPELINE-ENHANCED TRADING DEPLOYMENT PACKAGE
echo ============================================================================
echo.
echo Starting deployment package creation...
echo.

REM Get timestamp for package naming
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%

REM Define package name
set PACKAGE_NAME=pipeline_enhanced_trading_v1.4.0_%TIMESTAMP%

echo Package Name: %PACKAGE_NAME%
echo.

REM Create temporary deployment directory
set DEPLOY_DIR=temp_deploy_%TIMESTAMP%
mkdir %DEPLOY_DIR%

echo [1/8] Copying Phase 3 Intraday Deployment...
xcopy /E /I /Y phase3_intraday_deployment %DEPLOY_DIR%\phase3_intraday_deployment >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to copy phase3_intraday_deployment
    goto :error
)
echo       ✓ Phase 3 deployment copied

echo [2/8] Copying Pipeline Trading System...
xcopy /E /I /Y pipeline_trading %DEPLOY_DIR%\pipeline_trading >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to copy pipeline_trading
    goto :error
)
echo       ✓ Pipeline trading system copied

echo [3/8] Copying ML Pipeline Components...
if exist ml_pipeline (
    xcopy /E /I /Y ml_pipeline %DEPLOY_DIR%\ml_pipeline >nul 2>&1
    echo       ✓ ML pipeline components copied
) else (
    echo       ⚠ ML pipeline directory not found - skipping
)

echo [4/8] Copying Core Configuration Files...
for %%F in (
    config.json
    live_trading_config.json
    screening_config.json
    au_sectors.json
    us_sectors.json
    uk_sectors.json
) do (
    if exist %%F (
        copy /Y %%F %DEPLOY_DIR%\ >nul 2>&1
        echo       ✓ %%F
    )
)

echo [5/8] Copying Documentation...
for %%F in (
    PIPELINE_TRADING_INTEGRATION.md
    OVERNIGHT_INDICATORS_FINAL_SUMMARY.md
    WINDOWS_SCHEDULER_GUIDE.md
    MARKET_PIPELINES_README.md
    SCHEDULE_VERIFICATION_REPORT.md
    README.md
    DEPLOYMENT_README.md
) do (
    if exist %%F (
        copy /Y %%F %DEPLOY_DIR%\ >nul 2>&1
        echo       ✓ %%F
    ) else if exist phase3_intraday_deployment\%%F (
        copy /Y phase3_intraday_deployment\%%F %DEPLOY_DIR%\ >nul 2>&1
        echo       ✓ %%F
    )
)

echo [6/8] Creating Installation Scripts...

REM Create main installation script
(
echo @echo off
echo REM ============================================================================
echo REM PIPELINE-ENHANCED TRADING SYSTEM - INSTALLATION
echo REM ============================================================================
echo.
echo echo Installing Pipeline-Enhanced Trading System v1.4.0...
echo echo.
echo.
echo REM Install Python dependencies
echo echo [1/4] Installing Python dependencies...
echo pip install -r requirements.txt
echo if errorlevel 1 ^(
echo     echo ERROR: Failed to install dependencies
echo     pause
echo     exit /b 1
echo ^)
echo echo       ✓ Dependencies installed
echo.
echo REM Install schedule library for pipeline automation
echo echo [2/4] Installing pipeline scheduler...
echo pip install schedule pytz
echo echo       ✓ Pipeline scheduler installed
echo.
echo REM Setup logging directories
echo echo [3/4] Setting up directories...
echo if not exist logs mkdir logs
echo if not exist logs\screening mkdir logs\screening
echo if not exist logs\screening\au mkdir logs\screening\au
echo if not exist logs\screening\us mkdir logs\screening\us
echo if not exist logs\screening\uk mkdir logs\screening\uk
echo if not exist state mkdir state
echo if not exist reports mkdir reports
echo if not exist reports\au mkdir reports\au
echo if not exist reports\us mkdir reports\us
echo if not exist reports\uk mkdir reports\uk
echo echo       ✓ Directories created
echo.
echo echo [4/4] Setting up automated pipeline scheduler...
echo echo Please run SETUP_WINDOWS_TASK.bat as Administrator to enable automatic pipeline execution
echo echo.
echo echo ============================================================================
echo echo   INSTALLATION COMPLETE
echo echo ============================================================================
echo echo.
echo echo Next Steps:
echo echo   1. Review PIPELINE_TRADING_INTEGRATION.md for system overview
echo echo   2. Review SCHEDULE_VERIFICATION_REPORT.md for pipeline timing
echo echo   3. Run SETUP_WINDOWS_TASK.bat as Administrator
echo echo   4. Test with TEST_PIPELINE_SCHEDULER.bat
echo echo   5. Start trading with run_pipeline_enhanced_trading.py
echo echo.
echo pause
) > %DEPLOY_DIR%\INSTALL.bat

echo       ✓ INSTALL.bat created

REM Create requirements.txt
(
echo # Pipeline-Enhanced Trading System Requirements
echo # Version: 1.4.0
echo # Date: 2026-01-03
echo.
echo # Core Dependencies
echo pandas^>=2.0.0
echo numpy^>=1.24.0
echo yfinance^>=0.2.28
echo yahooquery^>=2.3.0
echo.
echo # ML/Prediction
echo scikit-learn^>=1.3.0
echo xgboost^>=2.0.0
echo lightgbm^>=4.0.0
echo.
echo # Technical Analysis
echo ta-lib^>=0.4.28
echo pandas-ta^>=0.3.14b
echo.
echo # Visualization
echo plotly^>=5.14.0
echo dash^>=2.11.0
echo dash-bootstrap-components^>=1.4.0
echo.
echo # Scheduling and Automation
echo schedule^>=1.2.0
echo pytz^>=2023.3
echo.
echo # Data Processing
echo python-dateutil^>=2.8.0
echo requests^>=2.31.0
echo.
echo # Optional: Advanced Features
echo tensorflow^>=2.13.0
echo torch^>=2.0.0
) > %DEPLOY_DIR%\requirements.txt

echo       ✓ requirements.txt created

echo [7/8] Creating Quick Start Guide...
(
echo # PIPELINE-ENHANCED TRADING SYSTEM v1.4.0
echo # Quick Start Guide
echo.
echo ## What's New in v1.4.0
echo.
echo This version integrates overnight pipeline screening with automated trading:
echo.
echo - **Automated Pipeline Execution**: Runs 2.5 hours before each market opens
echo - **Multi-Market Support**: AU ^(ASX^), US ^(NYSE/NASDAQ^), UK ^(LSE^)
echo - **Flexible Position Sizing**: 5-30%% based on sentiment, risk, and opportunity
echo - **Opportunity Mode**: Up to 150%% sizing for high-confidence signals
echo - **Risk Override**: Automatic position reduction/exit on elevated risk
echo.
echo ## Installation
echo.
echo 1. Run `INSTALL.bat` to install dependencies
echo 2. Run `SETUP_WINDOWS_TASK.bat` as Administrator for automated scheduling
echo 3. Test with `TEST_PIPELINE_SCHEDULER.bat`
echo.
echo ## Pipeline Schedule ^(Verified^)
echo.
echo - **AU Market**: Pipeline runs 07:30 AEDT ^(market opens 10:00^)
echo - **US Market**: Pipeline runs 07:00 EST ^(market opens 09:30^)
echo - **UK Market**: Pipeline runs 05:30 GMT ^(market opens 08:00^)
echo.
echo Each pipeline runs 2.5 hours before market open, providing morning reports
echo with sentiment analysis, opportunity scoring, and trading signals.
echo.
echo ## Usage
echo.
echo ### Automated Mode ^(Recommended^)
echo.
echo Once Windows Task Scheduler is set up, pipelines run automatically.
echo Start the trading system with:
echo.
echo ```bash
echo python phase3_intraday_deployment/run_pipeline_enhanced_trading.py --market AU
echo ```
echo.
echo Available markets: AU, US, UK, ALL
echo.
echo ### Manual Pipeline Execution
echo.
echo Run pipelines manually if needed:
echo.
echo ```bash
echo # Australian market
echo cd pipeline_trading
echo python scripts/run_au_morning_report.py
echo.
echo # US market
echo python scripts/run_us_morning_report.py
echo.
echo # UK market
echo python scripts/run_uk_morning_report.py
echo ```
echo.
echo ### Trading System Options
echo.
echo ```bash
echo # Single market with default capital
echo python run_pipeline_enhanced_trading.py --market US
echo.
echo # Custom capital allocation
echo python run_pipeline_enhanced_trading.py --market US --capital 50000
echo.
echo # All markets ^(capital split automatically^)
echo python run_pipeline_enhanced_trading.py --market ALL --capital 150000
echo.
echo # Dry run ^(no actual trades^)
echo python run_pipeline_enhanced_trading.py --market US --dry-run
echo.
echo # Opportunity mode ^(up to 150%% sizing^)
echo python run_pipeline_enhanced_trading.py --market US --opportunity-mode
echo ```
echo.
echo ## Key Documents
echo.
echo - `PIPELINE_TRADING_INTEGRATION.md` - Complete integration guide
echo - `SCHEDULE_VERIFICATION_REPORT.md` - Pipeline timing verification
echo - `WINDOWS_SCHEDULER_GUIDE.md` - Automated scheduling setup
echo - `OVERNIGHT_INDICATORS_FINAL_SUMMARY.md` - Overnight indicators overview
echo.
echo ## Monitoring
echo.
echo - Pipeline logs: `logs/pipeline_scheduler.log`
echo - Trading logs: `phase3_intraday_deployment/logs/paper_trading.log`
echo - Morning reports: `pipeline_trading/reports/{au,us,uk}/morning_report_YYYYMMDD.html`
echo.
echo ## Support
echo.
echo For issues or questions, review the documentation files included in this package.
echo.
echo ---
echo Version: 1.4.0 ^| Date: 2026-01-03 ^| Status: Production Ready
) > %DEPLOY_DIR%\QUICK_START.md

echo       ✓ QUICK_START.md created

echo [8/8] Creating deployment package archive...

REM Use PowerShell to create zip file
powershell -Command "Compress-Archive -Path '%DEPLOY_DIR%\*' -DestinationPath '%PACKAGE_NAME%.zip' -Force"

if errorlevel 1 (
    echo ERROR: Failed to create zip archive
    goto :error
)

echo       ✓ Package created: %PACKAGE_NAME%.zip

REM Cleanup
echo.
echo Cleaning up temporary files...
rmdir /S /Q %DEPLOY_DIR%
echo       ✓ Cleanup complete

echo.
echo ============================================================================
echo   DEPLOYMENT PACKAGE CREATED SUCCESSFULLY
echo ============================================================================
echo.
echo Package: %PACKAGE_NAME%.zip
echo Location: %CD%\%PACKAGE_NAME%.zip
echo.
for %%F in (%PACKAGE_NAME%.zip) do echo Size: %%~zF bytes
echo.
echo Contents:
echo   - Phase 3 Intraday Deployment System
echo   - Pipeline Trading System ^(AU/US/UK^)
echo   - ML Pipeline Components
echo   - Automated Pipeline Scheduler
echo   - Configuration Files
echo   - Documentation and Guides
echo   - Installation Scripts
echo.
echo Ready for deployment to Windows 11 production environment.
echo.
pause
goto :end

:error
echo.
echo ============================================================================
echo   ERROR OCCURRED DURING PACKAGE CREATION
echo ============================================================================
echo.
echo Please check the error messages above and try again.
echo.
if exist %DEPLOY_DIR% rmdir /S /Q %DEPLOY_DIR%
pause
exit /b 1

:end
echo Package creation complete.
exit /b 0
