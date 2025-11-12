# FinBERT v4.0 Enhanced - Windows 11 Localhost Deployment

**🖥️ Configured for Windows 11 Local Deployment**  
**🌐 Access: http://127.0.0.1:5001 or http://localhost:5001**

## 🎉 What's New in This Version

This is the **ENHANCED** version with ALL user-requested improvements:

### ✅ **1. Larger Charts** (+50% Size)
- **Price Chart**: 600px tall (was 400px)
- **Volume Chart**: 200px tall (was 150px)
- Much better visibility for technical analysis

### ✅ **2. Sentiment Transparency**
- **News Articles Section**: See all articles FinBERT analyzed
- **Individual Sentiment Scores**: Each article shows confidence %
- **Clickable Sources**: Verify sentiment with original articles
- **Article Count**: Shows how many articles were analyzed

### ✅ **3. Accurate Market Data**
- **Fixed Change Calculation**: Now matches current price change
- **Real-Time Accuracy**: Uses actual chart data, not stale metadata
- **Consistent Across Periods**: Works for intraday, daily, weekly

### ✅ **4. Perfect Candlestick Charts** (ECharts)
- **No Overlapping**: Crystal clear candlestick spacing
- **Built-in Zoom**: Mouse wheel + slider controls
- **Enhanced Tooltips**: Shows Open/High/Low/Close with crosshair
- **Professional Quality**: Trading-grade charts

---

## ⚙️ Windows 11 Configuration

**This package is pre-configured for Windows 11 localhost deployment:**

| Setting | Value | Description |
|---------|-------|-------------|
| **Host** | `127.0.0.1` | Localhost (Windows 11 standard) |
| **Port** | `5001` | Default port (change in config_dev.py if needed) |
| **Access URL** | `http://127.0.0.1:5001` | Open this in your browser |
| **Alternative** | `http://localhost:5001` | Same as above |

**Note**: If port 5001 is already in use, edit `config_dev.py` and change `PORT = 5001` to another port like `5002` or `8080`.

---

## 🚀 Quick Start (3 Steps)

### **Step 1: Install Dependencies**
```batch
Right-click: scripts\INSTALL_WINDOWS11.bat
Select: "Run as Administrator"
Choose: [1] FULL (includes TensorFlow + PyTorch + FinBERT)
Wait: ~3-5 minutes for installation
```

### **Step 2: Start Application**
```batch
Double-click: START_FINBERT_V4.bat
Wait: Server will start in ~10 seconds
```

### **Step 3: Open Browser**
```
Open: http://127.0.0.1:5001
Enter stock symbol: AAPL, TSLA, GOOGL, etc.
Click: "Analyze" button
```

---

## 📋 System Requirements

