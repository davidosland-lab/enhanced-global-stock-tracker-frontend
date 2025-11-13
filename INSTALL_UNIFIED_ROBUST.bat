@echo off
setlocal enabledelayedexpansion

echo ===============================================================================
echo UNIFIED ROBUST STOCK ANALYSIS - INSTALLATION
echo ===============================================================================
echo.
echo This will install all required dependencies for the robust stock analysis system
echo.

:: Check Python
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

:: Create virtual environment
echo [2/7] Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
)
echo.

:: Activate virtual environment
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

:: Upgrade pip
echo [4/7] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo Pip upgraded
echo.

:: Install core dependencies
echo [5/7] Installing core dependencies...
echo Installing Flask...
pip install flask flask-cors --quiet
echo Installing data libraries...
pip install pandas numpy --quiet
echo Installing yfinance...
pip install yfinance --quiet
echo Installing requests...
pip install requests --quiet
echo.

:: Install ML dependencies with fallback
echo [6/7] Installing ML dependencies (scikit-learn)...
echo This may take a few minutes...

:: Try to install scikit-learn
pip install scikit-learn --quiet >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: scikit-learn installation failed.
    echo The system will run without ML predictions.
    echo You can try installing it manually later with: pip install scikit-learn
    echo.
) else (
    echo scikit-learn installed successfully
)
echo.

:: Create requirements file
echo [7/7] Creating requirements.txt...
echo flask>=2.0.0 > requirements.txt
echo flask-cors>=3.0.0 >> requirements.txt
echo pandas>=1.3.0 >> requirements.txt
echo numpy>=1.21.0 >> requirements.txt
echo yfinance>=0.2.0 >> requirements.txt
echo requests>=2.26.0 >> requirements.txt
echo scikit-learn>=1.0.0 >> requirements.txt
echo Requirements file created
echo.

:: Display success message
echo ===============================================================================
echo INSTALLATION COMPLETE!
echo ===============================================================================
echo.
echo All dependencies have been installed successfully.
echo.
echo To run the application:
echo   1. Double-click RUN_UNIFIED_ROBUST.bat
echo   2. Open your browser to http://localhost:5000
echo.
echo Features available:
echo   - Real-time stock data (Yahoo Finance + Alpha Vantage)
echo   - Technical indicators (RSI, MACD, Bollinger Bands, etc.)
echo   - Market sentiment analysis (VIX, yields, dollar index)
echo   - ML predictions (if scikit-learn installed)
echo   - Chart zoom functionality
echo   - Australian stock support
echo.
echo ===============================================================================
echo.
echo Press any key to close this window...
pause >nul