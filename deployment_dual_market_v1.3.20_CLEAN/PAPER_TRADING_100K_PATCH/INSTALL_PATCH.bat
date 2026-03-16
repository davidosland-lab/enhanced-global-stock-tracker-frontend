@echo off
REM =====================================================================
REM PAPER TRADING $100K PATCH INSTALLER
REM =====================================================================
REM
REM This patch increases paper trading account from $10,000 to $100,000
REM
REM =====================================================================

echo.
echo ========================================================================
echo    PAPER TRADING $100K PATCH INSTALLER
echo ========================================================================
echo.
echo This patch will update your paper trading account limit:
echo   FROM: $10,000
echo   TO:   $100,000
echo.
echo Files to be updated:
echo   - models\trading\trade_database.py
echo   - models\trading\paper_trading_engine.py
echo   - models\trading\portfolio_manager.py
echo   - app_finbert_v4_dev.py
echo   - templates\finbert_v4_enhanced_ui.html
echo.
pause

REM Check if we're in the right directory
if not exist "finbert_v4.4.4\models\trading\trade_database.py" (
    echo.
    echo ======================================================================
    echo ERROR: Wrong directory!
    echo ======================================================================
    echo.
    echo This script must be run from: C:\Users\david\AATelS\
    echo.
    echo Current directory: %CD%
    echo.
    echo Please:
    echo   1. Extract PAPER_TRADING_100K_PATCH.zip to C:\Users\david\AATelS\
    echo   2. Open Command Prompt
    echo   3. Run: cd C:\Users\david\AATelS
    echo   4. Run: PAPER_TRADING_100K_PATCH\INSTALL_PATCH.bat
    echo.
    pause
    exit /b 1
)

echo.
echo Step 1: Creating Backup
echo ========================================================================
set BACKUP_DIR=finbert_v4.4.4\BACKUP_PAPER_TRADING_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

mkdir "%BACKUP_DIR%\models\trading" 2>nul
mkdir "%BACKUP_DIR%\templates" 2>nul

echo Backing up original files...
copy finbert_v4.4.4\models\trading\trade_database.py "%BACKUP_DIR%\models\trading\" >nul
copy finbert_v4.4.4\models\trading\paper_trading_engine.py "%BACKUP_DIR%\models\trading\" >nul
copy finbert_v4.4.4\models\trading\portfolio_manager.py "%BACKUP_DIR%\models\trading\" >nul
copy finbert_v4.4.4\app_finbert_v4_dev.py "%BACKUP_DIR%\" >nul
copy finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html "%BACKUP_DIR%\templates\" >nul

echo ✓ Backup created: %BACKUP_DIR%
echo.

echo Step 2: Installing Updated Files
echo ========================================================================
echo Copying updated files...
echo.

REM Check if patch directory exists
if not exist "PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py" (
    echo ✗ ERROR: Patch files not found!
    echo.
    echo Looking for: PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py
    echo Current directory: %CD%
    echo.
    echo Please ensure:
    echo   1. You extracted PAPER_TRADING_100K_PATCH.zip to C:\Users\david\AATelS\
    echo   2. The PAPER_TRADING_100K_PATCH folder exists
    echo   3. You are running this from C:\Users\david\AATelS\
    echo.
    echo Directory contents:
    dir /b | find "PAPER_TRADING"
    echo.
    pause
    exit /b 1
)

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py finbert_v4.4.4\models\trading\ >nul 2>&1
if errorlevel 1 (
    echo ✗ Failed to copy trade_database.py
    echo.
    echo Trying to diagnose the issue...
    echo Source exists: 
    if exist "PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py" (echo   YES) else (echo   NO)
    echo Target directory exists:
    if exist "finbert_v4.4.4\models\trading\" (echo   YES) else (echo   NO - creating...)
    mkdir "finbert_v4.4.4\models\trading\" 2>nul
    echo.
    echo Retrying copy...
    copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\trade_database.py finbert_v4.4.4\models\trading\
    if errorlevel 1 (
        echo ✗ Copy still failed!
        echo Please check file permissions and try running as Administrator
        pause
        exit /b 1
    )
)
echo ✓ Updated: models\trading\trade_database.py

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\paper_trading_engine.py finbert_v4.4.4\models\trading\ >nul
if errorlevel 1 (
    echo ✗ Failed to copy paper_trading_engine.py
    pause
    exit /b 1
)
echo ✓ Updated: models\trading\paper_trading_engine.py

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\models\trading\portfolio_manager.py finbert_v4.4.4\models\trading\ >nul
if errorlevel 1 (
    echo ✗ Failed to copy portfolio_manager.py
    pause
    exit /b 1
)
echo ✓ Updated: models\trading\portfolio_manager.py

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\app_finbert_v4_dev.py finbert_v4.4.4\ >nul
if errorlevel 1 (
    echo ✗ Failed to copy app_finbert_v4_dev.py
    pause
    exit /b 1
)
echo ✓ Updated: app_finbert_v4_dev.py

