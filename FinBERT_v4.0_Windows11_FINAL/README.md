# FinBERT v4.0 - AI-Powered Stock Analysis System

**Windows 11 Deployment Package - Clean Install**

---

## 🚀 Quick Start (3 Steps)

### **1. Install**
```cmd
Right-click Command Prompt → Run as Administrator
cd C:\[YourPath]\FinBERT_v4.0_Windows11_CLEAN
scripts\INSTALL_WINDOWS11.bat
```

Choose installation type:
- **[1] FULL** - Complete AI/ML (Recommended) - 900 MB, 10-20 min
- **[2] MINIMAL** - Basic features only - 50 MB, 2-3 min

### **2. Start**
```cmd
START_FINBERT_V4.bat
```

### **3. Access**
Open browser to: **http://127.0.0.1:5001**

---

## ✅ What's Included

### **FULL Install Features:**
- ✅ **Real FinBERT Sentiment** - 97% accuracy on financial texts (NO MOCK DATA!)
- ✅ **TensorFlow LSTM Predictions** - Next-day and 7-day price forecasts
- ✅ **Real News Scraping** - Yahoo Finance + Finviz
- ✅ **Fixed Candlestick Charts** - ECharts with perfect spacing (no overlapping!)
- ✅ **Technical Indicators** - SMA, RSI, MACD
- ✅ **15-Minute Cache** - Avoids rate limits

### **MINIMAL Install Features:**
- ✅ Basic price charts
- ✅ Technical indicators (SMA, RSI, MACD)
- ✅ Volume analysis
- ❌ No sentiment analysis
- ❌ No LSTM predictions

---

## 📋 System Requirements

### **Minimum (MINIMAL Install):**
- Windows 11 (any edition)
- Python 3.8 or higher
- 4 GB RAM
- 500 MB free disk space

### **Recommended (FULL Install):**
- Windows 11 Pro or better
- Python 3.9 or higher
- 8 GB RAM or more
- 2 GB free disk space
- CPU with AVX support (for TensorFlow)

---

## 📦 Package Contents

```
FinBERT_v4.0_Windows11_CLEAN/
├── scripts/
│   └── INSTALL_WINDOWS11.bat       # Installation wizard
├── models/
│   ├── finbert_sentiment.py        # FinBERT analyzer (NO MOCK DATA)
│   ├── news_sentiment_real.py      # Real news scraper
│   ├── lstm_predictor.py           # TensorFlow predictions
│   └── train_lstm.py               # Model training
├── templates/
│   └── finbert_v4_enhanced_ui.html # Fixed UI (ECharts)
├── docs/
│   ├── INSTALLATION_GUIDE.md       # Detailed setup
│   ├── USER_GUIDE.md               # Feature documentation
│   └── TROUBLESHOOTING.md          # Common issues
├── app_finbert_v4_dev.py           # Flask application
├── config_dev.py                   # Configuration
├── START_FINBERT_V4.bat            # Quick start
└── README.md                       # This file
```

---

## 🔧 Installation Details

### **What Gets Installed (FULL):**

**Core Packages:**
- Flask 3.0.0 - Web framework
- NumPy ≥1.26.0 - Numerical computing
- Pandas ≥2.1.0 - Data analysis
- scikit-learn ≥1.3.0 - Machine learning utilities

**Financial Data:**
- yfinance ≥0.2.28 - Yahoo Finance API

**News Scraping:**
- beautifulsoup4 ≥4.12.0 - HTML parsing
- aiohttp ≥3.9.0 - Async HTTP
- lxml ≥4.9.0 - XML/HTML parser

**AI/ML (FULL Only):**
- TensorFlow ≥2.13.0 - Deep learning
- PyTorch ≥2.0.0 - Neural networks
- Transformers ≥4.30.0 - FinBERT model
- sentencepiece ≥0.1.99 - Tokenization

**Total Size:**
- FULL: ~2 GB with all dependencies
- MINIMAL: ~500 MB with basic packages

---

## 🎯 Critical Fixes in v4.0

### **1. Mock Sentiment → Real FinBERT**
**Problem:** System was using hash-based fake sentiment  
**Solution:** Real news scraping with ProsusAI/finbert (97% accuracy)  
**Test Results:**
- AAPL: 9 real articles ✓
- TSLA: 9 real articles ✓
- CBA.AX: 0 articles (no fake fallback) ✓

### **2. Overlapping Candlesticks → Fixed Charts**
**Problem:** Candles overlapping and unreadable  
**Solution:** Replaced Chart.js with ECharts (auto-spacing)  
**Result:** Perfect gaps between candles ✓

### **3. Code Protection**
- Git tag: `v4.0-real-sentiment-complete`
- Backup directory available
- Comprehensive restore instructions

---

## 📊 Usage Examples

