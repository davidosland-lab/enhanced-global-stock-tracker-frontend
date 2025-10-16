@echo off
echo ============================================================
echo Stock Tracker V9 - Windows Installation (Fixed)
echo Real ML, Real Data, Real Predictions
echo ============================================================
echo.

REM Check Python installation
echo [Step 1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version

REM Create virtual environment
echo.
echo [Step 2/6] Creating virtual environment...
if exist "venv" (
    echo Removing old virtual environment...
    rmdir /s /q venv
)
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Try: python -m pip install --user virtualenv
    pause
    exit /b 1
)
echo Virtual environment created successfully

REM Activate virtual environment
echo.
echo [Step 3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip and install setuptools first
echo.
echo [Step 4/6] Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo WARNING: Could not upgrade pip/setuptools, continuing anyway...
)

REM Install core requirements one by one to identify issues
echo.
echo [Step 5/6] Installing core requirements...
echo Installing FastAPI framework...
python -m pip install fastapi==0.104.1
if %errorlevel% neq 0 goto :install_error

echo Installing Uvicorn server...
python -m pip install uvicorn==0.24.0
if %errorlevel% neq 0 goto :install_error

echo Installing Pydantic...
python -m pip install pydantic==2.4.2
if %errorlevel% neq 0 goto :install_error

echo Installing pandas for data processing...
python -m pip install pandas==2.1.3
if %errorlevel% neq 0 goto :install_error

echo Installing numpy...
python -m pip install numpy==1.25.2
if %errorlevel% neq 0 goto :install_error

echo Installing yfinance for stock data...
python -m pip install yfinance==0.2.32
if %errorlevel% neq 0 goto :install_error

echo Installing scikit-learn for ML...
python -m pip install scikit-learn==1.3.2
if %errorlevel% neq 0 goto :install_error

echo Installing joblib...
python -m pip install joblib==1.3.2
if %errorlevel% neq 0 goto :install_error

echo Installing technical analysis library...
python -m pip install ta==0.11.0
if %errorlevel% neq 0 (
    echo WARNING: TA library installation failed, continuing without it...
)

echo Installing XGBoost (optional)...
python -m pip install xgboost==2.0.2
if %errorlevel% neq 0 (
    echo WARNING: XGBoost installation failed, will use RandomForest only
)

echo Installing aiohttp for async operations...
python -m pip install aiohttp==3.9.0
if %errorlevel% neq 0 goto :install_error

echo Installing python-multipart for file uploads...
python -m pip install python-multipart==0.0.6
if %errorlevel% neq 0 goto :install_error

REM Optional FinBERT installation
echo.
echo [Step 6/6] Optional: FinBERT Installation
echo ============================================================
echo Do you want to install FinBERT for real sentiment analysis?
echo This requires ~2GB download and may take 5-10 minutes.
echo You can skip this and use keyword-based sentiment instead.
echo ============================================================
choice /C YN /M "Install FinBERT (Y/N)?"
if %errorlevel%==1 (
    echo Installing transformers and torch for FinBERT...
    python -m pip install transformers torch
    if %errorlevel% neq 0 (
        echo WARNING: FinBERT installation failed, will use keyword analysis
    )
) else (
    echo Skipping FinBERT - will use keyword-based sentiment analysis
)

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo All core components installed successfully.
echo.
echo To start the system:
echo   Run START_WINDOWS.bat
echo.
echo To test the system:
echo   Run TEST_SERVICES.bat
echo.
pause
exit /b 0

:install_error
echo.
echo ============================================================
echo ERROR: Installation failed!
echo ============================================================
echo.
echo Common solutions:
echo 1. Make sure you have internet connection
echo 2. Try running as Administrator
echo 3. Update pip: python -m pip install --upgrade pip
echo 4. Install Visual C++ Build Tools if needed
echo.
pause
exit /b 1