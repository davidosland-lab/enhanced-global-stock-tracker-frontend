@echo off
REM ============================================================================
REM Individual Stock LSTM Trainer
REM ============================================================================
REM 
REM Train LSTM models for specific stocks not in the overnight top 20.
REM Models saved to: finbert_v4.4.4/models/saved_models/
REM 
REM Usage: Double-click this file or run from command prompt
REM ============================================================================

echo.
echo ================================================================================
echo INDIVIDUAL STOCK LSTM TRAINER
echo ================================================================================
echo.
echo This tool trains LSTM models for specific stocks you choose.
echo.
echo Examples of stocks to train:
echo   - AU: CBA.AX, NAB.AX, WBC.AX, ANZ.AX (banks)
echo   - AU: WOW.AX, WES.AX, CSL.AX (retail/healthcare)
echo   - US: AAPL, GOOGL, MSFT, TSLA
echo   - UK: BP.L, HSBA.L, VOD.L
echo.
echo Models will be saved alongside overnight pipeline models.
echo Estimated time: 3 minutes per stock
echo.
echo ================================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python or activate your virtual environment
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists and activate it
if exist "finbert_v4.4.4\venv\Scripts\activate.bat" (
    echo Activating FinBERT virtual environment...
    call finbert_v4.4.4\venv\Scripts\activate.bat
    echo.
)

REM Run the trainer
python train_individual_stocks.py

REM Deactivate virtual environment if it was activated
if exist "finbert_v4.4.4\venv\Scripts\activate.bat" (
    deactivate 2>nul
)

echo.
echo ================================================================================
echo.
echo Training session complete.
echo.
echo To use the new models:
echo   1. Close this window
echo   2. Restart your trading dashboard (START_DASHBOARD.bat)
echo   3. Models will load automatically for trained stocks
echo.
echo ================================================================================
echo.
pause
