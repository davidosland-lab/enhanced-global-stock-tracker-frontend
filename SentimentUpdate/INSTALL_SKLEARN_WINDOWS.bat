@echo off
title Stock Analysis - Complete Installation with scikit-learn
echo ======================================================================
echo    STOCK ANALYSIS WITH ML & SENTIMENT - FULL INSTALLATION
echo ======================================================================
echo.
echo This installer will set up the complete application with ML features.
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [✓] Python detected
echo.

REM Create virtual environment
echo [*] Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [✓] Virtual environment created
) else (
    echo [!] Virtual environment already exists
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip and essential tools
echo [*] Upgrading pip and build tools...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1

echo.
echo ======================================================================
echo    INSTALLING PACKAGES
echo ======================================================================
echo.

REM Method 1: Try conda if available
where conda >nul 2>&1
if %errorlevel%==0 (
    echo [*] Conda detected! Using conda for scikit-learn...
    conda install -y scikit-learn pandas numpy -c conda-forge 2>nul
    if %errorlevel%==0 (
        echo [✓] Installed via conda
        goto :install_rest
    )
)

REM Method 2: Try pre-built wheels
echo [*] Installing core packages with pre-built wheels...
echo.

echo [1/7] Installing numpy (required for pandas and sklearn)...
pip install numpy --only-binary :all: --prefer-binary >nul 2>&1
if errorlevel 1 (
    echo    [!] Trying alternate numpy version...
    pip install numpy==1.24.3 --only-binary :all: 2>nul || pip install numpy
)

echo [2/7] Installing pandas...
pip install pandas --only-binary :all: --prefer-binary >nul 2>&1
if errorlevel 1 (
    echo    [!] Trying alternate pandas version...
    pip install pandas==2.0.3 --only-binary :all: 2>nul || pip install pandas
)

echo [3/7] Installing scikit-learn (this is important!)...
REM Try multiple methods for sklearn
pip install scikit-learn --only-binary :all: --prefer-binary >nul 2>&1
if errorlevel 1 (
    echo    [!] Trying alternate sklearn installation methods...
    
    REM Method 2a: Try specific version with wheels
    pip install scikit-learn==1.3.0 --only-binary :all: 2>nul
    if errorlevel 1 (
        REM Method 2b: Try from PyPI with no deps first
        pip install --no-deps scikit-learn 2>nul
        pip install scikit-learn 2>nul
        
        if errorlevel 1 (
            echo    [!] scikit-learn installation challenging. Trying final method...
            REM Method 2c: Last resort - any compatible version
            pip install "scikit-learn>=1.0.0" --prefer-binary
        )
    )
)

:install_rest
echo [4/7] Installing Flask...
pip install flask flask-cors --prefer-binary >nul 2>&1

echo [5/7] Installing yfinance...
pip install yfinance --prefer-binary >nul 2>&1

echo [6/7] Installing requests...
pip install requests --prefer-binary >nul 2>&1

echo [7/7] Installing remaining dependencies...
pip install python-dateutil werkzeug --prefer-binary >nul 2>&1

echo.
echo ======================================================================
echo    VERIFYING INSTALLATION
echo ======================================================================
echo.

REM Run diagnostic
python diagnostic_full.py 2>nul
if errorlevel 1 (
    echo.
    echo [!] Some components failed. Running simplified test...
    echo.
    python -c "import flask; print('[✓] Flask: OK')" 2>nul || echo [✗] Flask: FAILED
    python -c "import yfinance; print('[✓] yfinance: OK')" 2>nul || echo [✗] yfinance: FAILED
    python -c "import pandas; print('[✓] pandas: OK')" 2>nul || echo [✗] pandas: FAILED
    python -c "import numpy; print('[✓] numpy: OK')" 2>nul || echo [✗] numpy: FAILED
    python -c "import sklearn; from sklearn.ensemble import RandomForestRegressor; print('[✓] scikit-learn: OK with RandomForest')" 2>nul || echo [✗] scikit-learn: FAILED
)

echo.
echo ======================================================================
echo    CHECKING WHICH VERSION TO USE
echo ======================================================================
echo.

REM Check if sklearn works
python -c "import sklearn; exit(0)" 2>nul
if %errorlevel%==0 (
    echo [✓] FULL ML VERSION AVAILABLE!
    echo.
    echo You can use the complete application with ML predictions:
    echo   File: app_enhanced_sentiment_fixed.py
    echo   Run:  python app_enhanced_sentiment_fixed.py
    echo.
    echo Features:
    echo   - RandomForest ML predictions
    echo   - Feature importance analysis
    echo   - Sentiment-enhanced predictions
    echo   - All market indicators
) else (
    echo [!] scikit-learn not available
    echo.
    echo Use the simplified version without sklearn:
    echo   File: app_sentiment_no_sklearn.py
    echo   Run:  python app_sentiment_no_sklearn.py
    echo.
    echo Features:
    echo   - Trend-based predictions
    echo   - All sentiment indicators still work
    echo   - Technical analysis
    echo   - Real-time data
)

echo.
echo ======================================================================
echo    TROUBLESHOOTING TIPS
echo ======================================================================
echo.
echo If scikit-learn fails to install:
echo.
echo Option 1: Install Anaconda/Miniconda
echo   - Download from: https://www.anaconda.com/products/distribution
echo   - Then run: conda install scikit-learn pandas numpy
echo.
echo Option 2: Install Visual C++ Build Tools
echo   - Download from: https://visualstudio.microsoft.com/downloads/
echo   - Select "Desktop development with C++"
echo   - Restart and try installation again
echo.
echo Option 3: Use the no-sklearn version
echo   - It has all features except RandomForest ML
echo   - Run: python app_sentiment_no_sklearn.py
echo.
pause