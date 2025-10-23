@echo off
cls
echo ============================================================
echo    STOCK ANALYSIS SYSTEM - DEBUG MODE
echo ============================================================
echo.

echo System Information:
echo -------------------
echo Current Directory: %CD%
echo.

echo Python Check:
echo -------------
where python 2>nul
if %errorlevel% neq 0 (
    echo Python not found in PATH!
) else (
    python --version
    echo Python location: 
    where python
)
echo.

echo Pip Check:
echo ----------
python -m pip --version 2>nul
if %errorlevel% neq 0 (
    echo Pip not available!
)
echo.

echo Files Check:
echo ------------
if exist "app.py" (
    echo [OK] app.py found
) else (
    echo [ERROR] app.py NOT found
)

if exist "requirements.txt" (
    echo [OK] requirements.txt found
) else (
    echo [ERROR] requirements.txt NOT found
)

if exist "venv\" (
    echo [OK] venv folder found
) else (
    echo [INFO] venv folder not found - will be created on first run
)
echo.

echo Testing Python imports:
echo -----------------------
python -c "import sys; print('Python version:', sys.version)"
python -c "import flask; print('Flask installed')" 2>nul || echo Flask not installed
python -c "import yfinance; print('yfinance installed')" 2>nul || echo yfinance not installed
python -c "import sklearn; print('scikit-learn installed')" 2>nul || echo scikit-learn not installed
echo.

echo Press any key to attempt starting the server...
pause >nul

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

set FLASK_SKIP_DOTENV=1
python app.py

pause