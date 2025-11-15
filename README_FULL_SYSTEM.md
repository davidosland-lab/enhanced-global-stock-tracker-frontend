# FinBERT v4.4.4 - COMPLETE SYSTEM DEPLOYMENT

## 🎉 What's Included

This is the **COMPLETE SYSTEM** with all advanced features:

### 🧠 Machine Learning Components
- ✅ **LSTM Neural Network** (45% ensemble weight)
  - TensorFlow/Keras implementation
  - Trained on historical stock data
  - Predicts next-day price direction
  - Location: `finbert_v4.4.4/lstm_predictor.py`

- ✅ **FinBERT Sentiment Analysis** (15% ensemble weight)
  - Transformer-based sentiment analysis
  - Real news from Yahoo Finance + Finviz
  - Financial text understanding
  - Location: `finbert_v4.4.4/finbert_sentiment.py`

### 📊 Analysis Components
- ✅ **Trend Analysis** (25% ensemble weight)
- ✅ **Technical Analysis** (15% ensemble weight)
- ✅ **SPI 200 Futures Monitoring**
- ✅ **US Market Integration** (S&P 500, Nasdaq, Dow)
- ✅ **Gap Prediction**
- ✅ **Market Sentiment Scoring**

### 🔄 Two Scanning Modes

#### Mode 1: Quick Technical Scanner (yahooquery)
**Purpose**: Fast technical screening for stock filtering
**Runtime**: 5-10 minutes for all sectors
**Analysis**: Technical indicators only (no ML predictions)

**Run**:
```bash
# Windows
RUN_ALL_SECTORS_YAHOOQUERY.bat

# Or Python directly
python run_all_sectors_yahooquery.py
```

#### Mode 2: Full Overnight Pipeline (LSTM + Sentiment)
**Purpose**: Comprehensive ML-based predictions
**Runtime**: 30-60 minutes (depends on stock count)
**Analysis**: Full ensemble with LSTM + Sentiment + All features

**Run**:
```bash
# Windows
RUN_OVERNIGHT_PIPELINE.bat

# Or Python directly
python models/screening/overnight_pipeline.py
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r finbert_v4.4.4/requirements.txt
```

**Key Dependencies**:
- yahooquery (for reliable data fetching)
- tensorflow (for LSTM predictions)
- transformers (for FinBERT sentiment)
- pandas, numpy (data processing)

### Step 2: Configure Alpha Vantage API Key (Optional)
If using Alpha Vantage data source:
1. Get free API key from https://www.alphavantage.co/
2. Set environment variable: `ALPHA_VANTAGE_API_KEY=your_key_here`

### Step 3: Choose Your Scanning Mode

**For Quick Technical Screening**:
```bash
RUN_ALL_SECTORS_YAHOOQUERY.bat
```

**For Full ML Predictions**:
```bash
RUN_OVERNIGHT_PIPELINE.bat
```

---

## 📊 System Architecture

### Ensemble Prediction Weights:
```
LSTM Neural Network:    45%  (highest priority)
Trend Analysis:         25%
Technical Analysis:     15%
Sentiment Analysis:     15%
───────────────────────────
Total:                 100%
```

### Data Flow:
```
1. Stock Scanner → Validates and filters stocks
2. SPI Monitor → Gets market sentiment
3. Batch Predictor → Runs ensemble predictions
   ├─ LSTM Predictor (45%)
   ├─ Trend Analyzer (25%)
   ├─ Technical Analyzer (15%)
   └─ Sentiment Analyzer (15%)
4. Opportunity Scorer → Ranks stocks by score
5. Report Generator → Creates reports
```

---

## ⏰ Optimal Scheduling

### Recommendation: 3:45 PM AEST (Before Market Close)

**Why This Time?**
- ✅ Captures complete ASX trading day
- ✅ Gets all daily news sentiment
- ✅ Before US markets open (11:30 PM AEST)
- ✅ More relevant for next-day predictions

**Windows Task Scheduler**:
```batch
schtasks /create /tn "Stock Overnight Pipeline" ^
  /tr "C:\path\to\RUN_OVERNIGHT_PIPELINE.bat" ^
  /sc weekdays /st 15:45
```

**Linux Cron**:
```bash
45 15 * * 1-5 cd /path/to/project && python models/screening/overnight_pipeline.py
```

---

## 📁 Key Files

### Screening Modules
- `models/screening/stock_scanner.py` - Stock validation & technical analysis
- `models/screening/spi_monitor.py` - SPI 200 futures & US markets
- `models/screening/batch_predictor.py` - Ensemble prediction engine
- `models/screening/overnight_pipeline.py` - Main orchestrator

