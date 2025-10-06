@echo off
echo ============================================================
echo    Windows 11 Stock Tracker - Starting...
echo ============================================================
echo.
echo Features:
echo   - Real-time stock data from Yahoo Finance
echo   - SQLite local storage (100x faster backtesting)
echo   - CBA Enhanced tracker with Documents/Media
echo   - Phase 4 predictor with GNN models
echo   - Document analyzer with FinBERT
echo.
echo Starting backend server on http://localhost:8002
echo.
python backend.py
pause
