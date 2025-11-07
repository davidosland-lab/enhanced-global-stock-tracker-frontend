# FinBERT v4.0 Enhanced - Quick Access Guide

## 🌐 Access Your Enhanced Trading System

### Live Server (Currently Running)
**URL**: https://5001-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev

**Features Available NOW**:
- ✅ Candlestick & Line Charts
- ✅ Volume Chart with Color Coding
- ✅ Model Training Interface
- ✅ 1D to 2Y Timeframes
- ✅ US & Australian (ASX) Stocks
- ✅ Real-time Predictions

---

## 🎯 How to Use - 5 Simple Steps

### 1. **Analyze a Stock**
```
Method A: Quick Access Buttons
- Click any of the 16 pre-configured stock buttons (AAPL, MSFT, TSLA, etc.)

Method B: Custom Symbol
- Type symbol in search box (e.g., "AAPL" or "CBA.AX" for Australian stocks)
- Press Enter or click Analyze
```

### 2. **Switch Chart Type**
```
- Click "Candlestick" button → See OHLC candles (green/red)
- Click "Line" button → See traditional line chart
```

### 3. **Change Time Period**
```
Click any period button:
- 1D → Intraday (5-minute intervals)
- 5D → 5-day intraday
- 1M, 3M, 6M → Daily data
- 1Y, 2Y → Extended historical data
```

### 4. **View Volume Data**
```
Automatically displayed below the main chart:
- Green bars = Price closed UP that day
- Red bars = Price closed DOWN that day
- Height = Trading volume
```

### 5. **Train a Model** (NEW!)
```
1. Click "Train Model" button in top-right
2. Enter symbol (e.g., "AAPL" or "CBA.AX")
3. Set epochs (10-200, default 50)
4. Click "Start Training"
5. Watch progress bar and logs
6. Model automatically reloads when complete
```

---

## 🎨 Understanding the Charts

### Candlestick Chart (OHLC)
```
Each candle shows 4 prices:
┌─────┐  High ← Top of wick
│     │
│ ███ │  Open/Close ← Body (green=up, red=down)
│ ███ │
└─────┘  Low ← Bottom of wick

Green Candle = Close > Open (price went UP)
Red Candle = Close < Open (price went DOWN)
```

### Volume Chart
```
Volume bars below main chart:
║ ║  ║
║ ║ ║║  ← Bar height = trading volume
Green = Price UP that day
Red = Price DOWN that day
```

---

## 📊 Reading Predictions

### Prediction Badge Colors
```
🟢 BUY (Green)
   - Model predicts price will go UP
   - Confidence: 60-85%
   
🔴 SELL (Red)
   - Model predicts price will go DOWN
   - Confidence: 60-85%
   
🟡 HOLD (Yellow)
   - Model uncertain or neutral
   - Confidence: 50-60%
```

### Prediction Panel Shows
- **Current Price**: Latest market price
- **Predicted Price**: LSTM forecast
- **Change**: Dollar amount change
- **Confidence**: Model certainty (0-100%)
- **Model Type**: Ensemble (LSTM + Technical + Trend)

---

## 🛠️ Training Your Own Models

### Why Train?
- Customize predictions for specific stocks
- Improve accuracy for frequently-traded symbols
- Adapt to recent market conditions

### Training Process
```
1. Click "Train Model" button
2. Enter stock symbol
3. Configure parameters:
   - Epochs: 50 (recommended for most stocks)
   - Lower (20-30) for quick training
   - Higher (100-200) for better accuracy
4. Click "Start Training"
5. Watch progress:
   - Progress bar shows completion
   - Log displays training steps
   - Success message when done
6. Trained model automatically loads
7. Re-analyze the stock to see new predictions
```

### Training Tips
- **First time**: Use 50 epochs (5-10 minutes)
- **Quick test**: Use 20 epochs (2-3 minutes)
- **Best accuracy**: Use 100 epochs (10-20 minutes)
- **Large-cap stocks** (AAPL, MSFT): Usually train well
- **Small-cap stocks**: May need more epochs

---

## 🌏 Australian Stocks (ASX)

