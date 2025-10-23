@echo off
echo ============================================
echo STOCK TRACKER PRO - INSTALLATION SCRIPT
echo Version 5.0.0
echo ============================================
echo.
echo This will install all required Python packages.
echo.
pause

echo.
echo [1/2] Installing core requirements...
echo --------------------------------------
pip install -r requirements.txt

echo.
echo [2/2] Verifying installation...
echo --------------------------------------
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import yfinance; print('yfinance: OK')"
python -c "import pandas; print('pandas:', pandas.__version__)"

echo.
echo Testing FinBERT availability...
python -c "from transformers import pipeline; print('FinBERT: Available')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo FinBERT: Not installed (optional)
    echo To enable document sentiment analysis, the transformers library will
    echo download the FinBERT model on first use (~400MB).
) else (
    echo FinBERT: Installed and ready
)

echo.
echo ============================================
echo INSTALLATION COMPLETE
echo ============================================
echo.
echo To start the system, run:
echo   START_ALL_SERVICES.bat
echo.
pause