# FinBERT Trading System v3.1 - COMPLETE WITH INTRADAY & ZOOM

## 🆕 What's New in v3.1

### Intraday Trading Support
- **Real-time intervals**: 1m, 3m, 5m, 15m, 30m, 60m
- **VWAP indicator** for intraday analysis
- **Auto-refresh** every 30 seconds for live data
- **Time-based display** (HH:MM for intraday)

### Advanced Zoom Features
- **Mouse wheel zoom** - Scroll to zoom in/out
- **Pinch zoom** - Touch device support
- **Drag to zoom** - Draw rectangle to zoom area
- **Pan** - Ctrl+drag to navigate
- **Reset button** - Quick return to full view

### Core Fixes from v3.0
- ✅ **Candlestick charts fixed** - No more overlapping blocks
- ✅ **Real market data only** - No synthetic/fallback data
- ✅ **API endpoints corrected** - All routes working
- ✅ **Confidence scores added** - ML predictions show confidence %

## 📦 Package Contents

```
FinBERT_v3.1_COMPLETE_WITH_INTRADAY/
├── app_finbert_intraday.py       # Main app with all features
├── app_finbert_daily_only.py     # Simplified daily-only version
├── finbert_charts_intraday.html  # Enhanced UI with controls
├── requirements.txt               # Python dependencies
├── INSTALL.bat                    # Windows installer
├── START_INTRADAY.bat            # Start with all features
├── START_DAILY_ONLY.bat          # Start basic version
└── README.md                      # This file
```

## 🚀 Quick Start

### Windows Installation
1. Double-click `INSTALL.bat`
2. Wait for dependencies to install
3. Double-click `START_INTRADAY.bat`
4. Open browser to http://localhost:5000

### Manual Installation
```bash
pip install -r requirements.txt
python app_finbert_intraday.py
```

## 📊 Features Overview

### Trading Intervals
| Interval | Use Case | Best For |
|----------|----------|----------|
| 1m | Scalping | High-frequency trading |
| 3m | Quick trades | Fast momentum plays |
| 5m | Day trading | Standard intraday |
| 15m | Short swing | Quick position trades |
| 30m | Medium swing | Half-day positions |
| 60m | Hourly analysis | Longer intraday holds |
| Daily | Position trading | Traditional analysis |

### Technical Indicators
- **RSI** - Relative Strength Index (overbought/oversold)
- **MACD** - Moving Average Convergence Divergence
- **VWAP** - Volume Weighted Average Price (intraday)
- **SMA/EMA** - Simple/Exponential Moving Averages
- **ATR** - Average True Range (volatility)

### Chart Types
- **Candlestick** - OHLC with color coding
- **OHLC Bars** - Traditional bar chart
- **Line** - Simple price line

### Zoom Controls
- **Scroll** - Mouse wheel up/down
- **Pinch** - Two-finger gesture on touch
- **Drag** - Click and drag to select area
- **Pan** - Ctrl+drag to move around
- **Buttons** - Zoom in (+), out (-), reset (○)

## 🔧 Configuration

### Data Sources
- **Primary**: Yahoo Finance Direct API
- **Secondary**: Alpha Vantage (US stocks)
- **Key**: 68ZFANK047DL0KSR (included)

### API Endpoints

#### Get Stock Data
```
GET /api/stock/<symbol>?interval=5m
```

#### Get Intraday Data
```
GET /api/intraday/<symbol>?interval=1m&range=1d
```

#### Get Historical Data
```
GET /api/historical/<symbol>?period=30d&interval=1d
```

#### Get Predictions
```
GET /api/predict/<symbol>
```

#### Get Economic Indicators
```
GET /api/economic
```

## 🎯 Trading Strategies

### Day Trading Setup
1. Select **5m interval**
2. Set period to **1D**
3. Watch **VWAP** for entries
4. Monitor **RSI** for extremes
5. Use zoom to focus on last 2 hours

### Swing Trading Setup
1. Select **30m or 60m interval**
2. Set period to **5D**
3. Track **MACD** crossovers
4. Watch **SMA20** for support
5. Zoom to key price levels

### Position Trading Setup
1. Select **Daily interval**
2. Set period to **3M or 6M**
3. Analyze long-term trends
4. Check **52-week** highs/lows
5. Zoom out for full picture

## ⚠️ Known Limitations

### Intraday Data
- 1-minute: Last 7 days only
- 3-minute: Aggregated from 2m
- Rate limits apply (wait between requests)

### Australian Stocks
- Work with Yahoo Finance only
- Add .AX suffix (e.g., CBA.AX)

### Alpha Vantage
- 5 requests per minute limit
- US stocks only
- Daily data only

## 🐛 Troubleshooting

### Charts Not Loading
- Clear browser cache
- Check console for errors
- Try a known symbol (AAPL)

### No Intraday Data
- Markets may be closed
- Try during market hours
- Use popular symbols first

### Zoom Not Working
- Update browser
- Enable JavaScript
- Try different chart type

## 📈 Performance Tips

1. **Reduce lag**: Use 5m+ intervals for smoother updates
2. **Optimize zoom**: Reset zoom before changing intervals
3. **Cache data**: Keep browser tab open for faster switching
4. **Best symbols**: Start with liquid stocks (AAPL, MSFT, etc.)

## 🔄 Version History

### v3.1 (Current)
- Added intraday intervals
- Implemented zoom/pan
- Added VWAP indicator
- Auto-refresh feature

### v3.0
- Fixed candlestick overlap
- Real data only
- Added confidence scores
- Fixed API endpoints

### v2.x
- Initial FinBERT integration
- Basic charting
- ML predictions

## 📝 License & Credits

- **Chart.js** - Chart rendering
- **Yahoo Finance** - Market data
- **Alpha Vantage** - Backup data
- **FinBERT** - Sentiment analysis (optional)
- **scikit-learn** - ML predictions

---

**System Ready!** All features tested and working.
For support, check the troubleshooting section above.