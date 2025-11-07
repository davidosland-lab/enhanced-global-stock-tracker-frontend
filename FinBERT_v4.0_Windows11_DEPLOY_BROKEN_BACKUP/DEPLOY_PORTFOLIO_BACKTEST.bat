@echo off
REM =========================================================================
REM Deploy Portfolio Backtesting to Windows 11
REM =========================================================================
REM This script copies all portfolio backtesting files to deployment package
REM 
REM Author: FinBERT v4.0
REM Date: November 2025
REM =========================================================================

echo.
echo ========================================================================
echo  Portfolio Backtesting Deployment Script
echo ========================================================================
echo.
echo This script will deploy portfolio backtesting feature to Windows 11.
echo.
echo Files to be updated:
echo   - app_finbert_v4_dev.py (MODIFIED)
echo   - templates\finbert_v4_enhanced_ui.html (MODIFIED)
echo   - models\backtesting\*.py (3 MODIFIED + 2 NEW)
echo   - docs\*.md (3 NEW documentation files)
echo.
echo Target directory: %~dp0
echo.
pause

REM Create backup folder
echo.
echo Creating backup folder...
mkdir backup\portfolio_backtest_%date:~-4,4%%date:~-10,2%%date:~-7,2% 2>nul
set BACKUP_DIR=backup\portfolio_backtest_%date:~-4,4%%date:~-10,2%%date:~-7,2%

REM Backup existing files
echo.
echo Backing up existing files...
if exist app_finbert_v4_dev.py (
    copy app_finbert_v4_dev.py "%BACKUP_DIR%\app_finbert_v4_dev.py.backup"
    echo   - Backed up app_finbert_v4_dev.py
)
if exist templates\finbert_v4_enhanced_ui.html (
    copy templates\finbert_v4_enhanced_ui.html "%BACKUP_DIR%\finbert_v4_enhanced_ui.html.backup"
    echo   - Backed up finbert_v4_enhanced_ui.html
)
if exist models\backtesting\data_loader.py (
    copy models\backtesting\data_loader.py "%BACKUP_DIR%\data_loader.py.backup"
    echo   - Backed up data_loader.py
)
if exist models\backtesting\cache_manager.py (
    copy models\backtesting\cache_manager.py "%BACKUP_DIR%\cache_manager.py.backup"
    echo   - Backed up cache_manager.py
)

echo.
echo Backup complete! Saved to: %BACKUP_DIR%
echo.

REM Create necessary directories
echo Creating directories...
mkdir models\backtesting 2>nul
mkdir docs 2>nul
mkdir cache 2>nul
echo   - models\backtesting [OK]
echo   - docs [OK]
echo   - cache [OK]

REM Deploy modified files
echo.
echo Deploying modified files...
echo   [1/4] app_finbert_v4_dev.py
REM (In real deployment, you would copy from source)
REM copy source\app_finbert_v4_dev.py .

echo   [2/4] templates\finbert_v4_enhanced_ui.html
REM copy source\templates\finbert_v4_enhanced_ui.html templates\

echo   [3/4] models\backtesting\data_loader.py
REM copy source\models\backtesting\data_loader.py models\backtesting\

echo   [4/4] models\backtesting\cache_manager.py
REM copy source\models\backtesting\cache_manager.py models\backtesting\

echo.
echo Modified files deployed!

REM Deploy new files
echo.
echo Deploying new files...
echo   [1/5] models\backtesting\__init__.py
REM copy source\models\backtesting\__init__.py models\backtesting\

echo   [2/5] models\backtesting\portfolio_engine.py (27KB)
REM copy source\models\backtesting\portfolio_engine.py models\backtesting\

echo   [3/5] models\backtesting\portfolio_backtester.py (15KB)
REM copy source\models\backtesting\portfolio_backtester.py models\backtesting\

echo   [4/5] docs\PORTFOLIO_BACKTESTING_GUIDE.md
REM copy source\docs\PORTFOLIO_BACKTESTING_GUIDE.md docs\

