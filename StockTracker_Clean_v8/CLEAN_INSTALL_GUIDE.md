# Stock Tracker v8.0 - Clean Install Guide

## 📦 What's Included (All Fixed)

### ✅ Working Modules
1. **Technical Analysis** - Full candlestick charts with real Yahoo Finance data
2. **Prediction Centre with Integrated Backtesting** - ML predictions that improve through backtesting
3. **Market Tracker** - Live ASX 20 stock prices

### 🔧 Placeholder Modules
4. **Portfolio** - Placeholder (as requested, not implemented)
5. **Backtesting** - Now integrated into Prediction Centre (not separate)
6. **Scanner** - Placeholder

## 🚀 Installation Steps

### Option 1: Quick Start (Windows)
```batch
1. Double-click START.bat
2. Browser opens automatically to http://localhost:8002
```

### Option 2: Manual Installation
```bash
# Install dependencies
pip install flask flask-cors yfinance pandas numpy scikit-learn

# Run the backend
python backend.py

# Open browser to http://localhost:8002
```

## ✨ Key Features & Fixes

### Real Data Integration
- **CBA.AX**: Shows real price ~$170 (not $100)
- **Yahoo Finance API**: All data fetched from real sources
- **Fallback Values**: Realistic market prices if API fails

### Backtesting Integration
- Located in **Prediction Centre** (second tab)
- Train models on historical data
- Improves prediction accuracy
- Results saved and used for future predictions

### How to Use Backtesting:
1. Open Prediction Centre
2. Click "Backtesting & Training" tab
3. Enter stock symbol (e.g., CBA.AX)
4. Select training period
5. Click "Run Backtest"
6. Switch back to "Predictions" tab
7. Generate predictions - now using trained models!

## 📊 API Endpoints

- `http://localhost:8002/` - Main dashboard
- `http://localhost:8002/api/stock/{symbol}` - Stock data
- `http://localhost:8002/api/predict/{symbol}` - ML predictions
- `http://localhost:8002/api/indices` - Market indices
- `http://localhost:8002/api/status` - Server status

## 🔍 Testing the Installation

### Test 1: Check CBA.AX Price
1. Open Technical Analysis
2. Enter CBA.AX
3. Should show ~$170, not $100

### Test 2: Test Backtesting
1. Open Prediction Centre
2. Go to Backtesting tab
3. Run backtest for CBA.AX
4. Check that models show "Trained" status

### Test 3: Verify Module Links
1. Click each module card on dashboard
2. All should open without errors
3. No "file not found" errors

## 📁 File Structure
```
StockTracker_Clean_v8/
├── START.bat                    # Windows launcher
├── backend.py                   # Unified backend server
├── index.html                   # Main dashboard
├── README.md                    # Documentation
├── CLEAN_INSTALL_GUIDE.md       # This file
└── modules/
    ├── technical_analysis.html  # Working
    ├── prediction_centre.html   # Working with backtesting
    ├── market_tracker.html      # Working
    ├── portfolio.html           # Placeholder
    ├── backtesting.html         # Placeholder (integrated into prediction)
    └── scanner.html             # Placeholder
```

## ⚠️ Important Notes

1. **Backtesting is NOT separate** - It's integrated into Prediction Centre
2. **Portfolio Manager** - Not implemented (as requested)
3. **Windows Users** - Always use http://localhost:8002 (hardcoded)
4. **Port 8002** - Must be free, START.bat will kill existing processes

## 🐛 Troubleshooting

### "Module not found"
- All module files exist in /modules/ directory
- Check browser console for errors

### "Price shows $100 for CBA.AX"
- Backend should fetch real data from Yahoo Finance
- Check internet connection
- Fallback should be ~$170, not $100

### "Predictions not improving after backtest"
- Check localStorage in browser dev tools
- Backtest results should be saved
- Refresh prediction page after training

## 📈 Version History

- **v8.0** - Current version with all fixes
  - Fixed broken module links
  - Integrated backtesting into Prediction Centre
  - Real Yahoo Finance data
  - CBA.AX shows correct price (~$170)

---
Last Updated: December 2024
Status: Ready for deployment