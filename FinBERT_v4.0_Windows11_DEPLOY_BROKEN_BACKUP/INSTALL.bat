@echo off
REM ============================================================================
REM FinBERT v4.0 - Windows 11 Installation Script
REM Parameter Optimization Edition
REM ============================================================================

echo.
echo ========================================================================
echo   FinBERT v4.0 Enhanced - Parameter Optimization Edition
echo   Windows 11 Installation Script
echo ========================================================================
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo.

REM Check Python version
echo [2/6] Verifying Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required!
    echo Your version:
    python --version
    pause
    exit /b 1
)
echo Python version OK
echo.

REM Check pip
echo [3/6] Checking pip installation...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed!
    echo Installing pip...
    python -m ensurepip --upgrade
)
python -m pip --version
echo.

REM Upgrade pip
echo [4/6] Upgrading pip to latest version...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo [5/6] Installing Python dependencies...
echo This may take 5-10 minutes depending on your internet connection...
echo.

if exist requirements-full.txt (
    echo Installing full requirements (recommended)...
    python -m pip install -r requirements-full.txt
) else (
    if exist requirements-minimal.txt (
        echo Installing minimal requirements...
        python -m pip install -r requirements-minimal.txt
    ) else (
        echo ERROR: No requirements file found!
        pause
        exit /b 1
    )
)

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo Please check error messages above and try again.
    pause
    exit /b 1
)

echo.
echo [6/6] Creating necessary directories...
if not exist "models\saved_models" mkdir "models\saved_models"
if not exist "cache" mkdir "cache"
if not exist "logs" mkdir "logs"
echo.

REM Installation complete
echo ========================================================================
echo   Installation Complete!
echo ========================================================================
echo.
echo FinBERT v4.0 Enhanced has been successfully installed.
echo.
echo Next steps:
echo   1. Review README.md for configuration options
echo   2. Run START_PARAMETER_OPTIMIZATION.bat to start the application
echo   3. Open http://localhost:5001 in your browser
echo.
echo IMPORTANT: Use START_PARAMETER_OPTIMIZATION.bat (not START_FINBERT_V4.bat)
echo START_PARAMETER_OPTIMIZATION.bat works without virtual environment
echo.
echo New Features in This Version:
echo   - Parameter Optimization (Grid Search and Random Search)
echo   - Train-Test Split Validation
echo   - Overfitting Detection
echo   - Enhanced Portfolio Backtesting
echo   - Improved Chart Visualizations
echo.
echo ========================================================================
echo.
pause
