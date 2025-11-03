@echo off
echo ============================================================
echo INSTALLING SENTIMENT ANALYSIS DEPENDENCIES
echo ============================================================
echo.

echo Updating pip...
python -m pip install --upgrade pip

echo.
echo Installing required packages...
pip install flask==2.3.3
pip install flask-cors==4.0.0
pip install yfinance==0.2.28
pip install pandas==2.0.3
pip install numpy==1.24.3
pip install scikit-learn==1.3.0
pip install requests==2.31.0
pip install python-dateutil==2.8.2
pip install werkzeug==2.3.7

echo.
echo ============================================================
echo INSTALLATION COMPLETE!
echo ============================================================
echo.
echo You can now run the application using: RUN_SENTIMENT_FINAL.bat
echo.
pause