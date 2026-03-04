@echo off
REM ==============================================================================
REM COMPLETE_PATCH_v1.3.15.45 Installer
REM Unified FinBERT Integration - Sentiment Gates
REM ==============================================================================

echo.
echo ================================================================================
echo                COMPLETE_PATCH_v1.3.15.45 Installer
echo         Unified FinBERT Integration - Critical Sentiment Fix
echo ================================================================================
echo.
echo What this patch fixes:
echo   - 65%% Negative sentiment now BLOCKS trades
echo   - Unified FinBERT v4.4.4 across all components
echo   - Dashboard shows sentiment breakdown and gate status
echo.
echo.

REM ==============================================================================
REM Ask user for installation directory
REM ==============================================================================

echo This installer will copy files to your installation directory.
echo.
echo Default installation directory:
echo   C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15
echo.
set /p "INSTALL_DIR=Enter installation directory (or press Enter for default): "

REM Use default if nothing entered
if "%INSTALL_DIR%"=="" (
    set "INSTALL_DIR=C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15"
    echo Using default: %INSTALL_DIR%
)

echo.
echo Installation directory: %INSTALL_DIR%
echo.

REM ==============================================================================
REM Verify directory exists and has required files
REM ==============================================================================

echo [1/7] Verifying installation directory...

if not exist "%INSTALL_DIR%" (
    echo.
    echo ERROR: Directory does not exist: %INSTALL_DIR%
    echo.
    echo Please create the directory or enter the correct path.
    echo.
    pause
    exit /b 1
)

if not exist "%INSTALL_DIR%\models\screening" (
    echo.
    echo ERROR: models\screening directory not found in: %INSTALL_DIR%
    echo.
    echo This does not appear to be a valid installation directory.
    echo.
    echo Expected structure:
    echo   %INSTALL_DIR%\models\screening\
    echo.
    pause
    exit /b 1
)

echo   - OK: Installation directory found
echo   - OK: models\screening directory found
echo.

REM ==============================================================================
REM Create Backup
REM ==============================================================================

echo [2/7] Creating backup...

set "TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "BACKUP_DIR=%INSTALL_DIR%\backup_%TIMESTAMP%"

mkdir "%BACKUP_DIR%" 2>nul
mkdir "%BACKUP_DIR%\models\screening" 2>nul

REM Backup existing files
if exist "%INSTALL_DIR%\models\screening\finbert_bridge.py" (
    copy "%INSTALL_DIR%\models\screening\finbert_bridge.py" "%BACKUP_DIR%\models\screening\" >nul 2>&1
    echo   - Backed up: finbert_bridge.py
)

if exist "%INSTALL_DIR%\models\screening\overnight_pipeline.py" (
    copy "%INSTALL_DIR%\models\screening\overnight_pipeline.py" "%BACKUP_DIR%\models\screening\" >nul 2>&1
    echo   - Backed up: overnight_pipeline.py
)

if exist "%INSTALL_DIR%\sentiment_integration.py" (
    copy "%INSTALL_DIR%\sentiment_integration.py" "%BACKUP_DIR%\" >nul 2>&1
    echo   - Backed up: sentiment_integration.py
)

if exist "%INSTALL_DIR%\paper_trading_coordinator.py" (
    copy "%INSTALL_DIR%\paper_trading_coordinator.py" "%BACKUP_DIR%\" >nul 2>&1
    echo   - Backed up: paper_trading_coordinator.py
)

if exist "%INSTALL_DIR%\unified_trading_dashboard.py" (
    copy "%INSTALL_DIR%\unified_trading_dashboard.py" "%BACKUP_DIR%\" >nul 2>&1
    echo   - Backed up: unified_trading_dashboard.py
)

echo   - Backup location: %BACKUP_DIR%
echo.

REM ==============================================================================
REM Get patch directory (where this script is located)
REM ==============================================================================

set "PATCH_DIR=%~dp0"
if "%PATCH_DIR:~-1%"=="\" set "PATCH_DIR=%PATCH_DIR:~0,-1%"

echo [3/7] Installing patch files from: %PATCH_DIR%
echo.

REM ==============================================================================
REM Install models/screening files
REM ==============================================================================

