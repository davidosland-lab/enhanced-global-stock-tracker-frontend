@echo off
echo =====================================
echo ML Stock Prediction System - Clean Install
echo For Windows with Python 3.12
echo =====================================
echo.

echo Checking Python version...
python --version
echo.

echo Installing required packages...
echo This may take a few minutes...
echo.

pip install -r requirements.txt

echo.
echo =====================================
echo Installation complete!
echo.
echo Next steps:
echo 1. Run 2_test_system.bat to verify installation
echo 2. Run 3_start_server.bat to start the system
echo =====================================
pause