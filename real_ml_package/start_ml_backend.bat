@echo off
echo ============================================
echo Starting ML Enhanced Backend Server
echo ============================================
echo.
echo This server provides:
echo - Real ML models (Phase 1-4)
echo - Actual backtesting with historical data
echo - LSTM, GRU, Random Forest, XGBoost, Transformer, GNN, TFT
echo.
echo Server will run on http://localhost:8004
echo.
echo Installing required packages...
pip install yfinance fastapi uvicorn pandas numpy scikit-learn --quiet

echo.
echo Starting ML backend...
echo =====================================
python backend_ml_enhanced.py

pause