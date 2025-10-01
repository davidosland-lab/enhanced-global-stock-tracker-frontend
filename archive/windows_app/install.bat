@echo off
REM ============================================
REM Stock Predictor Pro - Installation Script
REM ============================================

echo.
echo =====================================
echo Stock Predictor Pro Installation
echo =====================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires Administrator privileges.
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

REM Check Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%VERSION%" LSS "10.0" (
    echo Error: Stock Predictor Pro requires Windows 10 or Windows 11
    pause
    exit /b 1
)

REM Check for Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.9 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    choice /C YN /M "Open Python download page now?"
    if errorlevel 2 goto SkipPythonDownload
    if errorlevel 1 start https://www.python.org/downloads/
    :SkipPythonDownload
    echo.
    echo After installing Python, please run this installer again.
    pause
    exit /b 1
) else (
    echo ✓ Python is installed
    python --version
)

REM Create installation directory
echo.
echo Creating installation directory...
set INSTALL_DIR=%ProgramFiles%\StockPredictorPro
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo ✓ Created directory: %INSTALL_DIR%
) else (
    echo ✓ Directory exists: %INSTALL_DIR%
)

REM Copy application files
echo.
echo Copying application files...
xcopy /E /I /Y "." "%INSTALL_DIR%" >nul 2>&1
echo ✓ Files copied successfully

REM Create user data directory
set USER_DATA=%APPDATA%\StockPredictorPro
if not exist "%USER_DATA%" (
    mkdir "%USER_DATA%"
    mkdir "%USER_DATA%\models"
    mkdir "%USER_DATA%\data"
    mkdir "%USER_DATA%\logs"
    echo ✓ Created user data directory
)

REM Install Python dependencies
echo.
echo Installing Python dependencies...
echo This may take several minutes...
echo.

cd /d "%INSTALL_DIR%"

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created

REM Activate virtual environment and install packages
echo.
echo Installing required packages...
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip --quiet

REM Install core dependencies first
echo Installing core dependencies...
pip install --no-cache-dir numpy pandas scikit-learn --quiet
if %errorlevel% neq 0 (
    echo Warning: Some core packages failed to install
)

echo Installing GUI framework...
pip install --no-cache-dir customtkinter pillow --quiet
if %errorlevel% neq 0 (
    echo Warning: GUI packages failed to install
)

echo Installing ML libraries...
pip install --no-cache-dir xgboost lightgbm --quiet
if %errorlevel% neq 0 (
    echo Warning: Some ML packages failed to install
)

echo Installing financial packages...
pip install --no-cache-dir yfinance pandas-ta --quiet
if %errorlevel% neq 0 (
    echo Warning: Some financial packages failed to install
)

echo Installing network packages...
pip install --no-cache-dir requests aiohttp --quiet
if %errorlevel% neq 0 (
    echo Warning: Some network packages failed to install
)

echo ✓ Package installation completed

REM Create desktop shortcut
echo.
echo Creating shortcuts...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Stock Predictor Pro.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\launch.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\assets\icon.ico,0'; $Shortcut.Description = 'Stock Predictor Pro - AI Trading System'; $Shortcut.Save()"
echo ✓ Desktop shortcut created

REM Create Start Menu shortcuts
set START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\Stock Predictor Pro
if not exist "%START_MENU%" mkdir "%START_MENU%"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Stock Predictor Pro.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\launch.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\assets\icon.ico,0'; $Shortcut.Description = 'Stock Predictor Pro - AI Trading System'; $Shortcut.Save()"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Uninstall.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\uninstall.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Uninstall Stock Predictor Pro'; $Shortcut.Save()"

echo ✓ Start Menu shortcuts created

REM Create launch script
echo Creating launch script...
echo @echo off > "%INSTALL_DIR%\launch.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\launch.bat"
echo call venv\Scripts\activate.bat >> "%INSTALL_DIR%\launch.bat"
echo start pythonw stock_predictor_pro.py >> "%INSTALL_DIR%\launch.bat"
echo exit >> "%INSTALL_DIR%\launch.bat"

REM Create uninstall script
echo Creating uninstall script...
echo @echo off > "%INSTALL_DIR%\uninstall.bat"
echo echo Uninstalling Stock Predictor Pro... >> "%INSTALL_DIR%\uninstall.bat"
echo rmdir /S /Q "%INSTALL_DIR%" >> "%INSTALL_DIR%\uninstall.bat"
echo del "%USERPROFILE%\Desktop\Stock Predictor Pro.lnk" >> "%INSTALL_DIR%\uninstall.bat"
echo rmdir /S /Q "%START_MENU%" >> "%INSTALL_DIR%\uninstall.bat"
echo echo Uninstall complete. >> "%INSTALL_DIR%\uninstall.bat"
echo pause >> "%INSTALL_DIR%\uninstall.bat"

REM Add to registry for uninstall
echo.
echo Adding to Windows registry...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "DisplayName" /t REG_SZ /d "Stock Predictor Pro" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "UninstallString" /t REG_SZ /d "%INSTALL_DIR%\uninstall.bat" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "DisplayIcon" /t REG_SZ /d "%INSTALL_DIR%\assets\icon.ico" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "Publisher" /t REG_SZ /d "Stock Predictor Team" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "DisplayVersion" /t REG_SZ /d "1.0.0" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
echo ✓ Registry entries added

REM Installation complete
echo.
echo =====================================
echo Installation Completed Successfully!
echo =====================================
echo.
echo Stock Predictor Pro has been installed to:
echo %INSTALL_DIR%
echo.
echo Shortcuts have been created on:
echo - Desktop
echo - Start Menu
echo.
echo To launch the application:
echo 1. Use the desktop shortcut, or
echo 2. Find it in the Start Menu, or
echo 3. Run: %INSTALL_DIR%\launch.bat
echo.

choice /C YN /M "Launch Stock Predictor Pro now?"
if errorlevel 2 goto End
if errorlevel 1 (
    echo.
    echo Launching Stock Predictor Pro...
    start "" "%INSTALL_DIR%\launch.bat"
)

:End
echo.
echo Thank you for installing Stock Predictor Pro!
echo.
pause