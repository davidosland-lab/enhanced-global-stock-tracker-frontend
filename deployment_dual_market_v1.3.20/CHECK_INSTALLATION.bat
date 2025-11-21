@echo off
REM ============================================================================
REM Dual Market Screening System - Installation Diagnostic
REM Checks if all dependencies are properly installed
REM ============================================================================

echo ================================================================================
echo   INSTALLATION DIAGNOSTIC CHECK
echo ================================================================================
echo.

echo [1/3] Checking Python and pip...
python --version
pip --version
echo.

echo [2/3] Checking critical packages...
echo.

python -c "import pandas; print('OK: pandas', pandas.__version__)" 2>nul || echo MISSING: pandas
python -c "import numpy; print('OK: numpy', numpy.__version__)" 2>nul || echo MISSING: numpy
python -c "import yfinance; print('OK: yfinance', yfinance.__version__)" 2>nul || echo MISSING: yfinance
python -c "import yahooquery; print('OK: yahooquery', yahooquery.__version__)" 2>nul || echo MISSING: yahooquery
python -c "import flask; print('OK: flask', flask.__version__)" 2>nul || echo MISSING: flask
python -c "import sklearn; print('OK: scikit-learn', sklearn.__version__)" 2>nul || echo MISSING: scikit-learn
python -c "import tensorflow; print('OK: tensorflow', tensorflow.__version__)" 2>nul || echo MISSING: tensorflow
python -c "import transformers; print('OK: transformers', transformers.__version__)" 2>nul || echo MISSING: transformers
python -c "import torch; print('OK: torch', torch.__version__)" 2>nul || echo MISSING: torch
python -c "import hmmlearn; print('OK: hmmlearn', hmmlearn.__version__)" 2>nul || echo MISSING: hmmlearn (optional)

echo.
echo [3/3] Checking module imports...
echo.

python -c "import setup_paths; from models.screening.overnight_pipeline import OvernightPipeline; print('OK: ASX Pipeline')" 2>nul || echo FAILED: ASX Pipeline import
python -c "import setup_paths; from models.screening.us_overnight_pipeline import USOvernightPipeline; print('OK: US Pipeline')" 2>nul || echo FAILED: US Pipeline import
python -c "import setup_paths; from models.finbert_sentiment import FinBERTSentiment; print('OK: FinBERT Sentiment')" 2>nul || echo WARNING: FinBERT Sentiment (optional)
python -c "import setup_paths; from models.lstm_predictor import LSTMPredictor; print('OK: LSTM Predictor')" 2>nul || echo WARNING: LSTM Predictor (optional)

echo.
echo ================================================================================
echo   DIAGNOSTIC COMPLETE
echo ================================================================================
echo.
echo If you see "MISSING" for any required package, run:
echo   pip install [package-name]
echo.
echo If you see "FAILED" for pipeline imports, run:
echo   INSTALL.bat
echo.
pause
