# Stock Analysis with ML & Sentiment - Installation Guide

## 🚀 Quick Start

### Step 1: Run Diagnostic
```batch
python diagnostic_full.py
```
This will tell you which version you can use.

### Step 2: Choose Your Installation Path

#### Option A: Full ML Version (with scikit-learn)
If diagnostic shows scikit-learn is available or can be installed:

```batch
# Install dependencies
INSTALL_SKLEARN_WINDOWS.bat

# Run the app
python app_enhanced_sentiment_fixed.py
```

**Features:**
- ✅ RandomForestRegressor ML predictions
- ✅ Feature importance analysis  
- ✅ 25+ technical and sentiment features
- ✅ Advanced confidence scoring
- ✅ Sentiment-enhanced predictions

#### Option B: No-sklearn Version (simplified ML)
If scikit-learn installation fails:

```batch
# Install minimal dependencies
INSTALL_MINIMAL.bat

# Run the app
python app_sentiment_no_sklearn.py
```

**Features:**
- ✅ Trend-based predictions
- ✅ All sentiment indicators work
- ✅ Technical analysis (RSI, MACD, etc.)
- ✅ Real-time market data
- ✅ No C++ compiler required

## 📊 Feature Comparison

| Feature | Full ML Version | No-sklearn Version |
|---------|----------------|-------------------|
| VIX Fear Gauge | ✅ | ✅ |
| Market Breadth | ✅ | ✅ |
| Bond Yields | ✅ | ✅ |
| Dollar Index | ✅ | ✅ |
| Sector Rotation | ✅ | ✅ |
| Technical Indicators | ✅ | ✅ |
| ML Model | RandomForest | Trend Analysis |
| Feature Importance | ✅ | ❌ |
| Prediction Confidence | Advanced | Simple |
| Min Data Required | 20 days | 20 days |

## 🔧 Troubleshooting scikit-learn Installation

### Windows Solutions (in order of preference):

1. **Use Anaconda/Miniconda** (Easiest)
   ```batch
   # After installing Anaconda
   conda install scikit-learn pandas numpy -c conda-forge
   ```

2. **Pre-compiled Wheels**
   ```batch
   pip install scikit-learn --only-binary :all:
   ```

3. **Install Visual C++ Build Tools**
   - Download: https://visualstudio.microsoft.com/downloads/
   - Select "Desktop development with C++"
   - Restart and reinstall

4. **Use No-sklearn Version**
   - Works immediately without compilation
   - All core features available

## 📁 File Descriptions

### Core Applications
- `app_enhanced_sentiment_fixed.py` - Full ML version with RandomForest
- `app_sentiment_no_sklearn.py` - Simplified version without sklearn dependency

### Installation Scripts
- `INSTALL_SKLEARN_WINDOWS.bat` - Attempts multiple methods to install sklearn
- `INSTALL_MINIMAL.bat` - Installs only essential packages (no sklearn)

### Utility Scripts
- `diagnostic_full.py` - Comprehensive system check
- `test_sentiment.py` - Test sentiment indicators

### Run Scripts
- `RUN_SENTIMENT_FINAL.bat` - Run full ML version
- `RUN_NO_SKLEARN.bat` - Run simplified version

## 🌐 API Endpoints

Both versions provide identical API endpoints:

- `/` - Web interface
- `/api/stock/<symbol>` - Get stock data with predictions
- `/api/sentiment` - Get market sentiment analysis
- `/api/sentiment/vix` - VIX fear gauge
- `/api/sentiment/breadth` - Market breadth
- `/api/sentiment/sectors` - Sector rotation

## 📈 Example API Response

```json
{
  "symbol": "AAPL",
  "current_price": 258.45,
  "predictions": [
    {
      "date": "2025-10-24",
      "predicted_price": 259.32,
      "confidence": 0.75,
      "trend": "Bullish"
    }
  ],
  "sentiment": {
    "score": 0.15,
    "sentiment": "Slightly Bullish"
  },
  "feature_importance": [
    {"feature": "macd", "importance": 0.147},
    {"feature": "rsi", "importance": 0.123}
  ]
}
```

## ✅ Verification Steps

1. **Check Installation:**
   ```python
   python diagnostic_full.py
   ```

2. **Test Sentiment:**
   ```python
   python test_sentiment.py
   ```

3. **Access Web Interface:**
   ```
   http://localhost:5000
   ```

## 🆘 Support

If you encounter issues:

1. Run `diagnostic_full.py` and note any errors
2. Check `WINDOWS_TROUBLESHOOTING.md` for solutions
3. Try the no-sklearn version as a fallback
4. The no-sklearn version works on all systems!

## 🎯 Success Indicators

You'll know everything is working when:
- ✅ Web interface loads at http://localhost:5000
- ✅ Sentiment dashboard shows live data
- ✅ Stock charts display with zoom functionality
- ✅ Predictions generate for selected stocks
- ✅ Australian stocks work with .AX suffix

---

**Package:** COMPLETE_ML_SENTIMENT_FINAL.zip
**Version:** 1.0.0
**ML Support:** Full (RandomForest) or Simplified (Trend)
**Platform:** Windows 10/11, Linux, macOS