@echo off
echo ================================================================================
echo FINBERT v4.4.4 - OVERNIGHT PREDICTION PIPELINE
echo ================================================================================
echo.
echo Full System Features:
echo   - LSTM Neural Network Predictions (45%% weight)
echo   - FinBERT Sentiment Analysis (15%% weight)
echo   - Trend Analysis (25%% weight)
echo   - Technical Analysis (15%% weight)
echo   - SPI 200 Futures Monitoring
echo   - US Market Data Integration
echo.
echo This will run comprehensive overnight analysis
echo Results will include ML predictions and sentiment scores
echo.
echo ================================================================================
echo.
pause

echo Checking dependencies...
echo.

REM Check if required packages are installed
python -c "import yahooquery, pandas, numpy" 2>nul
if errorlevel 1 (
    echo ERROR: Core packages not installed!
    echo.
    echo Please run: INSTALL_DEPENDENCIES.bat
    echo Or manually install: pip install yahooquery pandas numpy
    echo.
    pause
    exit /b 1
)

echo Core packages: OK
echo.

echo Starting overnight pipeline...
echo.

python run_overnight_pipeline.py

echo.
echo ================================================================================
echo Pipeline complete! Check results folder for reports.
echo ================================================================================
echo.
pause
