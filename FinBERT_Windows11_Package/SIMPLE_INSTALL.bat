@echo off
REM Simple Installation - Works without FinBERT if needed
REM This version installs minimal requirements and runs in fallback mode

echo ========================================
echo Simple Installation (Fallback Mode)
echo Works even if FinBERT fails to install
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

echo [✓] Python found
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist "venv_simple" rmdir /s /q venv_simple
python -m venv venv_simple
call venv_simple\Scripts\activate.bat
echo [✓] Virtual environment created
echo.

REM Upgrade pip and install basics
echo Installing basic requirements...
python -m pip install --upgrade pip setuptools wheel

REM Install only essential packages (no torch/transformers)
pip install numpy pandas yfinance flask flask-cors scikit-learn requests tqdm

echo.
echo ========================================
echo Simple Installation Complete!
echo ========================================
echo.
echo This installation runs in FALLBACK MODE:
echo - No FinBERT (uses keyword sentiment)
echo - No PyTorch required
echo - Smaller download (~50MB vs 500MB)
echo - Still provides trading predictions!
echo.
echo To run: python app_finbert_trading.py
echo.
pause