@echo off
echo ================================================================================
echo FINBERT ULTIMATE v3.0 - CLEAN INSTALLATION WITH ALPHA VANTAGE
echo ================================================================================
echo.

echo Step 1: Cleaning any existing cache/environment issues...
echo ----------------------------------------
REM Clean cache
if exist "%USERPROFILE%\.cache\py-yfinance" (
    echo Removing yfinance cache...
    RMDIR /S /Q "%USERPROFILE%\.cache\py-yfinance"
)
if exist "%LOCALAPPDATA%\py-yfinance" (
    RMDIR /S /Q "%LOCALAPPDATA%\py-yfinance"
)

REM Remove any .env files
if exist ".env" del /f /q ".env"
if exist "..\.env" del /f /q "..\.env"

echo.
echo Step 2: Setting environment variables...
echo ----------------------------------------
SET FLASK_SKIP_DOTENV=1
SET YFINANCE_CACHE_DISABLE=1
SET PYTHONIOENCODING=utf-8
SET PYTHONUNBUFFERED=1

echo.
echo Step 3: Installing required packages...
echo ----------------------------------------
pip install --upgrade pip
pip install numpy>=1.26.0
pip install pandas yfinance requests flask flask-cors
pip install scikit-learn ta feedparser
pip install transformers torch --no-deps 2>nul
pip install alpha-vantage

echo.
echo Step 4: Creating necessary directories...
echo ----------------------------------------
if not exist "cache" mkdir cache
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "data" mkdir data

echo.
echo ================================================================================
echo Installation Complete!
echo ================================================================================
echo.
echo Data Sources Configured:
echo   - Primary: Yahoo Finance
echo   - Secondary: Alpha Vantage (Key: 68ZFANK047DL0KSR)
echo.
echo To start the system:
echo   Run: START_SYSTEM.bat
echo.
pause