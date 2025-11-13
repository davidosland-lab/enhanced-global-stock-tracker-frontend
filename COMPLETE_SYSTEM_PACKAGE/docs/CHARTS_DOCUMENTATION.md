# 📊 FinBERT Ultimate Trading System - Charting Component

## Overview
The charting component provides comprehensive visualization for the FinBERT Ultimate Trading System, offering real-time market data visualization, technical analysis, and AI-powered predictions in an intuitive interface.

## 🎯 Features

### 1. Chart Types
- **Candlestick Charts**: Traditional OHLC visualization with color-coded bullish/bearish candles
- **Line Charts**: Smooth price trend visualization
- **OHLC Bars**: Open-High-Low-Close bar charts

### 2. Technical Indicators

#### Moving Averages
- **SMA (Simple Moving Average)**: 20-period by default
- **EMA (Exponential Moving Average)**: 20-period with adaptive weighting
- **Bollinger Bands**: Upper and lower bands with 2 standard deviations

#### Oscillators
- **RSI (Relative Strength Index)**: 14-period with overbought/oversold zones
- **MACD**: 12/26/9 configuration with signal line and histogram

#### Volume Analysis
- **Volume Bars**: Color-coded volume visualization
- **Volume Trend**: Comparison with average volume

### 3. AI Predictions Display
- **Next Day Prediction**: Tomorrow's expected price with confidence
- **Target Prices**: 5-10 day price targets with timeframes
- **Sentiment Score**: -1 to +1 scale with visual indicator
- **Prediction Confidence**: Percentage-based confidence metrics

### 4. Economic Indicators Dashboard
- **VIX**: Volatility Index (fear gauge)
- **10Y Treasury**: Bond yields indicator
- **Dollar Index (DXY)**: USD strength measurement
- **Gold Prices**: Safe haven asset tracking
- **Oil Prices**: Energy sector indicator

### 5. News & Sentiment
- Latest news articles with sentiment analysis
- Individual article sentiment scores
- Visual sentiment indicators (📈 📉 📊)
- Direct links to source articles

## 🚀 Quick Start

### Method 1: Using Launcher Script (Recommended)
```batch
# This starts the backend and opens charts automatically
RUN_FINBERT_WITH_CHARTS.bat
```

### Method 2: Manual Start
```batch
# Step 1: Start the backend
python app_finbert_ultimate.py

# Step 2: Open charts in browser
# Open finbert_charts.html in your browser
# Or use TEST_CHARTS.bat
```

### Method 3: Direct Access
1. Ensure backend is running at `http://localhost:5000`
2. Open `finbert_charts.html` in any modern browser

## 📈 Using the Charts

### Basic Operation

1. **Enter Stock Symbol**
   - Type any valid stock symbol (e.g., AAPL, MSFT, TSLA)
   - Supports US stocks, ETFs, and international symbols

2. **Select Time Period**
   - 1 Day: Intraday data
   - 5 Days: Week view
   - 1 Month: Short-term trends
   - 3 Months: Quarter view
   - 6 Months: Half-year analysis
   - 1 Year: Annual perspective

3. **Choose Chart Type**
   - Candlestick: Best for detailed price action
   - Line: Clean trend visualization
   - OHLC: Traditional bar charts

4. **Click Analyze**
   - Fetches latest data
   - Updates all indicators
   - Refreshes predictions

### Advanced Features

#### Indicator Toggles
Click indicator badges to show/hide:
- **SMA**: Simple moving average overlay
- **EMA**: Exponential moving average
- **Bollinger**: Volatility bands
- **Volume**: Volume bars below price

#### Chart Interaction
- **Zoom**: Scroll wheel or pinch to zoom
- **Pan**: Click and drag to move through time
- **Hover**: See detailed tooltip information
- **Reset**: Double-click to reset view

#### Quick Period Selection
Use the quick select buttons for rapid timeframe changes:
- 1D, 5D, 1M, 3M, 6M, 1Y

## 📊 Understanding the Display

### Price Panel
- **Current Price**: Live market price
- **Change**: Dollar and percentage change
- **Color Coding**: Green (up), Red (down)

### Prediction Cards

#### Next Day Prediction
- Expected price for tomorrow
- Direction indicator (↑ or ↓)
- Percentage change expected

#### Target Price (5-10 days)
- Medium-term price target
- Timeframe for reaching target
- Based on volatility and trends

#### Sentiment Score
- Range: -1 (bearish) to +1 (bullish)
- Visual indicator on gradient bar
- Based on FinBERT analysis

### Technical Analysis Summary

#### RSI Reading
- **Value**: 0-100 scale
- **Overbought**: >70 (potential reversal down)
- **Oversold**: <30 (potential reversal up)
- **Neutral**: 30-70

#### MACD Signal
- **Bullish**: MACD above signal line
- **Bearish**: MACD below signal line
- **Histogram**: Momentum strength

#### ATR (Average True Range)
- Volatility measurement
- Higher = more volatile
- Used for stop-loss calculations