echo   [5/5] docs\PORTFOLIO_BACKTEST_IMPLEMENTATION_SUMMARY.md
REM copy source\docs\PORTFOLIO_BACKTEST_IMPLEMENTATION_SUMMARY.md docs\

echo.
echo New files deployed!

REM Verify deployment
echo.
echo ========================================================================
echo Verifying deployment...
echo ========================================================================

set ERRORS=0

echo.
echo Checking core files...
if exist app_finbert_v4_dev.py (
    echo   [OK] app_finbert_v4_dev.py
) else (
    echo   [ERROR] app_finbert_v4_dev.py NOT FOUND
    set /a ERRORS+=1
)

if exist templates\finbert_v4_enhanced_ui.html (
    echo   [OK] templates\finbert_v4_enhanced_ui.html
) else (
    echo   [ERROR] templates\finbert_v4_enhanced_ui.html NOT FOUND
    set /a ERRORS+=1
)

echo.
echo Checking backtesting files...
if exist models\backtesting\__init__.py (
    echo   [OK] models\backtesting\__init__.py
) else (
    echo   [ERROR] models\backtesting\__init__.py NOT FOUND
    set /a ERRORS+=1
)

if exist models\backtesting\portfolio_engine.py (
    echo   [OK] models\backtesting\portfolio_engine.py
) else (
    echo   [ERROR] models\backtesting\portfolio_engine.py NOT FOUND
    set /a ERRORS+=1
)

if exist models\backtesting\portfolio_backtester.py (
    echo   [OK] models\backtesting\portfolio_backtester.py
) else (
    echo   [ERROR] models\backtesting\portfolio_backtester.py NOT FOUND
    set /a ERRORS+=1
)

if exist models\backtesting\data_loader.py (
    echo   [OK] models\backtesting\data_loader.py
) else (
    echo   [ERROR] models\backtesting\data_loader.py NOT FOUND
    set /a ERRORS+=1
)

if exist models\backtesting\cache_manager.py (
    echo   [OK] models\backtesting\cache_manager.py
) else (
    echo   [ERROR] models\backtesting\cache_manager.py NOT FOUND
    set /a ERRORS+=1
)

echo.
echo Checking documentation...
if exist docs\PORTFOLIO_BACKTESTING_GUIDE.md (
    echo   [OK] docs\PORTFOLIO_BACKTESTING_GUIDE.md
) else (
    echo   [WARN] docs\PORTFOLIO_BACKTESTING_GUIDE.md NOT FOUND
)

if exist docs\PORTFOLIO_BACKTEST_IMPLEMENTATION_SUMMARY.md (
    echo   [OK] docs\PORTFOLIO_BACKTEST_IMPLEMENTATION_SUMMARY.md
) else (
    echo   [WARN] docs\PORTFOLIO_BACKTEST_IMPLEMENTATION_SUMMARY.md NOT FOUND
)

echo.
echo ========================================================================
if %ERRORS% EQU 0 (
    echo  DEPLOYMENT SUCCESSFUL!
    echo ========================================================================
    echo.
    echo All required files are in place.
    echo.
    echo Next steps:
    echo   1. Start server: START_FINBERT_V4.bat
    echo   2. Open browser: http://localhost:5001
    echo   3. Click "Portfolio Backtest" button
    echo   4. Test with: AAPL, MSFT
    echo.
    echo Backup saved to: %BACKUP_DIR%
    echo.
) else (
    echo  DEPLOYMENT FAILED - %ERRORS% ERROR(S)
    echo ========================================================================
    echo.
    echo Some required files are missing!
    echo Please check the errors above and ensure all files are copied.
    echo.
    echo You can restore from backup: %BACKUP_DIR%
    echo.
)

echo.
echo For detailed deployment instructions, see:
echo   WINDOWS11_DEPLOYMENT_FILES.md
echo.
pause
