@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM   PHASE 3 TRADING SYSTEM - WINDOWS PATCH
REM   Fixes all known issues for Windows deployment
REM ============================================================================
REM
REM   This patch fixes:
REM   1. Logger not defined error in cba_enhanced_prediction_system.py
REM   2. Dash API compatibility (app.run_server -> app.run)
REM   3. .env encoding error (adds load_dotenv=False)
REM   4. Creates missing START_DASHBOARD.bat file
REM   5. Creates logs/, state/, config/ directories
REM   6. Verifies all critical files exist
REM
REM   Version: 1.3.2 FINAL - WINDOWS COMPATIBLE
REM   Date: December 29, 2024
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   PHASE 3 TRADING SYSTEM - WINDOWS PATCH
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   This patch will fix all known Windows compatibility issues:
echo   • Logger initialization error
echo   • Dash API compatibility
echo   • Missing batch files
echo   • Directory structure
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

echo [1/6] Checking current directory...
echo      Working directory: %CD%
echo.

REM ============================================================================
REM FIX 1: Logger initialization in cba_enhanced_prediction_system.py
REM ============================================================================
echo [2/6] Fixing logger initialization error...

set "CBA_FILE=ml_pipeline\cba_enhanced_prediction_system.py"

if not exist "%CBA_FILE%" (
    echo      [WARNING] File not found: %CBA_FILE%
    echo      Skipping logger fix.
) else (
    echo      Checking for logger error...
    
    REM Check if file has the logger error
    findstr /C:"logger.warning(\"Central bank rate integration not available" "%CBA_FILE%" >nul 2>&1
    if errorlevel 1 (
        echo      [OK] Logger already fixed or not needed.
    ) else (
        echo      [FIXING] Applying logger fix...
        
        REM Create backup
        copy "%CBA_FILE%" "%CBA_FILE%.backup" >nul 2>&1
        echo      Created backup: %CBA_FILE%.backup
        
        REM Use PowerShell to fix the logger issue
        powershell -Command "$content = Get-Content '%CBA_FILE%' -Raw; if ($content -match 'import warnings\r?\nwarnings.filterwarnings' -and $content -notmatch 'logger = logging.getLogger') { $content = $content -replace '(import warnings\r?\nwarnings\.filterwarnings\(''ignore''\)\r?\n)', '$1`r`n# Configure logging BEFORE using it`r`nlogger = logging.getLogger(__name__)`r`n`r`n'; $content = $content -replace '# Configure logging\r?\nlogging\.basicConfig\(level=logging\.INFO\)\r?\nlogger = logging\.getLogger\(__name__\)\r?\n', ''; Set-Content '%CBA_FILE%' $content -NoNewline; Write-Host '      Applied logger fix successfully.' } else { Write-Host '      Logger already properly initialized.' }"
    )
)
echo.

REM ============================================================================
REM FIX 2: Dash API compatibility in dashboard.py
REM ============================================================================
echo [3/6] Fixing Dash API compatibility...

set "DASHBOARD_FILE=phase3_intraday_deployment\dashboard.py"

if not exist "%DASHBOARD_FILE%" (
    echo      [WARNING] File not found: %DASHBOARD_FILE%
    echo      Skipping Dash fix.
) else (
    echo      Checking Dash API version...
    
    REM Check if file uses old API
    findstr /C:"app.run_server" "%DASHBOARD_FILE%" >nul 2>&1
    if errorlevel 1 (
        echo      [OK] Dash API already updated.
    ) else (
        echo      [FIXING] Updating Dash API...
        
        REM Create backup
        copy "%DASHBOARD_FILE%" "%DASHBOARD_FILE%.backup" >nul 2>&1
        echo      Created backup: %DASHBOARD_FILE%.backup
        
        REM Replace app.run_server with app.run
        powershell -Command "(Get-Content '%DASHBOARD_FILE%') -replace 'app\.run_server\(', 'app.run(' | Set-Content '%DASHBOARD_FILE%'"
        echo      Updated app.run_server to app.run
    )
    
    REM Check if load_dotenv fix is needed
    findstr /C:"load_dotenv=False" "%DASHBOARD_FILE%" >nul 2>&1
    if errorlevel 1 (
        echo      [FIXING] Adding load_dotenv=False parameter...
        
        REM Add load_dotenv=False to prevent .env encoding errors
        powershell -Command "$content = Get-Content '%DASHBOARD_FILE%' -Raw; if ($content -match 'app\.run\(\s*debug=False,\s*host=''0\.0\.0\.0'',\s*port=8050\s*\)') { $content = $content -replace '(app\.run\(\s*debug=False,\s*host=''0\.0\.0\.0'',\s*port=8050)\s*\)', '$1,`r`n        load_dotenv=False`r`n    )'; Set-Content '%DASHBOARD_FILE%' $content -NoNewline; Write-Host '      Added load_dotenv=False parameter' }"
    ) else (
        echo      [OK] load_dotenv=False already present.
    )
)
echo.

REM ============================================================================
REM FIX 3: Create START_DASHBOARD.bat
REM ============================================================================
echo [4/6] Creating START_DASHBOARD.bat...

set "DASHBOARD_BAT=phase3_intraday_deployment\START_DASHBOARD.bat"

