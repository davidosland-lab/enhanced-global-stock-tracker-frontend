@echo off
echo ============================================================
echo INSTALLING SENTIMENT ANALYSIS WITH PRE-COMPILED PACKAGES
echo ============================================================
echo.

echo Updating pip...
python -m pip install --upgrade pip

echo.
echo Installing packages with pre-compiled wheels...
echo.

REM Flask and extensions
pip install flask==3.0.0
pip install flask-cors==4.0.0

REM Use latest compatible versions that have wheels
pip install yfinance
pip install pandas
pip install numpy
pip install scikit-learn
pip install requests
pip install python-dateutil
pip install werkzeug

echo.
echo ============================================================
echo INSTALLATION COMPLETE!
echo ============================================================
echo.
echo You can now run the application using: RUN_SENTIMENT_FINAL.bat
echo.
pause