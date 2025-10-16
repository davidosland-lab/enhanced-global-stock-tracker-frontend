@echo off
echo ============================================================
echo Fixing setuptools and pip issues
echo ============================================================
echo.

REM First, try to use the system Python to fix pip
echo Step 1: Updating pip using system Python...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Failed to upgrade pip with system Python
    echo Trying alternative method...
    python -m ensurepip --upgrade
)

echo.
echo Step 2: Installing/Updating setuptools and wheel...
python -m pip install --upgrade setuptools wheel
if %errorlevel% neq 0 (
    echo Failed with regular pip, trying with --user flag...
    python -m pip install --user --upgrade setuptools wheel
)

echo.
echo Step 3: Removing old virtual environment...
if exist "venv" (
    rmdir /s /q venv
    echo Old virtual environment removed
)

echo.
echo Step 4: Creating new virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Could not create virtual environment
    echo.
    echo Try these steps manually:
    echo 1. Uninstall Python completely
    echo 2. Download Python 3.11 from python.org
    echo 3. During installation, check "Add Python to PATH"
    echo 4. After installation, run this script again
    pause
    exit /b 1
)

echo.
echo Step 5: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 6: Upgrading pip in virtual environment...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Step 7: Installing basic requirements...
python -m pip install fastapi uvicorn pandas numpy yfinance scikit-learn

echo.
echo ============================================================
echo Fix Complete!
echo ============================================================
echo.
echo Now try running INSTALL_WINDOWS.bat again
echo.
pause