copy /Y PAPER_TRADING_100K_PATCH\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html finbert_v4.4.4\templates\ >nul
if errorlevel 1 (
    echo ✗ Failed to copy finbert_v4_enhanced_ui.html
    pause
    exit /b 1
)
echo ✓ Updated: templates\finbert_v4_enhanced_ui.html

echo.
echo Step 3: Clearing Python Cache
echo ========================================================================
echo Removing cached bytecode...
for /d /r finbert_v4.4.4\models\trading %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /q finbert_v4.4.4\models\trading\*.pyc 2>nul
echo ✓ Python cache cleared
echo.

echo Step 4: Verification
echo ========================================================================
echo Checking updated files...

findstr /C:"DEFAULT 100000" finbert_v4.4.4\models\trading\trade_database.py >nul
if errorlevel 1 (
    echo ✗ trade_database.py verification FAILED
    echo   Expected to find "DEFAULT 100000" in the file
    pause
    exit /b 1
)
echo ✓ trade_database.py - Contains 100000 defaults

findstr /C:"initial_capital: float = 100000" finbert_v4.4.4\models\trading\paper_trading_engine.py >nul
if errorlevel 1 (
    echo ✗ paper_trading_engine.py verification FAILED
    pause
    exit /b 1
)
echo ✓ paper_trading_engine.py - Contains 100000 default

findstr /C:"initial_capital: float = 100000" finbert_v4.4.4\models\trading\portfolio_manager.py >nul
if errorlevel 1 (
    echo ✗ portfolio_manager.py verification FAILED
    pause
    exit /b 1
)
echo ✓ portfolio_manager.py - Contains 100000 default

findstr /C:"initial_capital.*100000" finbert_v4.4.4\app_finbert_v4_dev.py >nul
if errorlevel 1 (
    echo ✗ app_finbert_v4_dev.py verification FAILED
    pause
    exit /b 1
)
echo ✓ app_finbert_v4_dev.py - Contains 100000 references

findstr /C:"$100,000" finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html >nul
if errorlevel 1 (
    echo ✗ finbert_v4_enhanced_ui.html verification FAILED
    pause
    exit /b 1
)
echo ✓ finbert_v4_enhanced_ui.html - Contains $100,000 message

echo.
echo ========================================================================
echo    ✅ ALL CHECKS PASSED!
echo ========================================================================
echo.
echo Patch installed successfully!
echo.
echo IMPORTANT: Reset your account to apply the new $100,000 limit:
echo.
echo Option 1: Python Command
echo -----------------------
echo cd C:\Users\david\AATelS\finbert_v4.4.4
echo python -c "from models.trading.paper_trading_engine import PaperTradingEngine; engine = PaperTradingEngine(); engine.reset_account(100000); print('Account reset to $100,000')"
echo.
echo Option 2: Delete Database (Fresh Start)
echo ----------------------------------------
echo cd C:\Users\david\AATelS\finbert_v4.4.4
echo del trading.db
echo (Database will recreate with $100,000 on first use)
echo.
echo Option 3: Web UI
echo ----------------
echo 1. Run: python finbert_v4.4.4\app_finbert_v4_dev.py
echo 2. Open: http://localhost:5000
echo 3. Go to Paper Trading section
echo 4. Click "Reset Account"
echo.
echo Backup location: %BACKUP_DIR%
echo.
echo ========================================================================
echo.
pause
