@echo off
echo ================================================================================
echo CHECKING INSTALLED PACKAGES
echo ================================================================================
echo.

echo Checking critical packages for FinBERT...
echo.

python -c "import pkg_resources; print('Installed packages:')"
python -m pip list | findstr /i "numpy pandas yfinance flask scikit-learn torch transformers ta feedparser"

echo.
echo ----------------------------------------
echo Checking if transformers/torch are installed (for FinBERT):
python -c "import transformers; print(f'transformers version: {transformers.__version__}')" 2>nul || echo transformers NOT installed
python -c "import torch; print(f'torch version: {torch.__version__}')" 2>nul || echo torch NOT installed

echo.
echo ----------------------------------------
echo If transformers or torch are missing, FinBERT will use fallback sentiment.
echo These packages are LARGE (several GB) and take 5+ minutes to install.
echo.
pause