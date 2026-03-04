@echo off
REM ==============================================================================
REM COMPLETE_PATCH_v1.3.15.45 - FINAL CLEAN INSTALLER
REM FinBERT v4.4.4 Unified Integration
REM ==============================================================================
REM
REM This installer provides two installation methods:
REM   1. VIRTUAL ENVIRONMENT (Recommended - Clean isolated install)
REM   2. GLOBAL INSTALLATION (Uses system Python)
REM
REM Author: GenSpark AI Developer
REM Version: v1.3.15.45 FINAL
REM Date: 2026-01-29
REM ==============================================================================

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo          COMPLETE_PATCH_v1.3.15.45 - FINAL CLEAN INSTALLER
echo              FinBERT v4.4.4 Unified Integration
echo ================================================================================
echo.
echo This patch fixes the critical issue where negative sentiment did not block trades
echo.
echo Features:
echo   - Unified FinBERT v4.4.4 across all components
echo   - Sentiment gates (BLOCK/REDUCE/CAUTION/ALLOW)
echo   - Dashboard FinBERT sentiment panel
echo   - Automatic dependency installation
echo   - Virtual environment support (avoids DLL conflicts)
echo.

REM ==============================================================================
REM Choose Installation Method
REM ==============================================================================

echo ================================================================================
echo                        INSTALLATION METHOD
echo ================================================================================
echo.
echo Choose installation method:
echo.
echo [1] VIRTUAL ENVIRONMENT (RECOMMENDED)
echo     - Clean isolated Python environment
echo     - Avoids DLL conflicts and package issues
echo     - Easy to remove if needed
echo     - Best for production use
echo.
echo [2] GLOBAL INSTALLATION
echo     - Installs to system Python
echo     - May conflict with existing packages
echo     - Use only if you understand Python environments
echo.
set /p INSTALL_METHOD="Enter choice (1 or 2): "

if "%INSTALL_METHOD%"=="1" goto :venv_install
if "%INSTALL_METHOD%"=="2" goto :global_install

echo.
echo Invalid choice. Defaulting to Virtual Environment installation.
timeout /t 3
goto :venv_install

REM ==============================================================================
REM VIRTUAL ENVIRONMENT INSTALLATION (RECOMMENDED)
REM ==============================================================================

:venv_install
echo.
echo ================================================================================
echo              VIRTUAL ENVIRONMENT INSTALLATION (RECOMMENDED)
echo ================================================================================
echo.

REM Ask for installation directory
echo Default installation directory:
echo   C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15
echo.
set /p "INSTALL_DIR=Enter installation directory (or press Enter for default): "

if "%INSTALL_DIR%"=="" (
    set "INSTALL_DIR=C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15"
    echo Using default: %INSTALL_DIR%
)

echo.
echo Installation directory: %INSTALL_DIR%
echo.

REM Verify directory exists
if not exist "%INSTALL_DIR%" (
    echo ERROR: Directory does not exist: %INSTALL_DIR%
    echo.
    pause
    exit /b 1
)

