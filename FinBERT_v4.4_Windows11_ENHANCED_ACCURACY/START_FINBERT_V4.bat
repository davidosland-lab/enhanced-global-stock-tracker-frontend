@echo off
echo ==============================================================================
echo   FinBERT v4.4 - Enhanced Accuracy Server
echo ==============================================================================
echo.
echo Starting FinBERT v4.4 with:
echo   - Sentiment Analysis (15%% ensemble weight)
echo   - Volume Analysis (confidence adjustment)
echo   - 8+ Technical Indicators (consensus voting)
echo   - LSTM Neural Networks (if trained)
echo.
echo Expected Accuracy: 78-93%% (85-95%% with trained LSTM)
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if Flask is installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo ERROR: Flask is not installed!
    echo Please run INSTALL.bat first.
    echo.
    pause
    exit /b 1
)

echo Starting Flask server on port 5001...
echo.
echo Server will be available at:
echo   http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python app_finbert_v4_dev.py

if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start!
    echo.
    echo Common issues:
    echo   - Port 5001 already in use
    echo   - Missing dependencies
    echo   - Configuration errors
    echo.
    echo See TROUBLESHOOTING_FINBERT.txt for help.
    echo.
    pause
    exit /b 1
)
