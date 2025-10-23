@echo off
REM Simple installer that stays open

echo ============================================================
echo INSTALLING STOCK ANALYSIS SYSTEM
echo ============================================================
echo.

REM Use cmd /k to keep window open no matter what
cmd /k python -m pip install flask flask-cors yfinance pandas numpy scikit-learn requests ta