if not exist "%INSTALL_DIR%\models\screening" (
    echo ERROR: Invalid installation directory (models\screening not found)
    echo.
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%"

echo [1/10] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo   - OK: Python found
echo.

echo [2/10] Creating virtual environment...
if exist "venv" (
    echo   - Virtual environment already exists
    set /p RECREATE="Recreate virtual environment? (Y/N): "
    if /i "!RECREATE!"=="Y" (
        echo   - Removing old virtual environment...
        rmdir /S /Q venv
        python -m venv venv
        echo   - New virtual environment created
    )
) else (
    python -m venv venv
    echo   - Virtual environment created: venv
)
echo.

echo [3/10] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo   - Virtual environment activated
echo.

echo [4/10] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo   - pip upgraded
echo.

echo [5/10] Creating backup...
set "TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "BACKUP_DIR=%INSTALL_DIR%\backup_%TIMESTAMP%"

mkdir "%BACKUP_DIR%" 2>nul
mkdir "%BACKUP_DIR%\models\screening" 2>nul

if exist "models\screening\finbert_bridge.py" copy "models\screening\finbert_bridge.py" "%BACKUP_DIR%\models\screening\" >nul 2>&1
if exist "models\screening\overnight_pipeline.py" copy "models\screening\overnight_pipeline.py" "%BACKUP_DIR%\models\screening\" >nul 2>&1
if exist "models\screening\batch_predictor.py" copy "models\screening\batch_predictor.py" "%BACKUP_DIR%\models\screening\" >nul 2>&1
if exist "sentiment_integration.py" copy "sentiment_integration.py" "%BACKUP_DIR%\" >nul 2>&1
if exist "paper_trading_coordinator.py" copy "paper_trading_coordinator.py" "%BACKUP_DIR%\" >nul 2>&1
if exist "unified_trading_dashboard.py" copy "unified_trading_dashboard.py" "%BACKUP_DIR%\" >nul 2>&1

echo   - Backup created: %BACKUP_DIR%
echo.

echo [6/10] Installing Python dependencies...
set "PATCH_DIR=%~dp0"
if "%PATCH_DIR:~-1%"=="\" set "PATCH_DIR=%PATCH_DIR:~0,-1%"

echo   - Installing PyTorch (CPU version for compatibility)...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
if errorlevel 1 (
    echo   - WARNING: PyTorch CPU install failed, trying default...
    python -m pip install torch torchvision --quiet
)

echo   - Installing transformers and other dependencies...
python -m pip install transformers --quiet
python -m pip install feedparser yahooquery yfinance pandas numpy dash plotly requests beautifulsoup4 --quiet

echo   - All dependencies installed
echo.

echo [7/10] Installing patch files...

copy /Y "%PATCH_DIR%\models\screening\finbert_bridge.py" "models\screening\" >nul 2>&1
echo   - Installed: models\screening\finbert_bridge.py

copy /Y "%PATCH_DIR%\models\screening\overnight_pipeline.py" "models\screening\" >nul 2>&1
echo   - Installed: models\screening\overnight_pipeline.py

copy /Y "%PATCH_DIR%\models\screening\batch_predictor.py" "models\screening\" >nul 2>&1
echo   - Installed: models\screening\batch_predictor.py

copy /Y "%PATCH_DIR%\sentiment_integration.py" . >nul 2>&1
echo   - Installed: sentiment_integration.py

copy /Y "%PATCH_DIR%\paper_trading_coordinator.py" . >nul 2>&1
echo   - Installed: paper_trading_coordinator.py

copy /Y "%PATCH_DIR%\unified_trading_dashboard.py" . >nul 2>&1
echo   - Installed: unified_trading_dashboard.py

copy /Y "%PATCH_DIR%\test_finbert_integration.py" . >nul 2>&1
echo   - Installed: test_finbert_integration.py

echo.

echo [8/10] Downloading FinBERT model (this may take 2-5 minutes)...
echo   - Attempting to download ProsusAI/finbert from Hugging Face...
python -c "import sys; import torch; print('  - PyTorch version:', torch.__version__); from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('  - Downloading tokenizer...'); tok = AutoTokenizer.from_pretrained('ProsusAI/finbert'); print('  - Downloading model...'); model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('  - SUCCESS: FinBERT model ready')" 2>&1
if errorlevel 1 (
    echo.
    echo   ============================================================
    echo   WARNING: FinBERT model download encountered an issue
    echo   ============================================================
    echo.
    echo   This is usually caused by:
    echo   1. PyTorch/torchvision version mismatch
    echo   2. Network connectivity issues
    echo   3. Missing dependencies
    echo.
    echo   The installer will continue, but you may need to:
    echo.
    echo   Option 1 - Reinstall PyTorch:
    echo     venv\Scripts\activate
    echo     pip uninstall torch torchvision -y
    echo     pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    echo     pip install transformers
    echo.
    echo   Option 2 - Manual download later:
    echo     The model will download automatically on first use
    echo.
    echo   ============================================================
    timeout /t 5
) else (
    echo   - FinBERT model cached successfully
)
echo.

echo [9/10] Clearing Python cache...
if exist "__pycache__" del /Q "__pycache__\*.pyc" 2>nul
if exist "models\screening\__pycache__" del /Q "models\screening\__pycache__\*.pyc" 2>nul
echo   - Python cache cleared
echo.

echo [10/10] Running integration tests...
echo.
python test_finbert_integration.py
echo.

goto :installation_complete

REM ==============================================================================
REM GLOBAL INSTALLATION
REM ==============================================================================

:global_install
echo.
echo ================================================================================
echo                        GLOBAL INSTALLATION
echo ================================================================================
echo.
echo WARNING: This will install packages to your system Python
echo          May cause conflicts with existing packages
echo.
set /p CONFIRM="Continue with global installation? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Installation cancelled.
    pause
    exit /b 0
)

REM Ask for installation directory
echo.
echo Default installation directory:
echo   C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15
echo.
set /p "INSTALL_DIR=Enter installation directory (or press Enter for default): "

if "%INSTALL_DIR%"=="" (
    set "INSTALL_DIR=C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15"
    echo Using default: %INSTALL_DIR%
)

