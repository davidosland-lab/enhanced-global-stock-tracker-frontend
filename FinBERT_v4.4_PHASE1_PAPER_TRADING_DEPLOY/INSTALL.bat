@echo off
echo ========================================================================
echo   FinBERT v4.4 - Enhanced Accuracy + Paper Trading
echo   Phase 1 Installation Script
echo ========================================================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo.

echo [2/4] Creating virtual environment (optional but recommended)...
set /p VENV="Create virtual environment? (y/n): "
if /i "%VENV%"=="y" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Skipping virtual environment creation
)
echo.

echo [3/4] Installing required packages...
echo This may take a few minutes...
pip install --upgrade pip
pip install -r requirements.txt
echo.

echo [4/4] Installation complete!
echo.
echo ========================================================================
echo   Installation Summary
echo ========================================================================
echo.
echo Core packages installed:
echo   - Flask + Flask-CORS (Web server)
echo   - yfinance (Market data)
echo   - pandas, numpy (Data processing)
echo   - ta (Technical analysis)
echo   - transformers, torch (FinBERT sentiment)
echo   - scikit-learn (Machine learning)
echo   - apscheduler (Scheduled tasks)
echo.
echo Optional packages (install if needed):
echo   - tensorflow: For LSTM training
echo     pip install tensorflow
echo.
echo ========================================================================
echo   Next Steps
echo ========================================================================
echo.
echo 1. Start the server:
echo    python app_finbert_v4_dev.py
echo.
echo 2. Open browser:
echo    http://localhost:5001
echo.
echo 3. Start analyzing stocks and paper trading!
echo.
echo For LSTM training:
echo    - Single stock: Use "Train Model" button in UI
echo    - Batch (10 stocks): python train_lstm_batch.py
echo.
echo Documentation available in:
echo    - README.md
echo    - README_V4.4.txt
echo    - PHASE_1_PAPER_TRADING_COMPLETE.md
echo.
echo ========================================================================
pause
