@echo off
cls
color 0A
echo ============================================================
echo    Stock Tracker V8 Professional - Windows 11 Installation
echo    REAL ML Implementation - No Simulated Data
echo ============================================================
echo.
echo Starting installation process...
echo.

:: Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo Python found!
echo.

:: Create virtual environment
echo [2/6] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)
echo.

:: Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.

:: Upgrade pip
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo Pip upgraded!
echo.

:: Install requirements
echo [5/6] Installing required packages...
echo This may take a few minutes...
pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo.
    echo Installing core packages only (some features may be limited)...
    pip install fastapi uvicorn yfinance pandas numpy scikit-learn joblib --quiet
)
echo Packages installed!
echo.

:: Create necessary directories
echo [6/6] Creating directory structure...
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "saved_models" mkdir saved_models
echo Directories created!
echo.

:: Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Stock Tracker V8.lnk'); $SC.TargetPath = '%CD%\START_TRACKER.bat'; $SC.IconLocation = '%SystemRoot%\System32\shell32.dll, 13'; $SC.Save()"
echo Desktop shortcut created!
echo.

color 0A
echo ============================================================
echo    Installation Complete!
echo ============================================================
echo.
echo To start Stock Tracker:
echo   1. Double-click "START_TRACKER.bat" or
echo   2. Use the desktop shortcut "Stock Tracker V8"
echo.
echo Features:
echo   - REAL Machine Learning (10-60s training time)
echo   - NO simulated or fake data
echo   - FinBERT sentiment analysis
echo   - 15+ Global market indices tracking
echo   - Backtesting with $100k capital
echo   - SQLite cached historical data
echo.
echo Press any key to exit...
pause >nul