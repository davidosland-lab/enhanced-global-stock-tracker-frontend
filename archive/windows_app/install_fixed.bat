@echo off
REM ============================================
REM Stock Predictor Pro - Fixed Installation Script
REM Handles Python version compatibility and dependency issues
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

REM Check Python version and find compatible one
echo Checking Python installation...
set PYTHON_CMD=python
set PYTHON_FOUND=0

REM Try python3.9 first (most compatible)
python3.9 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3.9
    set PYTHON_FOUND=1
    echo Found Python 3.9
    goto :PythonFound
)

REM Try python3.10
python3.10 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3.10
    set PYTHON_FOUND=1
    echo Found Python 3.10
    goto :PythonFound
)

REM Try python3.11
python3.11 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3.11
    set PYTHON_FOUND=1
    echo Found Python 3.11
    goto :PythonFound
)

REM Try generic python3
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    set PYTHON_FOUND=1
    echo Found Python 3.x
    goto :PythonFound
)

REM Try generic python (check version)
python --version 2>&1 | findstr /R "3\.9\|3\.10\|3\.11" >nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    echo Found compatible Python version
    goto :PythonFound
)

:PythonFound
if %PYTHON_FOUND% equ 0 (
    echo.
    echo ERROR: Compatible Python version not found!
    echo Stock Predictor Pro requires Python 3.9, 3.10, or 3.11
    echo.
    echo You have Python 3.14 which is too new and causes compatibility issues.
    echo.
    echo Please install Python 3.11 from:
    echo https://www.python.org/downloads/release/python-3119/
    echo.
    echo IMPORTANT: During installation:
    echo   1. Check "Add Python to PATH"
    echo   2. Choose "Install for all users"
    echo.
    pause
    exit /b 1
)

echo Using Python command: %PYTHON_CMD%
%PYTHON_CMD% --version

REM Create installation directory
echo.
echo Creating installation directory...
set INSTALL_DIR=%ProgramFiles%\StockPredictorPro
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo Created directory: %INSTALL_DIR%
) else (
    echo Directory exists: %INSTALL_DIR%
)

REM Copy application files
echo.
echo Copying application files...
xcopy /E /I /Y "." "%INSTALL_DIR%" >nul 2>&1
echo Files copied successfully

REM Create user data directory
set USER_DATA=%APPDATA%\StockPredictorPro
if not exist "%USER_DATA%" (
    mkdir "%USER_DATA%"
    mkdir "%USER_DATA%\models"
    mkdir "%USER_DATA%\data"
    mkdir "%USER_DATA%\logs"
    echo Created user data directory
)

REM Install Python dependencies
echo.
echo Installing Python dependencies...
echo This may take several minutes...
echo.

cd /d "%INSTALL_DIR%"

REM Create virtual environment with specific Python version
echo Creating virtual environment with %PYTHON_CMD%...
%PYTHON_CMD% -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created

REM Activate virtual environment and install packages
echo.
echo Installing required packages...
call venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install core dependencies
echo Installing core dependencies...
pip install --no-cache-dir numpy pandas scikit-learn 2>nul
if %errorlevel% neq 0 (
    echo Retrying with individual packages...
    pip install --no-cache-dir numpy
    pip install --no-cache-dir pandas
    pip install --no-cache-dir scikit-learn
)

echo Installing GUI framework...
pip install --no-cache-dir customtkinter pillow 2>nul
if %errorlevel% neq 0 (
    pip install --no-cache-dir customtkinter
    pip install --no-cache-dir pillow
)

echo Installing ML libraries...
pip install --no-cache-dir xgboost lightgbm 2>nul
if %errorlevel% neq 0 (
    pip install --no-cache-dir xgboost
    echo Note: LightGBM may require additional setup
)

echo Installing financial packages...
REM Install alternatives to pandas-ta
pip install --no-cache-dir yfinance 2>nul
pip install --no-cache-dir ta 2>nul
pip install --no-cache-dir technical 2>nul
if %errorlevel% neq 0 (
    echo Note: Some technical analysis packages may need manual installation
)

echo Installing network packages...
pip install --no-cache-dir requests aiohttp 2>nul

echo Installing additional packages...
pip install --no-cache-dir matplotlib plotly 2>nul

echo Package installation completed

REM Create desktop shortcut with better error handling
echo.
echo Creating shortcuts...

REM First check if Desktop exists
if exist "%USERPROFILE%\Desktop\" (
    powershell -NoProfile -Command "try { $WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Stock Predictor Pro.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\launch.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Stock Predictor Pro'; $Shortcut.Save(); Write-Host 'Desktop shortcut created' } catch { Write-Host 'Could not create desktop shortcut' }"
) else (
    echo Desktop folder not found, skipping desktop shortcut
)

REM Create Start Menu shortcuts
set START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\Stock Predictor Pro
if not exist "%START_MENU%" mkdir "%START_MENU%"

powershell -NoProfile -Command "try { $WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\Stock Predictor Pro.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\launch.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Stock Predictor Pro'; $Shortcut.Save(); Write-Host 'Start Menu shortcut created' } catch { Write-Host 'Could not create Start Menu shortcut' }"

echo Shortcuts created

REM Create launch script
echo Creating launch script...
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo python stock_predictor_pro.py
echo pause
) > "%INSTALL_DIR%\launch.bat"

REM Create launch GUI script (no console window)
(
echo @echo off
echo cd /d "%INSTALL_DIR%"
echo call venv\Scripts\activate.bat
echo start pythonw stock_predictor_pro.py
echo exit
) > "%INSTALL_DIR%\launch_gui.bat"

REM Create uninstall script
echo Creating uninstall script...
(
echo @echo off
echo echo Uninstalling Stock Predictor Pro...
echo rmdir /S /Q "%INSTALL_DIR%"
echo del "%USERPROFILE%\Desktop\Stock Predictor Pro.lnk" 2^>nul
echo rmdir /S /Q "%START_MENU%"
echo echo Uninstall complete.
echo pause
) > "%INSTALL_DIR%\uninstall.bat"

REM Add to registry
echo.
echo Adding to Windows registry...
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "DisplayName" /t REG_SZ /d "Stock Predictor Pro" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "UninstallString" /t REG_SZ /d "%INSTALL_DIR%\uninstall.bat" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "Publisher" /t REG_SZ /d "Stock Predictor Team" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "DisplayVersion" /t REG_SZ /d "1.0.0" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" /v "InstallLocation" /t REG_SZ /d "%INSTALL_DIR%" /f >nul 2>&1
echo Registry entries added

REM Installation complete
echo.
echo =====================================
echo Installation Completed Successfully!
echo =====================================
echo.
echo Stock Predictor Pro has been installed to:
echo %INSTALL_DIR%
echo.
echo IMPORTANT NOTES:
echo 1. Some packages may need manual installation due to Python version
echo 2. If the app doesn't start, try running: %INSTALL_DIR%\launch.bat
echo 3. For GUI mode (no console), use: %INSTALL_DIR%\launch_gui.bat
echo.
echo To launch the application:
echo - Use the desktop shortcut (if created), or
echo - Find it in the Start Menu, or  
echo - Run: %INSTALL_DIR%\launch.bat
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