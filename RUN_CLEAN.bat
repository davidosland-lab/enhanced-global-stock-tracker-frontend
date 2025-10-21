@echo off
echo Starting CLEAN version - No JavaScript errors
echo.
set FLASK_SKIP_DOTENV=1
set PYTHONIOENCODING=utf-8
python unified_stock_CLEAN.py
pause