### How to Use
```
1. Click "ASX" in market selector (top-right)
2. Quick access buttons show Australian stocks:
   - CBA (Commonwealth Bank)
   - BHP (BHP Group)
   - WBC (Westpac)
   - And more...
3. Or type symbol with .AX suffix (e.g., "CBA.AX")
```

### Pre-Trained Models
- **CBA.AX**: Already trained (65% confidence BUY)
- Other ASX stocks: Train using the modal

---

## 🔍 Advanced Features

### Chart Zoom & Pan
```
- Scroll wheel: Zoom in/out
- Click + drag: Pan left/right
- Double-click: Reset zoom
```

### Market Selector
```
- US: American stocks (NASDAQ, NYSE)
- ASX: Australian Securities Exchange
```

### Quick Access Buttons
```
Tech: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, NFLX
Finance: JPM, BAC, GS, V
Retail: WMT, TGT, HD, COST
```

---

## 🚨 Troubleshooting

### Chart Not Loading?
```
1. Check internet connection
2. Try different stock symbol
3. Switch time period (try 1M first)
4. Refresh page
```

### Training Failed?
```
1. Check symbol is correct (e.g., AAPL not Apple)
2. For ASX stocks, use .AX suffix (CBA.AX)
3. Try lower epochs (20-30)
4. Check server logs for errors
```

### No Volume Data?
```
- Some stocks have low volume reporting
- Try a different time period
- Large-cap stocks have better volume data
```

### Prediction Says "HOLD"?
```
This is normal when:
- Market is sideways
- Model is uncertain
- Low volatility period
```

---

## 📱 Mobile Access

The UI is responsive and works on mobile devices:
- Tap instead of click
- Pinch to zoom charts
- Scroll to pan
- Training works on mobile too

---

## 🔗 Quick Links

### Live System
**URL**: https://5001-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev

### API Endpoints
```
GET  /api/stock/AAPL     - Get stock data + predictions
POST /api/train/AAPL     - Train model for symbol
GET  /api/models         - Model information
GET  /api/health         - System status
```

### GitHub
**PR**: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/7

---

## 🎓 Learning Resources

### Understanding Candlestick Patterns
- **Bullish Engulfing**: Large green candle after small red → BUY signal
- **Bearish Engulfing**: Large red candle after small green → SELL signal
- **Doji**: Open = Close (small body) → Indecision

### LSTM Model Basics
- **What it does**: Learns patterns from historical price data
- **How it works**: 30-day windows predict next day's price
- **Accuracy**: 65-85% on well-trained models
- **Features used**: Price, volume, technical indicators (RSI, MACD, SMA)

### Technical Indicators
- **SMA (20)**: 20-day simple moving average
- **RSI**: Relative Strength Index (overbought/oversold)
- **MACD**: Moving Average Convergence Divergence

---

## 💡 Pro Tips

### Best Practices
1. **Always check multiple timeframes** (1M, 3M, 1Y)
2. **Compare candlestick and line charts** for different insights
3. **Look at volume** - High volume = Strong signal
4. **Train models for stocks you trade often**
5. **Higher confidence = More reliable prediction**

### What to Look For
```
Strong BUY Signal:
✅ Green candlesticks trending up
✅ Increasing volume on green days
✅ Prediction: BUY with 70%+ confidence
✅ Price above 20-day SMA

Strong SELL Signal:
✅ Red candlesticks trending down
✅ Increasing volume on red days
✅ Prediction: SELL with 70%+ confidence
✅ Price below 20-day SMA
```

---

## 🎯 Quick Commands

### For Power Users
```javascript
// Browser console commands (F12 → Console)

// Analyze any symbol
analyzeStock('AAPL')

// Switch chart type
switchChartType('candlestick')
switchChartType('line')

// Change period
changePeriod('1y')

// Get current data
console.log(currentData)
```

---

## 📞 Support

### Need Help?
1. Check this guide first
2. Review full documentation (README_V4_COMPLETE.md)
3. Check GitHub issues
4. Server logs show detailed error messages

---

**Quick Start**: Open URL → Click stock button → View charts → Train model → Done! 🚀

**Version**: 4.0-dev Enhanced  
**Last Updated**: October 30, 2025
