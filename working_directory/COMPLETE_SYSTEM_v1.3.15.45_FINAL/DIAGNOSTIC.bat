@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM  DIAGNOSTIC - Find Python and Virtual Environment
REM ═══════════════════════════════════════════════════════════════════════════

cd /d "%~dp0"
cls

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   PYTHON ENVIRONMENT DIAGNOSTIC
echo ═══════════════════════════════════════════════════════════════════════════
echo.

echo Current Directory:
echo %CD%
echo.

echo ───────────────────────────────────────────────────────────────────────────
echo Checking for Virtual Environments:
echo ───────────────────────────────────────────────────────────────────────────

if exist "venv\Scripts\activate.bat" (
    echo [FOUND] venv\Scripts\activate.bat
) else (
    echo [NOT FOUND] venv\Scripts\activate.bat
)

if exist ".venv\Scripts\activate.bat" (
    echo [FOUND] .venv\Scripts\activate.bat
) else (
    echo [NOT FOUND] .venv\Scripts\activate.bat
)

if exist "env\Scripts\activate.bat" (
    echo [FOUND] env\Scripts\activate.bat
) else (
    echo [NOT FOUND] env\Scripts\activate.bat
)

if exist "virtualenv\Scripts\activate.bat" (
    echo [FOUND] virtualenv\Scripts\activate.bat
) else (
    echo [NOT FOUND] virtualenv\Scripts\activate.bat
)

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo Checking System Python:
echo ───────────────────────────────────────────────────────────────────────────

python --version 2>nul
if errorlevel 1 (
    echo [NOT FOUND] Python not in PATH
) else (
    echo [FOUND] Python in PATH
    python -c "import sys; print('Location:', sys.executable)"
)

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo Checking for Dashboard File:
echo ───────────────────────────────────────────────────────────────────────────

if exist "unified_trading_dashboard.py" (
    echo [FOUND] unified_trading_dashboard.py
) else (
    echo [NOT FOUND] unified_trading_dashboard.py
)

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo Listing Python Files in Current Directory:
echo ───────────────────────────────────────────────────────────────────────────
dir *.py /b

echo.
echo ───────────────────────────────────────────────────────────────────────────
echo Checking Key Dependencies (if system Python available):
echo ───────────────────────────────────────────────────────────────────────────

python -c "import dash; print('[OK] dash installed')" 2>nul || echo [NOT FOUND] dash
python -c "import plotly; print('[OK] plotly installed')" 2>nul || echo [NOT FOUND] plotly
python -c "import transformers; print('[OK] transformers installed')" 2>nul || echo [NOT FOUND] transformers
python -c "import keras; print('[OK] keras installed')" 2>nul || echo [NOT FOUND] keras
python -c "import torch; print('[OK] torch installed')" 2>nul || echo [NOT FOUND] torch

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   DIAGNOSTIC COMPLETE
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Please share this output so I can help you fix the issue!
echo.

pause
