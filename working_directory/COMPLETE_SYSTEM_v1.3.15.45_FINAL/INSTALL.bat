@echo off
REM ==============================================================================
REM COMPLETE SYSTEM v1.3.15.45 FINAL - Clean Installation
REM ==============================================================================

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo          COMPLETE REGIME TRADING SYSTEM v1.3.15.45 FINAL
echo                    Clean Installation Script
echo ================================================================================
echo.

REM Check Python
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo   - Python %PYTHON_VER% found
echo.

REM Create virtual environment
echo [2/8] Creating virtual environment...
if exist "venv" (
    echo   - Virtual environment already exists
    set /p RECREATE="   Recreate? (Y/N): "
    if /i "!RECREATE!"=="Y" (
        echo   - Removing old venv...
        rmdir /S /Q venv
        python -m venv venv
        echo   - New venv created
    )
) else (
    python -m venv venv
    echo   - Virtual environment created
)
echo.

REM Activate venv
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo   - Virtual environment activated
echo.

REM Upgrade pip
echo [4/8] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo   - pip upgraded
echo.

REM Install PyTorch (CPU version - compatible)
echo [5/8] Installing PyTorch (CPU version)...
echo   - This ensures compatibility and avoids DLL conflicts
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo   - WARNING: CPU version failed, trying default
    python -m pip install torch torchvision
)
echo   - PyTorch installed
echo.

REM Install other dependencies
echo [6/8] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo   - All dependencies installed
echo.

REM Download FinBERT model
echo [7/8] Downloading FinBERT model...
echo   - This may take 2-5 minutes (~500MB download)
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; print('  - Downloading tokenizer...'); AutoTokenizer.from_pretrained('ProsusAI/finbert'); print('  - Downloading model...'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('  - FinBERT model ready')"
if errorlevel 1 (
    echo.
    echo   WARNING: FinBERT download encountered an issue
    echo   The model will download automatically on first use
    echo.
    timeout /t 3
) else (
    echo   - FinBERT model cached successfully
)
echo.

REM Clear cache
echo [8/8] Clearing Python cache...
del /S /Q __pycache__\*.pyc 2>nul
del /S /Q models\screening\__pycache__\*.pyc 2>nul
echo   - Cache cleared
echo.

REM Installation complete
echo.
echo ================================================================================
echo                      INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo Virtual environment: venv\
echo Python version: %PYTHON_VER%
echo.
echo ================================================================================
echo                           QUICK START
echo ================================================================================
echo.
echo 1. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Run AU overnight pipeline:
echo    python run_au_pipeline_v1.3.13.py --full-scan --capital 100000
echo.
echo 3. Start trading dashboard:
echo    python unified_trading_dashboard.py
echo.
echo 4. Open browser to:
echo    http://localhost:8050
echo.
echo ================================================================================
echo                         IMPORTANT NOTES
echo ================================================================================
echo.
echo - ALWAYS activate virtual environment before running scripts
echo - Your prompt will show (venv) when activated
echo - To deactivate: type 'deactivate'
echo.
echo Features:
echo   - FinBERT v4.4.4 sentiment analysis
echo   - Trading gates (BLOCK/REDUCE/CAUTION/ALLOW)
echo   - Unified dashboard with sentiment panel
echo   - Multi-market support (AU/US/UK)
echo   - Paper trading coordinator
echo.
echo ================================================================================
echo.
echo Installation complete! Press any key to exit...
pause >nul