### **Analyze a Stock:**
1. Start the application: `START_FINBERT_V4.bat`
2. Open browser to: http://127.0.0.1:5001
3. Enter stock symbol: `AAPL`, `TSLA`, `MSFT`
4. Click "Analyze Stock"
5. View results in 5-10 seconds

### **First Run (FULL Install):**
- First analysis: 20-30 seconds (downloads FinBERT model ~500 MB)
- Subsequent analyses: 5-10 seconds (using cache)

### **Recommended Stocks:**
**Good news coverage (FULL install):**
- US Large Caps: AAPL, TSLA, MSFT, GOOGL, AMZN
- High-profile: NVDA, META, NFLX

**Limited news (expected behavior):**
- Small caps, international stocks (CBA.AX)
- System correctly returns empty (no fake data)

---

## 🐛 Troubleshooting

### **"Python is not recognized"**
- Install Python from https://www.python.org/downloads/
- **CRITICAL:** Check "Add Python to PATH" during installation
- Restart Command Prompt

### **"Port 5001 already in use"**
- Find process: `netstat -ano | findstr :5001`
- Kill process: `taskkill /PID [PID] /F`
- Or edit `config_dev.py` to change port

### **"Module not found"**
- Ensure virtual environment is activated
- Run `START_FINBERT_V4.bat` (auto-activates)
- Or manually: `venv\Scripts\activate`

### **Charts not displaying**
- Check browser console (F12)
- Verify internet connection (CDN for ECharts)
- Try different browser (Chrome recommended)

### **No sentiment data**
- This is expected for stocks with limited news
- Try well-known US stocks: AAPL, TSLA, MSFT
- International stocks may have no news (not a bug!)

**For more help:** See `docs/TROUBLESHOOTING.md` (solutions for 30+ issues)

---

## 📚 Documentation

### **Inside This Package:**
- `README.md` - This file (quick start)
- `docs/INSTALLATION_GUIDE.md` - Detailed installation steps
- `docs/USER_GUIDE.md` - Complete feature documentation
- `docs/TROUBLESHOOTING.md` - Common issues and solutions

### **Online:**
- Pull Request: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/7
- Repository: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend

---

## 🔐 Security & Privacy

- **No data collection** - All analysis runs locally
- **No API keys required** - Uses free Yahoo Finance data
- **Open source** - All code is reviewable
- **Cached locally** - News cached for 15 minutes

---

## ⚙️ Configuration

Edit `config_dev.py` to customize:

```python
# Server settings
PORT = 5001                    # Change if port conflict

# Technical indicators
SMA_SHORT = 20                 # Short-term moving average
SMA_LONG = 50                  # Long-term moving average
RSI_PERIOD = 14                # RSI calculation period

# Data settings
LOOKBACK_DAYS = 90             # Historical data period
CACHE_EXPIRY = 900             # Cache duration (seconds)

# Sentiment settings
NEWS_DAYS = 7                  # Days of news to analyze
MIN_ARTICLES = 3               # Minimum for valid sentiment

# LSTM settings
LSTM_EPOCHS = 50               # Training iterations
SEQUENCE_LENGTH = 60           # Days of history for prediction
```

---

## 🎉 What's New in v4.0

### **Major Changes:**
- ✅ Real FinBERT sentiment (removed all mock data)
- ✅ Fixed candlestick charts (ECharts replacement)
- ✅ News scraping (Yahoo Finance + Finviz)
- ✅ Code protection (git tags + backups)
- ✅ Windows 11 optimized installation
- ✅ Comprehensive documentation

### **Breaking Changes:**
- ❌ Removed `get_mock_sentiment()` - No fake data
- ❌ Removed Chart.js - Replaced with ECharts
- ⚠️ Sentiment returns `None` if no news (not fake data)

---

## 📈 Performance

**Analysis Speed:**
- First run: 20-30 seconds (model download)
- Cached: 5-10 seconds
- News scraping: 2-3 seconds per source

**Memory Usage:**
- FULL: ~1.5 GB (with models loaded)
- MINIMAL: ~200 MB

**Model Sizes:**
- FinBERT: ~500 MB (downloads on first use)
- LSTM: ~5 MB per trained symbol

---

## 🙏 Credits

**Models:**
- FinBERT: ProsusAI/finbert (Hugging Face)
- LSTM: Custom TensorFlow implementation

**Libraries:**
- ECharts v5 (Apache Foundation)
- Flask (Pallets)
- TensorFlow, PyTorch
- Hugging Face Transformers

**Data Sources:**
- Yahoo Finance (yfinance)
- Finviz

---

## 📞 Support

**Documentation:** See `docs/` folder  
**Issues:** Check `docs/TROUBLESHOOTING.md` first  
**Pull Request:** #7  

---

## 📜 License

[Include license information]

---

**Version:** 4.0  
**Release Date:** October 30, 2024  
**Status:** Production Ready  

**🚀 Happy Analyzing!**
