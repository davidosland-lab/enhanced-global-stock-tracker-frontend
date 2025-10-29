@echo off
echo ================================================================================
echo SETTING UP FINBERT MODEL
echo ================================================================================
echo.
echo This will download the FinBERT model if not already cached.
echo Requires internet connection.
echo.

python DOWNLOAD_FINBERT.py

echo.
echo Now trying to start the main application...
echo.

python app_finbert_ultimate_original_with_key.py

pause