#### Volume Trend
- **High**: >20% above average
- **Normal**: Within 20% of average
- **Low**: >20% below average

## 🔧 Customization

### Modify API Endpoint
Edit line in `finbert_charts.html`:
```javascript
const API_BASE = 'http://localhost:5000';
```

### Change Default Symbol
Edit line in `finbert_charts.html`:
```html
<input type="text" id="symbolInput" value="AAPL" ...>
```

### Adjust Indicator Periods
Modify in the JavaScript section:
```javascript
const sma20 = calculateSMA(prices, 20); // Change 20 to desired period
const rsi = calculateRSI(prices, 14);   // Change 14 to desired period
```

### Color Scheme
Modify CSS variables in the style section for different themes.

## 🐛 Troubleshooting

### Charts Not Loading Data

1. **Check Backend**
   ```batch
   curl http://localhost:5000/
   ```
   Should return API information

2. **Verify Symbol**
   - Ensure symbol exists and is valid
   - Try a known symbol like AAPL

3. **Browser Console**
   - Open Developer Tools (F12)
   - Check Console for errors
   - Verify network requests

### Indicators Not Showing

1. **Data Availability**
   - Some indicators need minimum data
   - SMA-50 needs 50+ days
   - Try longer time periods

2. **Toggle State**
   - Click indicator badges to enable
   - Check opacity (0.5 = disabled)

### Predictions Missing

1. **Model Training**
   - Train model first via API
   - Check `/api/predict/{symbol}` response

2. **Data Requirements**
   - Needs sufficient historical data
   - Minimum 50 days recommended

## 📱 Browser Compatibility

### Fully Supported
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

### Partial Support
- Chrome/Edge 80-89
- Firefox 78-87
- Safari 12-13

### Not Supported
- Internet Explorer (any version)
- Browsers before 2020

## 🔄 Real-time Updates

The system updates:
- **Price Data**: On each analysis click
- **Predictions**: With each API call
- **News**: Fetched per symbol
- **Economic Indicators**: On page load

For auto-refresh, add this to the script:
```javascript
setInterval(loadStockData, 60000); // Refresh every minute
```

## 📝 API Integration

### Endpoints Used

1. **Stock Data**
   ```
   GET /api/stock/{symbol}
   ```

2. **Predictions**
   ```
   GET /api/predict/{symbol}
   ```

3. **Historical Data**
   ```
   GET /api/historical/{symbol}?period={period}
   ```

4. **News**
   ```
   GET /api/news/{symbol}
   ```

### Response Format
All endpoints return JSON with consistent structure:
```json
{
  "data": {...},
  "error": null,
  "timestamp": "2024-10-26T12:00:00Z"
}
```

## 🎨 UI Components

### Glass Panel Design
- Semi-transparent backgrounds
- Backdrop blur effect
- Subtle borders
- Smooth shadows

### Color Coding
- **Green**: Positive/Bullish
- **Red**: Negative/Bearish
- **Blue**: Primary actions
- **Purple**: Predictions
- **Gray**: Neutral/Disabled

### Responsive Layout
- Mobile-first design
- Breakpoints at 768px, 1024px
- Touch-friendly controls
- Scalable charts

## 💡 Tips & Best Practices

### For Day Trading
1. Use 1D or 5D timeframes
2. Focus on RSI and MACD
3. Watch volume trends
4. Monitor VIX for volatility

### For Swing Trading
1. Use 1M to 3M timeframes
2. Enable Bollinger Bands
3. Track sentiment changes
4. Watch for MACD crossovers

### For Long-term Investing
1. Use 6M to 1Y timeframes
2. Focus on SMA trends
3. Monitor economic indicators
4. Track sentiment over time

## 🔐 Security Notes

- All data processed client-side
- No sensitive data stored
- API keys kept on backend only
- CORS configured for localhost

## 📚 Further Reading

- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [Technical Analysis Guide](https://www.investopedia.com/technical-analysis-4689657)
- [FinBERT Paper](https://arxiv.org/abs/1908.10063)
- [Random Forest for Stock Prediction](https://scikit-learn.org/stable/modules/ensemble.html#random-forests)

## 📧 Support

For issues or enhancements:
1. Check browser console for errors
2. Verify backend is running
3. Ensure valid stock symbols
4. Try with default settings first

## ⚡ Performance

- Initial load: ~2-3 seconds
- Chart update: <1 second
- Prediction fetch: 1-2 seconds
- Works with 2+ years of data

## 🎯 Roadmap

Planned enhancements:
- [ ] Multiple symbol comparison
- [ ] Custom indicator creation
- [ ] Alert notifications
- [ ] Portfolio tracking
- [ ] Backtesting visualization
- [ ] Mobile app version
- [ ] WebSocket real-time updates
- [ ] Export charts as images
- [ ] Custom color themes
- [ ] Keyboard shortcuts

---

**Remember**: This charting tool visualizes predictions from AI models. Always conduct your own research before making investment decisions.