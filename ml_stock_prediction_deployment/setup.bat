@echo off
REM ML Stock Prediction System - Quick Setup Script for Windows

echo ML Stock Prediction System Setup
echo ====================================

REM Check Python version
python --version

echo.
echo Step 1: Running diagnostic tool...
python diagnostic_tool.py

echo.
echo Step 2: Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To start the system:
echo   python ml_core_enhanced_production_fixed.py
echo.
echo Then open: http://localhost:8000
pause
