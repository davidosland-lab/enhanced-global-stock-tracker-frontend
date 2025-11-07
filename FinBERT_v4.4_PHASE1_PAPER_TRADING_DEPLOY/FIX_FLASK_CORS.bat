@echo off
echo ================================================================================
echo   FinBERT v4.4 - Flask-CORS Installation Fix
echo ================================================================================
echo.
echo This script will fix the "ModuleNotFoundError: No module named 'flask_cors'" error
echo.
echo Step 1: Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)
echo.

echo Step 2: Checking current directory...
echo Current directory: %CD%
echo.

echo Step 3: Attempting to activate virtual environment...
if exist venv\Scripts\activate.bat (
    echo Found virtual environment at: venv\Scripts\activate.bat
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo No virtual environment found. Using system Python.
)
echo.

echo Step 4: Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Step 5: Installing flask-cors directly...
pip install flask-cors
echo.

echo Step 6: Verifying installation...
pip show flask-cors
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: flask-cors installation failed
    echo.
    echo Trying alternative method: Installing all requirements...
    pip install -r requirements.txt
    echo.
    echo Verifying again...
    pip show flask-cors
)
echo.

echo Step 7: Listing all Flask-related packages...
pip list | findstr /I "flask"
echo.

echo ================================================================================
echo   Fix Complete!
echo ================================================================================
echo.
echo If you see Flask-CORS in the list above, the fix was successful.
echo.
echo You can now start the server with:
echo   python app_finbert_v4_dev.py
echo.
echo Or simply double-click: START_FINBERT.bat
echo.
pause