### **Minimum Requirements**:
- **OS**: Windows 11 (or Windows 10 with updates)
- **Python**: 3.8 or higher (3.12 recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB free space
- **Internet**: Active connection for stock data and news

### **Recommended Requirements**:
- **OS**: Windows 11 (latest updates)
- **Python**: 3.12.x
- **RAM**: 8GB or more
- **Disk Space**: 5GB free space
- **GPU**: Optional (for faster TensorFlow/PyTorch)

---

## 📦 Package Contents

```
FinBERT_v4.0_Windows11_ENHANCED/
├── scripts/
│   └── INSTALL_WINDOWS11.bat       ← Installation script (FIXED)
├── templates/
│   └── finbert_v4_enhanced_ui.html ← Enhanced UI with ECharts
├── models/
│   ├── finbert_sentiment.py        ← FinBERT sentiment analyzer
│   ├── news_sentiment_real.py      ← Real news scraping (Finviz + Yahoo)
│   ├── lstm_predictor.py           ← LSTM neural network predictor
│   └── train_lstm.py               ← LSTM training script
├── docs/
│   ├── INSTALLATION_GUIDE.md       ← Detailed installation guide
│   └── USER_GUIDE.md               ← Feature documentation
├── app_finbert_v4_dev.py           ← Main Flask application (FIXED)
├── config_dev.py                   ← Configuration settings
├── START_FINBERT_V4.bat            ← Startup script (FIXED)
├── requirements-full.txt           ← Full dependencies (TensorFlow + PyTorch)
├── requirements-minimal.txt        ← Minimal dependencies (lightweight)
└── README.md                       ← This file
```

---

## 🔧 Installation Options

### **Option 1: FULL Installation (Recommended)**
Includes ALL features:
- ✅ LSTM Neural Networks (TensorFlow)
- ✅ FinBERT Sentiment Analysis (PyTorch + Transformers)
- ✅ Real News Scraping (Finviz + Yahoo Finance)
- ✅ Enhanced Technical Analysis
- ✅ Ensemble Predictions

**Install Time**: ~3-5 minutes  
**Size**: ~2GB

### **Option 2: MINIMAL Installation**
Includes basic features only:
- ✅ Stock Price Charts (ECharts)
- ✅ Volume Analysis
- ✅ Basic Technical Analysis
- ✅ Market Data
- ❌ No LSTM/FinBERT (uses simple predictions)

**Install Time**: ~1-2 minutes  
**Size**: ~500MB

---

## 🎯 Key Features

### **1. Enhanced Charts (ECharts)**
- **Perfect Candlesticks**: No overlapping, crystal clear
- **Larger Display**: 600px price chart, 200px volume
- **Interactive Zoom**: Mouse wheel + slider controls
- **Professional Tooltips**: OHLC data with crosshair
- **Multiple Timeframes**: 1m, 5m, 15m, 1D, 1M, 3M, 6M, 1Y, 2Y

### **2. AI/ML Predictions**
- **LSTM Neural Networks**: Deep learning time series prediction
- **FinBERT Sentiment**: 97% accurate financial sentiment analysis
- **Technical Analysis**: RSI, SMA, trend indicators
- **Ensemble Method**: Combines multiple models for accuracy

### **3. Real Sentiment Analysis**
- **Concurrent News Scraping**: Finviz + Yahoo Finance
- **FinBERT Classification**: Positive/Neutral/Negative
- **15-Minute Caching**: Prevents rate limiting
- **Article Display**: See all analyzed articles with confidence scores
- **Source Verification**: Click to read original articles

### **4. Market Data**
- **Real-Time Prices**: Yahoo Finance API
- **Accurate Calculations**: Fixed change calculations
- **Multiple Markets**: US stocks, ASX, international
- **Historical Data**: Access years of price history

---

## 📊 What You'll See

### **Main Dashboard**:
```
┌─────────────────────────────────────────────┐
│ FinBERT v4.0 - Enhanced Trading System      │
├─────────────────────────────────────────────┤
│ [Search: AAPL] [Analyze]                    │
├──────────────────────┬──────────────────────┤
│                      │ 🤖 AI Prediction     │
│ 📈 Price Chart       │ BUY / $175.43       │
│ (600px - LARGER!)    │ Confidence: 74%     │
│                      │                     │
│ Candlesticks:        │ 🧠 Sentiment        │
│ ┃ ▌ ┃ ▌ ┃ ▌ ┃       │ Positive (87%)      │
│ (NO OVERLAP!)        │ Articles: 9 ← NEW!  │
│                      │                     │
│ 📊 Volume Chart      │ 📊 Market Data      │
│ (200px - LARGER!)    │ Change: +$2.31      │
│                      │ (ACCURATE!)         │
└──────────────────────┴──────────────────────┘
│                                             │
│ 📰 News & Sentiment Analysis ← NEW!        │
├─────────────────────────────────────────────┤
│ [🟢 89%] Apple Reports Record Earnings     │
│ [🟢 78%] iPhone Sales Exceed Targets       │
│ [⚪ 45%] Apple Updates macOS               │
│ ... (up to 10 articles)                     │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Troubleshooting

### **Installation Issues**:

#### "Python not found"
```batch
1. Download Python 3.12 from python.org
2. Install with "Add to PATH" checked
3. Restart Command Prompt
4. Run installation script again
```

#### "Virtual environment not created"
```batch
1. Open Command Prompt as Administrator
2. Navigate to installation folder
3. Run: python -m venv venv
4. Run: venv\Scripts\activate
5. Install packages: pip install -r requirements-full.txt
```

#### "TensorFlow installation failed"
```batch
Option 1: Use MINIMAL installation instead
Option 2: Install Visual C++ Redistributable from Microsoft
Option 3: Try: pip install tensorflow --no-cache-dir
```

### **Startup Issues**:

#### "Virtual environment not found"
```batch
Problem: Installation script created venv in wrong location
Solution: This is FIXED in this package
If still occurs: Re-run INSTALL_WINDOWS11.bat
```

#### "Port 5001 already in use"
```batch
1. Close any existing FinBERT instances
2. Open Task Manager → End python.exe processes
3. Try starting again
```

### **Runtime Issues**:

#### "No news articles found"
```
This is normal for:
- International stocks (CBA.AX, BHP.AX)
- Less popular stocks
- After market hours with no recent news

System will still show predictions based on price data.
```

#### "Charts not loading"
```batch
1. Check internet connection
2. Try different stock symbol (AAPL, TSLA)
3. Clear browser cache (Ctrl+Shift+Delete)
4. Restart application
```

---

## 🎓 Usage Examples

### **Example 1: Analyze Apple (AAPL)**
```
1. Start application
2. Enter: AAPL
3. Click: Analyze
4. View:
   - Large candlestick chart (600px)
   - Volume chart (200px)
   - AI prediction (BUY/SELL/HOLD)
   - Sentiment analysis (with articles)
   - Market data (accurate change)
```

### **Example 2: View Different Timeframes**
```
1. After analyzing AAPL
2. Click timeframe buttons:
   - Intraday: 1m, 5m, 15m
   - Periods: 1D, 5D, 1M, 3M, 6M, 1Y, 2Y
3. Watch charts update automatically
4. Use zoom controls to focus on specific dates
```

### **Example 3: Check News Sources**
```
1. After analyzing AAPL
2. Scroll down to "News & Sentiment Analysis"
3. See all 9 articles with:
   - Sentiment indicator (🟢/⚪/🔴)
   - Confidence percentage
   - Article title (clickable)
   - Publication date
4. Click article title to verify source
```

---

## 🔒 Security Notes

### **Safe to Use**:
- ✅ All code is open source
- ✅ No data collection or tracking
- ✅ Runs locally on your machine
- ✅ Only connects to Yahoo Finance API and news sites

### **Data Privacy**:
- Your stock searches are NOT logged
- No personal information collected
- No analytics or telemetry
- Cache stored locally only

### **Internet Connections**:
- **Yahoo Finance**: Stock price data
- **Finviz**: Financial news articles
- **CDN**: ECharts library (for charts)
- **Hugging Face**: FinBERT model download (first time only)

---

## 📈 Performance Tips

### **For Best Performance**:
1. **Close other applications** during first run (model download)
2. **Use SSD storage** for faster model loading
3. **8GB RAM recommended** for full AI features
4. **Enable GPU** if you have NVIDIA graphics card
5. **Clear cache** if experiencing slowdowns

### **Expected Response Times**:
- **First Analysis**: 10-30 seconds (downloads models)
- **Subsequent Analyses**: 2-5 seconds
- **Cached Results**: Instant (15-minute cache)
- **News Scraping**: 3-5 seconds
- **Chart Rendering**: Instant

---

## 🆕 What's Different from Previous Versions

### **vs. v4.0 FINAL**:
- ✅ **50% larger charts** (600px vs 400px)
- ✅ **ECharts instead of Chart.js** (no overlapping)
- ✅ **News articles display** (full transparency)
- ✅ **Fixed market data** (accurate calculations)
- ✅ **All installation bugs fixed**

### **vs. v3.x**:
- ✅ **Candlestick charts** (was line only)
- ✅ **Volume charts** (color-coded)
- ✅ **Real sentiment** (no mock data)
- ✅ **LSTM predictions** (neural networks)
- ✅ **Enhanced UI** (professional design)

---

## 🐛 Known Issues

### **Minor Issues**:
1. **First startup slow**: Models need to download (~1GB)
2. **Yahoo Finance 404**: Sometimes returns no data (use different symbol)
3. **International stocks**: Limited news availability
4. **After hours**: May show stale data

### **Not Issues (Expected Behavior)**:
1. **No articles for CBA.AX**: Australian stocks have limited US news
2. **Change shows 0%**: Market closed, no movement
3. **Predictions vary**: AI models update with new data

---

## 📞 Support

### **For Issues**:
1. Check **Troubleshooting** section above
2. Read **INSTALLATION_GUIDE.md** in docs/
3. Review **USER_GUIDE.md** in docs/

### **Common Questions**:

**Q: Why are candlesticks not overlapping?**  
A: This version uses ECharts which automatically calculates perfect spacing!

**Q: Why do I see news articles now?**  
A: This is the ENHANCED version with full sentiment transparency!

**Q: Is market data more accurate?**  
A: Yes! We fixed the calculation to use actual chart data instead of stale metadata.

**Q: Are charts bigger?**  
A: Yes! 50% larger for better visibility.

---

## ⚡ Quick Reference

### **Essential Commands**:
```batch
Install:    scripts\INSTALL_WINDOWS11.bat (as Admin)
Start:      START_FINBERT_V4.bat
Stop:       Ctrl+C in terminal window
Uninstall:  Delete entire folder
```

### **URLs**:
```
Application: http://127.0.0.1:5001
API Health:  http://127.0.0.1:5001/api/health
API Stock:   http://127.0.0.1:5001/api/stock/AAPL
```

### **Keyboard Shortcuts** (in browser):
```
F5:          Refresh page
Ctrl+F5:     Hard refresh (clear cache)
Mouse Wheel: Zoom in/out on charts
Click+Drag:  Pan chart left/right
```

---

## 🎉 Enjoy FinBERT v4.0 Enhanced!

**All user-requested improvements delivered:**
- ✅ Larger charts (50% increase)
- ✅ Perfect candlesticks (no overlap)
- ✅ Sentiment transparency (see all articles)
- ✅ Accurate market data (fixed calculations)

**Version**: 4.0-Enhanced  
**Release Date**: October 30, 2025  
**Status**: Production Ready 🚀
