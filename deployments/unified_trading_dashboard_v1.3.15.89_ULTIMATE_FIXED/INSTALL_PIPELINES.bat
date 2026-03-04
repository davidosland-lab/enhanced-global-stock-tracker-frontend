@echo off
REM Install Overnight Pipelines Dependencies
REM Updates FinBERT v4.4.4 venv with additional packages required for pipelines

chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ================================================================================
echo OVERNIGHT PIPELINES - DEPENDENCY INSTALLER v1.3.15.87
echo ================================================================================
echo.
echo This will install additional dependencies required for overnight pipelines:
echo   - yahooquery (market data)
echo   - statsmodels (regime analysis)
echo   - dash + plotly (dashboard)
echo   - beautifulsoup4 (news scraping)
echo.
echo Virtual Environment: finbert_v4.4.4\venv
echo Estimated Time: 2-5 minutes
echo Disk Space Required: ~500 MB
echo.
echo ================================================================================
echo.

REM Check if venv exists
if not exist "%~dp0finbert_v4.4.4\venv\Scripts\python.exe" (
    echo [ERROR] FinBERT venv not found!
    echo.
    echo Please run INSTALL.bat first to create the virtual environment.
    echo.
    pause
    exit /b 1
)

set "PYTHON=%~dp0finbert_v4.4.4\venv\Scripts\python.exe"
set "PIP=%~dp0finbert_v4.4.4\venv\Scripts\pip.exe"

echo [1/4] Upgrading pip...
"%PYTHON%" -m pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] pip upgrade failed, continuing...
)

echo.
echo [2/4] Installing market data packages...
"%PIP%" install yahooquery>=2.3.0 yfinance>=0.2.30
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install yahooquery/yfinance
    pause
    exit /b 1
)

echo.
echo [3/4] Installing analysis packages...
"%PIP%" install statsmodels>=0.13.0 scipy>=1.10.0
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] statsmodels/scipy installation failed, some features may not work
)

echo.
echo [4/4] Installing dashboard and utilities...
"%PIP%" install dash>=2.11.0 plotly>=5.15.0 beautifulsoup4>=4.12.0 lxml>=4.9.0
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Dashboard packages installation failed
)

echo.
echo ================================================================================
echo INSTALLATION COMPLETE
echo ================================================================================
echo.
echo Installed Packages:
echo   - yahooquery (market data)
echo   - yfinance (market data backup)
echo   - statsmodels (regime analysis)
echo   - dash + plotly (dashboard)
echo   - beautifulsoup4 (news scraping)
echo.
echo Next Steps:
echo   1. Test a single pipeline:
echo      cd pipelines
echo      RUN_AU_PIPELINE.bat
echo.
echo   2. Run all pipelines:
echo      cd pipelines
echo      RUN_ALL_PIPELINES.bat
echo.
echo ================================================================================
echo.

pause
exit /b 0
