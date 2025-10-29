@echo off
REM Debug installer - shows everything and doesn't close

title Stock Analysis - Debug Installer
color 0A

echo ============================================================
echo     DEBUG INSTALLER - SHOWS ALL OUTPUT
echo ============================================================
echo.

echo Checking Python path...
where python
echo.

echo Python version:
python --version
echo.

echo Pip version:
pip --version
echo.

echo ============================================================
echo Installing packages (showing all output)...
echo ============================================================
echo.

echo [1/7] Installing Flask...
pip install flask
echo.
echo Press any key to continue to next package...
pause >nul

echo [2/7] Installing Flask-CORS...
pip install flask-cors
echo.
echo Press any key to continue to next package...
pause >nul

echo [3/7] Installing yfinance...
pip install yfinance
echo.
echo Press any key to continue to next package...
pause >nul

echo [4/7] Installing pandas...
pip install pandas
echo.
echo Press any key to continue to next package...
pause >nul

echo [5/7] Installing numpy...
pip install numpy
echo.
echo Press any key to continue to next package...
pause >nul

echo [6/7] Installing scikit-learn...
pip install scikit-learn
echo.
echo Press any key to continue to next package...
pause >nul

echo [7/7] Installing requests...
pip install requests
echo.

echo ============================================================
echo Testing imports...
echo ============================================================
echo.

python -c "import flask; print('Flask: OK')"
python -c "import flask_cors; print('Flask-CORS: OK')"
python -c "import yfinance; print('yfinance: OK')"
python -c "import pandas; print('pandas: OK')"
python -c "import numpy; print('numpy: OK')"
python -c "import sklearn; print('scikit-learn: OK')"
python -c "import requests; print('requests: OK')"

echo.
echo ============================================================
echo Installation complete. Check for any errors above.
echo ============================================================
echo.
echo Press any key to exit...
pause >nul