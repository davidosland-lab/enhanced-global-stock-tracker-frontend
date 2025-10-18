@echo off
echo ============================================================
echo ML Stock Prediction System - Installation
echo Version: 2.0 FIXED (Sentiment Disabled)
echo ============================================================
echo.

echo Installing required packages...
echo This may take a few minutes...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install core requirements
pip install pandas numpy scikit-learn
pip install fastapi uvicorn
pip install yfinance
pip install ta

REM Optional but recommended
pip install xgboost
pip install python-multipart

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Run 2_TEST.bat to verify installation
echo 2. Run 3_START.bat to start the system
echo.
pause