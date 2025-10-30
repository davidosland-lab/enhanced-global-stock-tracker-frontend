@echo off
echo Testing Python installation...
echo.

python --version
echo.

echo Testing if Python can run a simple script...
python -c "print('Python is working')"
echo.

echo Testing required imports...
echo.

echo 1. Testing numpy...
python -c "import numpy; print('numpy OK')"

echo 2. Testing pandas...
python -c "import pandas; print('pandas OK')"

echo 3. Testing yfinance...
python -c "import yfinance; print('yfinance OK')"

echo 4. Testing flask...
python -c "import flask; print('flask OK')"

echo 5. Testing sklearn...
python -c "import sklearn; print('sklearn OK')"

echo 6. Testing ta...
python -c "import ta; print('ta OK')"

echo.
echo If any of the above failed, that package needs to be installed.
echo.
pause