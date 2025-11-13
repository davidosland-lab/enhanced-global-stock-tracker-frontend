@echo off
echo ========================================================
echo FinBERT Ultimate Trading System v3.0 - FIXED INSTALLER
echo ========================================================
echo.
echo This installer will:
echo 1. Install Python dependencies
echo 2. Download FinBERT model (if needed)
echo 3. Set up the environment
echo.

:: Keep window open on error
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Installing core dependencies...
pip install --upgrade pip
pip install numpy>=1.26.0 pandas flask flask-cors requests

echo.
echo [2/4] Installing machine learning dependencies...
pip install scikit-learn

echo.
echo [3/4] Installing FinBERT dependencies (this may take a while)...
echo Note: If this step fails, the system will use fallback sentiment analysis
pip install transformers torch --index-url https://download.pytorch.org/whl/cpu

echo.
echo [4/4] Installing additional dependencies...
pip install python-dateutil urllib3

echo.
echo ========================================================
echo Installation Complete!
echo ========================================================
echo.
echo To start the system:
echo 1. Run: python app_finbert_v3_fixed.py
echo 2. Open: http://localhost:5000
echo.
echo The system will automatically download the FinBERT model
echo on first run (about 420MB).
echo.
echo Press any key to exit...
pause >nul