### FinBERT Components
- `finbert_v4.4.4/lstm_predictor.py` - Neural network predictions
- `finbert_v4.4.4/finbert_sentiment.py` - Sentiment analysis
- `finbert_v4.4.4/news_sentiment_real.py` - News scraping

### Configuration
- `models/config/asx_sectors.json` - Sector definitions (8 sectors)
- `models/config/screening_config.json` - Screening parameters

### Runners
- `RUN_OVERNIGHT_PIPELINE.bat` - Full system runner
- `RUN_ALL_SECTORS_YAHOOQUERY.bat` - Quick technical scanner

---

## 🎯 Expected Output

### Quick Scanner Output
**File**: `screener_results_yahooquery_[timestamp].csv`

**Columns**:
- symbol, name, price, volume
- sector, score (0-100)
- technical indicators (RSI, MA, volatility)

### Overnight Pipeline Output
**Files**:
- `overnight_report_[date].html` - Visual report
- `predictions_[date].csv` - Full predictions with LSTM
- `sentiment_scores_[date].csv` - Sentiment analysis
- `top_opportunities_[date].csv` - Ranked opportunities

**Additional Data**:
- LSTM prediction confidence
- Sentiment scores (positive/negative/neutral)
- SPI 200 gap prediction
- US market influence score
- Ensemble final score (0-100)

---

## 🐛 Troubleshooting

### LSTM Not Available
**Issue**: "LSTM models not found"
**Solution**: 
1. Check `finbert_v4.4.4/lstm_models/` directory exists
2. Ensure TensorFlow is installed: `pip install tensorflow`
3. System will fall back to other prediction methods

### Sentiment Analysis Issues
**Issue**: "FinBERT not available"
**Solution**:
1. Install transformers: `pip install transformers torch`
2. Check internet connection (for news scraping)
3. System will use fallback keyword-based sentiment

### Unicode Errors on Windows
**Solution**: Use Windows-compatible versions:
```bash
RUN_ALL_SECTORS_YAHOOQUERY_WINDOWS.bat
```

---

## 📊 Performance Expectations

### Quick Scanner (Technical Only)
- **Stocks**: 250-300 (all sectors)
- **Runtime**: 5-10 minutes
- **Success Rate**: 90-100%
- **Output**: Technical scores

### Full Pipeline (LSTM + Sentiment)
- **Stocks**: 50-100 (top opportunities)
- **Runtime**: 30-60 minutes
- **Success Rate**: 80-95%
- **Output**: ML predictions + sentiment + scores

---

## 📚 Documentation

- **STOCK_ANALYSIS_EXPLAINED.md** - Complete analysis breakdown
- **YAHOOQUERY_INTEGRATION_COMPLETE.md** - yahooquery implementation
- **DEPLOYMENT_README_YAHOOQUERY.md** - Deployment guide
- **UNICODE_FIX_README.md** - Windows encoding fixes

---

## 🏆 System Comparison

| Feature | Quick Scanner | Full Pipeline |
|---------|--------------|---------------|
| LSTM Predictions | ❌ | ✅ 45% weight |
| FinBERT Sentiment | ❌ | ✅ 15% weight |
| Real News Data | ❌ | ✅ Yahoo + Finviz |
| SPI 200 Futures | ❌ | ✅ Yes |
| US Markets | ❌ | ✅ S&P, Nasdaq, Dow |
| Technical Analysis | ✅ | ✅ 15% weight |
| Trend Analysis | ❌ | ✅ 25% weight |
| Speed | Fast (10 min) | Slower (60 min) |
| Purpose | Screening | Predictions |

---

## 💡 Usage Recommendations

### For Daily Quick Screening
Use the **yahooquery scanner**:
- Fast technical filtering
- Identify liquid, stable stocks
- Good for initial screening

### For Overnight Predictions
Use the **full pipeline**:
- Comprehensive ML analysis
- LSTM price predictions
- Sentiment-informed decisions
- Best run at 3:45 PM AEST

### For Both
Run technical scanner daily (10 min)
Run full pipeline overnight (60 min)
Combine results for best decisions

---

## 🔐 Security Notes

- Alpha Vantage API key should be in environment variable
- News scraping respects robots.txt
- No personal data collected
- All processing is local

---

## 📞 Support

For issues or questions:
1. Check documentation files
2. Review STOCK_ANALYSIS_EXPLAINED.md
3. Check log files in project directory

---

**Version**: v4.4.4 with yahooquery integration
**Date**: 2025-11-11
**Status**: Production Ready

Full documentation available in included markdown files.