if exist "%PATCH_DIR%\models\screening\finbert_bridge.py" (
    copy /Y "%PATCH_DIR%\models\screening\finbert_bridge.py" "%INSTALL_DIR%\models\screening\" >nul 2>&1
    if errorlevel 1 (
        echo   - ERROR: Failed to copy finbert_bridge.py
        goto :install_error
    )
    echo   - Installed: models\screening\finbert_bridge.py
) else (
    echo   - WARNING: finbert_bridge.py not found in patch
)

if exist "%PATCH_DIR%\models\screening\overnight_pipeline.py" (
    copy /Y "%PATCH_DIR%\models\screening\overnight_pipeline.py" "%INSTALL_DIR%\models\screening\" >nul 2>&1
    if errorlevel 1 (
        echo   - ERROR: Failed to copy overnight_pipeline.py
        goto :install_error
    )
    echo   - Installed: models\screening\overnight_pipeline.py
) else (
    echo   - WARNING: overnight_pipeline.py not found in patch
)

REM ==============================================================================
REM Install root files
REM ==============================================================================

if exist "%PATCH_DIR%\sentiment_integration.py" (
    copy /Y "%PATCH_DIR%\sentiment_integration.py" "%INSTALL_DIR%\" >nul 2>&1
    if errorlevel 1 (
        echo   - ERROR: Failed to copy sentiment_integration.py
        goto :install_error
    )
    echo   - Installed: sentiment_integration.py (NEW)
) else (
    echo   - WARNING: sentiment_integration.py not found in patch
)

if exist "%PATCH_DIR%\paper_trading_coordinator.py" (
    copy /Y "%PATCH_DIR%\paper_trading_coordinator.py" "%INSTALL_DIR%\" >nul 2>&1
    if errorlevel 1 (
        echo   - ERROR: Failed to copy paper_trading_coordinator.py
        goto :install_error
    )
    echo   - Installed: paper_trading_coordinator.py
) else (
    echo   - WARNING: paper_trading_coordinator.py not found in patch
)

if exist "%PATCH_DIR%\unified_trading_dashboard.py" (
    copy /Y "%PATCH_DIR%\unified_trading_dashboard.py" "%INSTALL_DIR%\" >nul 2>&1
    if errorlevel 1 (
        echo   - ERROR: Failed to copy unified_trading_dashboard.py
        goto :install_error
    )
    echo   - Installed: unified_trading_dashboard.py
) else (
    echo   - WARNING: unified_trading_dashboard.py not found in patch
)

if exist "%PATCH_DIR%\test_finbert_integration.py" (
    copy /Y "%PATCH_DIR%\test_finbert_integration.py" "%INSTALL_DIR%\" >nul 2>&1
    echo   - Installed: test_finbert_integration.py (TEST)
) else (
    echo   - WARNING: test_finbert_integration.py not found in patch
)

echo.

REM ==============================================================================
REM Clear Python Cache
REM ==============================================================================

echo [4/7] Clearing Python cache...

if exist "%INSTALL_DIR%\__pycache__\" (
    del /Q "%INSTALL_DIR%\__pycache__\*.pyc" 2>nul
    echo   - Cleared: __pycache__
)

if exist "%INSTALL_DIR%\models\screening\__pycache__\" (
    del /Q "%INSTALL_DIR%\models\screening\__pycache__\*.pyc" 2>nul
    echo   - Cleared: models\screening\__pycache__
)

echo.

REM ==============================================================================
REM Verify Installation
REM ==============================================================================

echo [5/7] Verifying installation...

set "ALL_GOOD=1"

if not exist "%INSTALL_DIR%\models\screening\finbert_bridge.py" (
    echo   - ERROR: finbert_bridge.py not found
    set "ALL_GOOD=0"
) else (
    echo   - OK: finbert_bridge.py
)

if not exist "%INSTALL_DIR%\models\screening\overnight_pipeline.py" (
    echo   - ERROR: overnight_pipeline.py not found
    set "ALL_GOOD=0"
) else (
    echo   - OK: overnight_pipeline.py
)

if not exist "%INSTALL_DIR%\sentiment_integration.py" (
    echo   - ERROR: sentiment_integration.py not found
    set "ALL_GOOD=0"
) else (
    echo   - OK: sentiment_integration.py (NEW)
)

if not exist "%INSTALL_DIR%\paper_trading_coordinator.py" (
    echo   - ERROR: paper_trading_coordinator.py not found
    set "ALL_GOOD=0"
) else (
    echo   - OK: paper_trading_coordinator.py
)

