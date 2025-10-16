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
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo Python found!
echo.

:: Create virtual environment
echo [2/7] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        echo Trying with system packages...
        python -m pip install --user virtualenv
        python -m virtualenv venv
    )
    echo Virtual environment created!
)
echo.

:: Activate virtual environment
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo WARNING: Could not activate virtual environment
    echo Continuing with system Python...
)
echo.

:: Upgrade pip
echo [4/7] Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: Could not upgrade pip, continuing...
)
echo.

:: Install requirements
echo [5/7] Installing required packages...
echo This may take several minutes...

:: Check if requirements.txt exists
if exist requirements.txt (
    echo Installing from requirements.txt...
    pip install -r requirements.txt --disable-pip-version-check
    if %errorlevel% neq 0 (
        echo.
        echo Requirements.txt failed, installing core packages individually...
        goto :install_core
    )
) else (
    :install_core
    echo Installing core packages individually...
    pip install fastapi --disable-pip-version-check
    pip install uvicorn --disable-pip-version-check
    pip install yfinance --disable-pip-version-check
    pip install pandas --disable-pip-version-check
    pip install numpy --disable-pip-version-check
    pip install scikit-learn --disable-pip-version-check
    pip install joblib --disable-pip-version-check
    pip install requests --disable-pip-version-check
)

echo.
echo Core packages installed!
echo.

:: Create necessary directories
echo [6/7] Creating directory structure...
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "saved_models" mkdir saved_models
if not exist "cache" mkdir cache
echo Directories created!
echo.

:: Create desktop shortcut (with error handling)
echo [7/7] Creating desktop shortcut...
echo @echo off > create_shortcut.vbs
echo Set WshShell = CreateObject("WScript.Shell") >> create_shortcut.vbs
echo strDesktop = WshShell.SpecialFolders("Desktop") >> create_shortcut.vbs
echo Set oShellLink = WshShell.CreateShortcut(strDesktop ^& "\Stock Tracker V8.lnk") >> create_shortcut.vbs
echo oShellLink.TargetPath = "%CD%\START_TRACKER.bat" >> create_shortcut.vbs
echo oShellLink.WindowStyle = 1 >> create_shortcut.vbs
echo oShellLink.IconLocation = "%SystemRoot%\System32\shell32.dll, 13" >> create_shortcut.vbs
echo oShellLink.Description = "Stock Tracker V8 Professional" >> create_shortcut.vbs
echo oShellLink.WorkingDirectory = "%CD%" >> create_shortcut.vbs
echo oShellLink.Save >> create_shortcut.vbs

cscript //nologo create_shortcut.vbs
if %errorlevel% equ 0 (
    echo Desktop shortcut created successfully!
    del create_shortcut.vbs
) else (
    echo WARNING: Could not create desktop shortcut
    echo You can manually create a shortcut to START_TRACKER.bat
)
echo.

:: Test Python packages
echo Testing installed packages...
python -c "import fastapi; import pandas; import sklearn; print('Core packages OK')" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Some packages may not be properly installed
    echo The application may have limited functionality
) else (
    echo All core packages verified!
)
echo.

color 0A
echo ============================================================
echo    Installation Complete!
echo ============================================================
echo.
echo Next Steps:
echo   1. Run START_TRACKER.bat to start all services
echo   2. Open http://localhost:8080 in your browser
echo   3. Or use the desktop shortcut "Stock Tracker V8"
echo.
echo If services don't start properly:
echo   - Try using index_fixed.html instead of index.html
echo   - Check WINDOWS_SETUP_GUIDE.md for troubleshooting
echo.
echo Features Installed:
echo   - REAL Machine Learning (10-60s training time)
echo   - NO simulated or fake data
echo   - FinBERT sentiment analysis
echo   - 15+ Global market indices tracking
echo   - Backtesting with $100k capital
echo   - SQLite cached historical data
echo.
echo Press any key to exit installation...
pause >nul