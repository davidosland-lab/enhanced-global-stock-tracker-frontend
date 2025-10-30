@echo off
echo ================================================================================
echo STARTING WORKING API WITH REAL DATA
echo ================================================================================
echo.
echo This version uses:
echo   - Direct Yahoo Finance API (bypasses broken yfinance)  
echo   - Alpha Vantage for US stocks
echo   - REAL MARKET DATA ONLY
echo.

REM Kill existing Python
taskkill /F /IM python.exe 2>nul
timeout /t 2

python app_working_api.py

pause