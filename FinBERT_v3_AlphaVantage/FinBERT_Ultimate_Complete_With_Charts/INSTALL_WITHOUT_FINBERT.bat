@echo off
echo ================================================================================
echo INSTALLING WITHOUT FINBERT (Quick Installation)
echo ================================================================================
echo.
echo This installs everything EXCEPT transformers/torch (FinBERT)
echo The system will work but use fallback sentiment analysis
echo.

echo Installing core packages...
pip install --upgrade pip
pip install numpy>=1.26.0
pip install pandas yfinance flask flask-cors
pip install scikit-learn ta feedparser requests

echo.
echo ================================================================================
echo Installation complete (without FinBERT)
echo The system will use keyword-based sentiment instead of FinBERT
echo ================================================================================
echo.
pause