if exist "%DASHBOARD_BAT%" (
    echo      [OK] START_DASHBOARD.bat already exists.
) else (
    echo      [CREATING] START_DASHBOARD.bat...
    
    (
        echo @echo off
        echo echo ════════════════════════════════════════════════════════════
        echo echo   Phase 3 Paper Trading Dashboard
        echo echo ════════════════════════════════════════════════════════════
        echo echo.
        echo echo Starting dashboard server...
        echo echo.
        echo echo ┌──────────────────────────────────────────────────────────┐
        echo echo │  Open your browser to: http://localhost:8050             │
        echo echo └──────────────────────────────────────────────────────────┘
        echo echo.
        echo echo Dashboard Features:
        echo echo   • Live portfolio value and P/L
        echo echo   • Open positions with real-time updates
        echo echo   • Intraday alerts feed
        echo echo   • Performance metrics
        echo echo   • Trade history
        echo echo   • Market sentiment gauge
        echo echo   • Auto-refreshes every 5 seconds
        echo echo.
        echo echo Press Ctrl+C to stop the dashboard
        echo echo ════════════════════════════════════════════════════════════
        echo echo.
        echo.
        echo REM Change to script directory
        echo cd /d "%%~dp0"
        echo.
        echo REM Check if dash is installed
        echo python -c "import dash" 2^>nul
        echo if errorlevel 1 ^(
        echo     echo [WARNING] Dash not installed. Installing now...
        echo     pip install dash plotly
        echo     echo.
        echo ^)
        echo.
        echo REM Start dashboard
        echo echo Starting dashboard...
        echo python dashboard.py
        echo.
        echo echo.
        echo echo Dashboard stopped.
        echo pause
    ) > "%DASHBOARD_BAT%"
    
    echo      Created: %DASHBOARD_BAT%
)
echo.

REM ============================================================================
REM FIX 4: Create required directories
REM ============================================================================
echo [5/6] Creating required directories...

set "DIRS=logs state config phase3_intraday_deployment\logs phase3_intraday_deployment\state phase3_intraday_deployment\config"

for %%D in (%DIRS%) do (
    if not exist "%%D" (
        mkdir "%%D" 2>nul
        if exist "%%D" (
            echo      Created: %%D\
        ) else (
            echo      [WARNING] Could not create: %%D\
        )
    ) else (
        echo      [OK] Directory exists: %%D\
    )
)
echo.

REM ============================================================================
REM FIX 5: Verify installation
REM ============================================================================
echo [6/6] Verifying installation...
echo.

set "ERROR_COUNT=0"

REM Check critical files
echo      Checking critical files...

set "CRITICAL_FILES=ml_pipeline\__init__.py ml_pipeline\swing_signal_generator.py phase3_intraday_deployment\paper_trading_coordinator.py phase3_intraday_deployment\dashboard.py test_ml_stack.py"

for %%F in (%CRITICAL_FILES%) do (
    if exist "%%F" (
        echo      ✓ %%F
    ) else (
        echo      ✗ %%F [MISSING]
        set /a ERROR_COUNT+=1
    )
)
echo.

REM Check Python packages
echo      Checking Python packages...

set "PACKAGES=pandas numpy yfinance yahooquery torch keras sklearn xgboost lightgbm catboost dash plotly"

for %%P in (%PACKAGES%) do (
    python -c "import %%P" 2>nul
    if errorlevel 1 (
        echo      ✗ %%P [NOT INSTALLED]
        set /a ERROR_COUNT+=1
    ) else (
        echo      ✓ %%P
    )
)
echo.

REM ============================================================================
REM Summary
REM ============================================================================
echo ════════════════════════════════════════════════════════════════════════
echo   PATCH COMPLETE
echo ════════════════════════════════════════════════════════════════════════
echo.

if %ERROR_COUNT% GTR 0 (
    echo   Status: COMPLETED WITH WARNINGS
    echo   Warnings: %ERROR_COUNT% issue^(s^) found
    echo.
    echo   Please review the warnings above and install missing packages:
    echo   pip install -r phase3_intraday_deployment\requirements.txt
    echo   pip install torch keras optree absl-py h5py ml-dtypes namex
    echo   pip install transformers sentencepiece xgboost lightgbm catboost
    echo   pip install dash plotly
) else (
    echo   Status: ✅ SUCCESS - All fixes applied!
    echo.
    echo   Your system is now ready to use!
)
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

REM ============================================================================
REM Next steps
REM ============================================================================
echo NEXT STEPS:
echo.
echo 1. Test ML Stack:
echo    python test_ml_stack.py
echo.
echo 2. Start Paper Trading:
echo    cd phase3_intraday_deployment
echo    python paper_trading_coordinator.py --symbols RIO.AX,CBA.AX,BHP.AX --capital 100000 --real-signals
echo.
echo 3. Start Dashboard ^(in a new terminal^):
echo    cd phase3_intraday_deployment
echo    python dashboard.py
echo    Then open: http://localhost:8050
echo.
echo Or use the batch files:
echo    phase3_intraday_deployment\START_PAPER_TRADING.bat
echo    phase3_intraday_deployment\START_DASHBOARD.bat
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

if %ERROR_COUNT% GTR 0 (
    echo Press any key to view installation instructions...
    pause >nul
    echo.
    echo INSTALLATION INSTRUCTIONS:
    echo.
    echo If packages are missing, run these commands:
    echo.
    echo pip install --upgrade pip
    echo pip install -r phase3_intraday_deployment\requirements.txt
    echo pip install torch --index-url https://download.pytorch.org/whl/cpu
    echo pip install keras optree absl-py h5py ml-dtypes namex
    echo pip install transformers sentencepiece
    echo pip install xgboost lightgbm catboost scikit-learn
    echo pip install dash plotly
    echo.
)

echo Press any key to exit...
pause >nul
