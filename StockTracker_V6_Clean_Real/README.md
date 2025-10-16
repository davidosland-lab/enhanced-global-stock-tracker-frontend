# Stock Tracker V6 - Clean Real ML Implementation

## 🎯 Overview
This is a **CLEAN INSTALLATION** of Stock Tracker with **100% REAL** machine learning - no fake data, no simulations, no random numbers.

## ✅ What's Different in V6

### Real ML Implementation
- **Training**: Uses actual RandomForest, XGBoost, and Gradient Boosting algorithms
- **Data**: Fetches real historical data from Yahoo Finance
- **Features**: Calculates 50+ real technical indicators
- **Predictions**: Generated from trained models, not Math.random()
- **Storage**: Models saved to disk with joblib, tracked in SQLite

### No More Fake Data
- ❌ No more `Math.random()` for predictions
- ❌ No more simulated training progress
- ❌ No more fake accuracy scores
- ✅ Real training that takes 30s-2min (not exactly 10s)
- ✅ Real model evaluation with train/test splits
- ✅ Real predictions based on learned patterns

## 🚀 Quick Start

### Windows
```batch
# Run the batch file
start.bat
```

### Linux/Mac
```bash
# Make executable and run
chmod +x start.sh
./start.sh
```

### Manual Start
```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Main Backend
python backend.py

# Terminal 2: ML Backend (REAL ML)
python ml_backend.py

# Terminal 3: Web Server
python -m http.server 8080
```

## 📊 Architecture

```
Port 8080: Web Interface
├── ML Training Center (Real training)
├── Prediction Module (Real predictions)
└── Backtesting Suite (Real signals)

Port 8002: Main Backend API
├── Stock data from Yahoo Finance
├── Historical data
└── Technical indicators

Port 8003: ML Backend (REAL ML)
├── RandomForest implementation
├── XGBoost implementation
├── Gradient Boosting
├── Model persistence
└── SQLite tracking
```

## 🧪 How to Verify It's Real

### 1. Check Training Time
- Fake: Always exactly 10 seconds
- **Real: Variable 30s-2min depending on data**

### 2. Check Model Storage
```bash
# Real models are saved as .pkl files
ls saved_models/
# You'll see: AAPL_random_forest_20241014_123456.pkl

# Check database
sqlite3 models.db "SELECT * FROM models;"
```

### 3. Check Training Logs
```bash
tail -f logs/ml_backend.log
# You'll see real training progress, not simulated
```

### 4. Test Consistency
- Train the same model twice
- Results should be similar but not identical
- Fake systems would give exact same results

## 📈 Features

### ML Training Center
- **Real Algorithms**: RandomForest, XGBoost, Gradient Boosting
- **Real Data**: Up to 1000 days of historical prices
- **Real Features**: RSI, MACD, Bollinger Bands, Moving Averages
- **Real Metrics**: Train/Test scores, MAE, RMSE

### Prediction Module  
- Uses trained models from disk
- Calculates confidence based on model performance
- Updates with latest market data

### Technical Stack
- **Backend**: FastAPI (async Python)
- **ML**: scikit-learn, XGBoost
- **Data**: yfinance, pandas, numpy
- **Technical Analysis**: ta library
- **Storage**: SQLite + joblib

## 🔍 API Endpoints

### Main Backend (8002)
- `GET /api/status` - System status
- `GET /api/stock/{symbol}` - Real-time price
- `GET /api/historical/{symbol}` - Historical data
- `GET /api/technical/{symbol}` - Technical indicators

### ML Backend (8003)
- `GET /api/ml/status` - ML system status
- `POST /api/train` - Train a real model
- `POST /api/predict` - Generate real prediction
- `GET /api/models` - List trained models
- `DELETE /api/models/{id}` - Delete a model

## 📝 Training Example

```python
# Request to train a model
POST http://localhost:8003/api/train
{
    "symbol": "AAPL",
    "model_type": "random_forest",
    "days_back": 365
}

# Response (after REAL training)
{
    "model_id": "AAPL_random_forest_20241014_123456",
    "train_score": 0.924,  # Real score
    "test_score": 0.887,   # Real score
    "mae": 2.34,           # Real error
    "training_samples": 292,
    "test_samples": 73
}
```

## ⚠️ Requirements

- Python 3.8+
- 4GB RAM minimum
- Internet connection (for Yahoo Finance)
- ~500MB disk space for models

## 🐛 Troubleshooting

### ML Backend Not Starting
```bash
# Check if port 8003 is in use
netstat -an | grep 8003

# Check logs
cat logs/ml_backend.log
```

### Training Fails
- Ensure symbol exists (e.g., AAPL, MSFT)
- Check internet connection
- Verify Yahoo Finance is accessible

### No Models Showing
```bash
# Check if models are saved
ls saved_models/

# Check database
sqlite3 models.db ".tables"
```

## 🎯 Key Differences from V5

| Feature | V5 (Old) | V6 (Clean) |
|---------|----------|------------|
| Training | Simulated with setTimeout | Real sklearn training |
| Predictions | Math.random() | Model.predict() |
| Training Time | Always 10 seconds | Variable 30s-2min |
| Model Storage | localStorage | SQLite + .pkl files |
| Accuracy | Fake 85-95% | Real cross-validation |
| Features | Not calculated | 50+ indicators |
| Data Source | Sometimes fake | Always Yahoo Finance |

## 📜 License
MIT License - Use freely, but remember: past performance doesn't guarantee future results!

---

**Version**: 6.0 Clean  
**Status**: Production Ready  
**ML**: 100% Real Implementation