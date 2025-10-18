@echo off
echo =====================================
echo ML Stock Prediction - FIXED VERSION
echo Installing with correct package versions
echo =====================================
echo.

echo Step 1: Uninstalling problematic packages...
python -m pip uninstall -y numpy scipy scikit-learn

echo.
echo Step 2: Installing correct versions...
python -m pip install -r requirements.txt

echo.
echo =====================================
echo Installation Complete!
echo =====================================
echo.
echo Next: Run 2_TEST.bat to verify
pause