if not exist "%INSTALL_DIR%\unified_trading_dashboard.py" (
    echo   - ERROR: unified_trading_dashboard.py not found
    set "ALL_GOOD=0"
) else (
    echo   - OK: unified_trading_dashboard.py
)

if "%ALL_GOOD%"=="0" (
    echo.
    echo ERROR: Installation verification failed!
    goto :install_error
)

echo.

REM ==============================================================================
REM Check Dependencies
REM ==============================================================================

echo [6/7] Checking Python dependencies...

python --version >nul 2>&1
if errorlevel 1 (
    echo   - WARNING: Python not found in PATH
    echo   - You may need to run commands with full Python path
) else (
    echo   - OK: Python found
)

echo.

REM ==============================================================================
REM Run Tests
REM ==============================================================================

echo [7/7] Ready to run tests...
echo.
echo Do you want to run the test suite now? (Recommended)
echo   - Tests verify all components are working
echo   - Takes about 10-15 seconds
echo.
set /p RUN_TESTS="Run tests? (Y/N): "

if /i "%RUN_TESTS%"=="Y" (
    echo.
    echo Running tests...
    echo.
    cd /d "%INSTALL_DIR%"
    python test_finbert_integration.py
    if errorlevel 1 (
        echo.
        echo WARNING: Some tests failed. Please review the output above.
        echo.
    ) else (
        echo.
        echo All tests passed!
        echo.
    )
) else (
    echo   - Skipped (you can run manually later)
    echo.
)

REM ==============================================================================
REM Installation Complete
REM ==============================================================================

echo ================================================================================
echo                         Installation Complete!
echo ================================================================================
echo.
echo Patch v1.3.15.45 installed successfully to:
echo   %INSTALL_DIR%
echo.
echo Backup location:
echo   %BACKUP_DIR%
echo.
echo What was installed:
echo   - models/screening/finbert_bridge.py (Enhanced)
echo   - models/screening/overnight_pipeline.py (FinBERT integration)
echo   - sentiment_integration.py (NEW - Core logic)
echo   - paper_trading_coordinator.py (Sentiment gates)
echo   - unified_trading_dashboard.py (FinBERT panel)
echo   - test_finbert_integration.py (Testing suite)
echo.
echo ================================================================================
echo                              Next Steps
echo ================================================================================
echo.
echo 1. Run test suite (if you haven't already):
echo    cd %INSTALL_DIR%
echo    python test_finbert_integration.py
echo.
echo 2. Run overnight pipeline to generate morning report:
echo    python run_au_pipeline.py --full-scan --capital 100000
echo.
echo 3. Start unified trading dashboard:
echo    python unified_trading_dashboard.py
echo.
echo 4. Navigate to: http://localhost:8050
echo.
echo 5. Verify FinBERT sentiment panel appears
echo.
echo ================================================================================
echo                      What This Patch Does
echo ================================================================================
echo.
echo BEFORE: 65%% Negative sentiment - Platform still trades (WRONG!)
echo.
echo AFTER:  65%% Negative sentiment - BLOCK gate - NO TRADES (CORRECT!)
echo.
echo Trading Gates:
echo   - BLOCK (0.0x):   Negative over 50%% - NO TRADES
echo   - REDUCE (0.5x):  Negative 40-50%% - Half-size positions
echo   - CAUTION (0.8x): Neutral 30-40%% - Smaller positions
echo   - ALLOW (1.0x):   Normal trading
echo   - ALLOW (1.2x):   Positive over 60%% - Boosted positions
echo.
echo Dashboard shows:
echo   - FinBERT sentiment breakdown (Negative/Neutral/Positive)
echo   - Trading gate status (Color-coded: Red=BLOCK, Green=ALLOW)
echo   - Reason for gate decision
echo.
echo ================================================================================
echo.
pause
exit /b 0

REM ==============================================================================
REM Error Handler
REM ==============================================================================

:install_error
echo.
echo ================================================================================
echo                        Installation Failed!
echo ================================================================================
echo.
echo An error occurred during installation.
echo.
echo Rollback to backup:
echo   cd %INSTALL_DIR%
echo   xcopy /E /Y "%BACKUP_DIR%\*" .
echo.
echo Or restore manually from: %BACKUP_DIR%
echo.
pause
exit /b 1