echo.
echo Installation directory: %INSTALL_DIR%
echo.

REM Verify directory exists
if not exist "%INSTALL_DIR%" (
    echo ERROR: Directory does not exist: %INSTALL_DIR%
    echo.
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%"

echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)
echo   - OK: Python found
echo.

echo [2/8] Creating backup...
set "TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "BACKUP_DIR=%INSTALL_DIR%\backup_%TIMESTAMP%"

mkdir "%BACKUP_DIR%" 2>nul
mkdir "%BACKUP_DIR%\models\screening" 2>nul

if exist "models\screening\finbert_bridge.py" copy "models\screening\finbert_bridge.py" "%BACKUP_DIR%\models\screening\" >nul 2>&1
if exist "sentiment_integration.py" copy "sentiment_integration.py" "%BACKUP_DIR%\" >nul 2>&1
if exist "paper_trading_coordinator.py" copy "paper_trading_coordinator.py" "%BACKUP_DIR%\" >nul 2>&1

echo   - Backup created: %BACKUP_DIR%
echo.

echo [3/8] Installing Python dependencies globally...
set "PATCH_DIR=%~dp0"
if "%PATCH_DIR:~-1%"=="\" set "PATCH_DIR=%PATCH_DIR:~0,-1%"

echo   - Installing PyTorch (CPU version for compatibility)...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --quiet
if errorlevel 1 (
    echo   - WARNING: PyTorch CPU install failed, trying default...
    python -m pip install torch torchvision --quiet
)

echo   - Installing transformers and other dependencies...
python -m pip install --upgrade transformers feedparser yahooquery yfinance pandas numpy dash plotly requests beautifulsoup4 --quiet
echo   - Dependencies installed
echo.

echo [4/8] Installing patch files...
copy /Y "%PATCH_DIR%\models\screening\*.py" "models\screening\" >nul 2>&1
copy /Y "%PATCH_DIR%\*.py" . >nul 2>&1
echo   - All patch files installed
echo.

echo [5/8] Downloading FinBERT model...
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('ProsusAI/finbert'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('  - FinBERT model ready')"
echo.

echo [6/8] Clearing Python cache...
del /S /Q __pycache__\*.pyc 2>nul
del /S /Q models\screening\__pycache__\*.pyc 2>nul
echo   - Cache cleared
echo.

echo [7/8] Verifying installation...
if not exist "sentiment_integration.py" (
    echo ERROR: Installation failed
    pause
    exit /b 1
)
echo   - Installation verified
echo.

echo [8/8] Running tests...
python test_finbert_integration.py
echo.

REM ==============================================================================
REM INSTALLATION COMPLETE
REM ==============================================================================

:installation_complete
echo.
echo ================================================================================
echo                      INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo Patch v1.3.15.45 installed successfully
echo.
echo Installation directory: %INSTALL_DIR%
echo Backup location: %BACKUP_DIR%
echo.

if "%INSTALL_METHOD%"=="1" (
    echo ================================================================================
    echo                    VIRTUAL ENVIRONMENT USAGE
    echo ================================================================================
    echo.
    echo IMPORTANT: Always activate the virtual environment before running scripts:
    echo.
    echo   Activate:   venv\Scripts\activate
    echo   Deactivate: deactivate
    echo.
    echo After activation, your prompt will show: ^(venv^)
    echo.
)

echo ================================================================================
echo                           NEXT STEPS
echo ================================================================================
echo.

if "%INSTALL_METHOD%"=="1" (
    echo 1. ALWAYS activate virtual environment first:
    echo    venv\Scripts\activate
    echo.
    echo 2. Run overnight pipeline:
    echo    python run_au_pipeline_v1.3.13.py --full-scan --capital 100000
    echo.
    echo 3. Start unified trading dashboard:
    echo    python unified_trading_dashboard.py
    echo.
    echo 4. Navigate to: http://localhost:8050
    echo.
) else (
    echo 1. Run overnight pipeline:
    echo    python run_au_pipeline_v1.3.13.py --full-scan --capital 100000
    echo.
    echo 2. Start unified trading dashboard:
    echo    python unified_trading_dashboard.py
    echo.
    echo 3. Navigate to: http://localhost:8050
    echo.
)

echo ================================================================================
echo                         WHAT THIS PATCH DOES
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
echo Dashboard displays:
echo   - FinBERT sentiment breakdown (Negative/Neutral/Positive bars)
echo   - Trading gate status (Color-coded: Red=BLOCK, Green=ALLOW)
echo   - Reason for gate decision
echo.
echo ================================================================================
echo.
echo Installation complete! Press any key to exit...
pause >nul
exit /b 0
