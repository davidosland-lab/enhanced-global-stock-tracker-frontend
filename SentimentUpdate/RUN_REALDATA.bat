@echo off
title Stock Analysis - Real Data Only
echo ============================================================
echo    STOCK ANALYSIS - 100%% REAL MARKET DATA
echo ============================================================
echo.
echo NO synthetic data, NO demo data, NO fallbacks
echo Only real market information from:
echo - Yahoo Finance
echo - Alpha Vantage
echo.

REM First run the fix utility
echo Running Yahoo Finance fix utility...
python fix_yahoo_finance.py

echo.
echo Starting real data application...
python app_enhanced_realdata.py

pause