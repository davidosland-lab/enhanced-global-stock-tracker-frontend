# US Market Screening Pipeline

Complete stock screening pipeline for US markets (NYSE/NASDAQ), designed to mirror the ASX pipeline architecture while incorporating US market-specific characteristics.

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Components](#components)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Features](#features)
- [Output](#output)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The US Market Screening Pipeline is a comprehensive overnight stock screening system that:

- **Screens 240 US stocks** across 8 major sectors
- **Analyzes market sentiment** using S&P 500, VIX, and other indices
- **Detects market regimes** using HMM-based crash risk analysis
- **Generates predictions** using LSTM models
- **Scores opportunities** based on technical, fundamental, and sentiment analysis
- **Produces morning reports** with top trading opportunities

### Key Differences from ASX Pipeline

| Feature | ASX Pipeline | US Pipeline |
|---------|-------------|-------------|
| Primary Index | ^AXJO (ASX 200) | ^GSPC (S&P 500) |
| Volatility Index | N/A | ^VIX (CBOE VIX) |
| Market Hours | 10:00-16:00 AEST | 09:30-16:00 ET |
| Ticker Format | XXX.AX | XXX |
| Min Market Cap | $500M AUD | $2B USD |
| Min Volume | 500K shares | 1M shares |
| Total Stocks | 240 | 240 |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Launcher                          │
│                  (run_screening.py)                          │
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
       ┌───────▼────────┐         ┌───────▼────────┐
       │  ASX Pipeline  │         │  US Pipeline   │
       └────────────────┘         └───┬────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
        ┌───────────▼──────────┐          ┌────────────▼───────────┐
        │  US Market Monitor   │          │  US Stock Scanner      │
        │  (S&P 500, VIX)      │          │  (240 stocks, 8 sectors)│
        └──────────────────────┘          └────────────────────────┘
                    │                                   │
        ┌───────────▼──────────┐          ┌────────────▼───────────┐
        │ US Regime Engine     │          │  Batch Predictor       │
        │ (HMM-based)          │          │  (LSTM predictions)    │
        └──────────────────────┘          └────────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                          ┌───────────▼───────────┐
                          │  Opportunity Scorer   │
                          └───────────┬───────────┘
                                      │
                          ┌───────────▼───────────┐
                          │  Report Generator     │
                          └───────────────────────┘
```

---

## 🧩 Components

### 1. US Market Monitor (`us_market_monitor.py`)

Tracks US market sentiment and indices:

- **S&P 500 (^GSPC)** - Primary market indicator
- **VIX (^VIX)** - Volatility/fear index
- **Dow Jones (^DJI)** - Industrial average
- **NASDAQ (^IXIC)** - Technology index

**Key Metrics:**
- Day/week price changes
- Moving averages (20-day, 50-day)
- Market sentiment (Bullish/Neutral/Bearish)
- VIX interpretation (complacency to fear)

### 2. US Stock Scanner (`us_stock_scanner.py`)

Scans 240 US stocks across 8 sectors:

**Sectors:**
1. Financials (JPM, BAC, WFC, etc.)
2. Materials (LIN, APD, SHW, etc.)
3. Healthcare (UNH, JNJ, LLY, etc.)
4. Technology (AAPL, MSFT, NVDA, etc.)
5. Energy (XOM, CVX, COP, etc.)
6. Industrials (BA, HON, UPS, etc.)
7. Consumer_Discretionary (AMZN, HD, MCD, etc.)
8. Consumer_Staples (PG, KO, PEP, etc.)

**Selection Criteria:**
- Price range: $5 - $1,000
- Min volume: 1M shares/day
- Min market cap: $2B
- Beta range: 0.5 - 2.5

### 3. US Market Regime Engine (`us_market_regime_engine.py`)

HMM-based market regime classifier:

**States:**
- **Low Volatility** (Bull Market) - VIX < 15%, stable growth
- **Medium Volatility** (Normal Market) - VIX 15-25%, healthy volatility
- **High Volatility** (Bear/Crash Market) - VIX > 25%, elevated risk

**Outputs:**
- Current regime state
- Crash risk score (0-100%)
- State probabilities
- Volatility metrics

### 4. US Overnight Pipeline (`us_overnight_pipeline.py`)

Main orchestrator coordinating all components:

**Pipeline Phases:**
1. **Market Sentiment** (10%) - Fetch S&P 500, VIX data
2. **Regime Analysis** (15%) - Classify market state
3. **Stock Scanning** (20%) - Screen 240 stocks
4. **Event Risk** (35%) - Check earnings, SEC filings
5. **Predictions** (50%) - LSTM price predictions
6. **Scoring** (70%) - Opportunity ranking
7. **Report** (85%) - Generate morning report
8. **Finalization** (100%) - Save results, export CSV

---

## 💿 Installation

### Prerequisites

```bash
Python 3.8+
pip (Python package manager)
```

### Required Dependencies

```bash
# Core dependencies
pip install yahooquery pandas numpy

# Machine learning
pip install scikit-learn hmmlearn

# Optional: LSTM predictions
pip install tensorflow keras

# Optional: Visualization
pip install matplotlib plotly
```

### Quick Install

```bash
# Install all dependencies
cd /home/user/webapp
pip install -r requirements.txt

# Verify installation
python -c "from models.screening.us_stock_scanner import USStockScanner; print('✓ US Pipeline ready')"
```

---

## 🚀 Usage

### Option 1: Run US Pipeline Only

```bash
# Run US market screening
python run_screening.py --market us

# Run with custom settings
python run_screening.py --market us --stocks 40 --sectors Technology,Healthcare
```

### Option 2: Run Both Markets

```bash
# Run ASX and US sequentially
python run_screening.py --market both

# Run ASX and US in parallel (faster)
python run_screening.py --market both --parallel
```

### Option 3: Direct Module Execution

```bash
# Run US pipeline directly
cd models/screening
python us_overnight_pipeline.py

# Test individual components
python us_market_monitor.py
python us_stock_scanner.py
python us_market_regime_engine.py
```

### Command-Line Options

```bash
--market {asx, us, both, all}   # Which market(s) to screen
--stocks NUM                     # Stocks per sector (default: 30)
--sectors LIST                   # Comma-separated sectors
--parallel                       # Parallel execution (for both/all)
```

---

## ⚙️ Configuration

### Market Configuration (`us_market_config.py`)

Edit configuration parameters:

```python
# Market hours (Eastern Time)
MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)

# Selection criteria
SELECTION_CRITERIA = {
    "min_market_cap": 2_000_000_000,  # $2B
    "min_avg_volume": 1_000_000,       # 1M shares
    "min_price": 5.00,
    "max_price": 1000.00
}

# Risk thresholds
REGIME_SETTINGS = {
    "crash_threshold": 0.30  # 30% crash risk threshold
}
```

### Sectors Configuration (`us_sectors.json`)

Customize sector stocks:

```json
{
  "sectors": {
    "Technology": {
      "weight": 1.4,
      "stocks": ["AAPL", "MSFT", "NVDA", ...]
    }
  }
}
```

---

## ✨ Features

### Market Sentiment Analysis

- ✅ Real-time S&P 500 tracking
- ✅ VIX fear/greed analysis
- ✅ Multi-index agreement scoring
- ✅ Market mood interpretation

### Technical Analysis

- ✅ RSI (Relative Strength Index)
- ✅ Moving averages (20-day, 50-day)
- ✅ Volatility metrics
- ✅ Volume analysis

### Market Regime Detection

- ✅ HMM-based state classification
- ✅ Crash risk scoring
- ✅ Volatility regime tracking
- ✅ Probabilistic state estimates

### Opportunity Scoring

- ✅ Multi-factor scoring (0-100)
- ✅ Sector weighting
- ✅ Sentiment integration
- ✅ Regime-aware adjustments

### Event Risk Protection

- ✅ Earnings blackout detection
- ✅ SEC filing monitoring
- ✅ FOMC meeting awareness
- ✅ Sit-out recommendations

---

## 📊 Output

### Directory Structure

```
/home/user/webapp/
├── reports/us/                  # HTML morning reports
├── logs/screening/us/           # Pipeline execution logs
└── data/us/                     # JSON results, CSV exports
```

### Morning Report Contents

- **Executive Summary**
  - Market overview (S&P 500, VIX)
  - Regime analysis
  - Top 20 opportunities
  
- **Market Analysis**
  - Sentiment indicators
  - Crash risk assessment
  - Volatility metrics
  
- **Stock Opportunities**
  - Ranked by score
  - Technical indicators
  - Prediction targets
  - Event risk warnings

### JSON Output Example

```json
{
  "market": "US",
  "timestamp": "2025-11-21T07:00:00-05:00",
  "total_stocks": 240,
  "sentiment": {
    "overall": {
      "sentiment": "Bullish",
      "score": 72.5
    },
    "sp500": {
      "price": 4750.32,
      "day_change": 0.85
    },
    "vix": {
      "current_vix": 14.2,
      "level": "Low"
    }
  },
  "regime": {
    "regime_label": "low_vol",
    "crash_risk_score": 0.12
  },
  "top_opportunities": [...]
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'yahooquery'
pip install yahooquery

# Error: No module named 'hmmlearn'
pip install hmmlearn
```

#### 2. Data Fetch Failures

```bash
# Check internet connection
ping yahoo.com

# Test data fetch manually
python -c "from yahooquery import Ticker; print(Ticker('^GSPC').history(period='1d'))"
```

#### 3. Insufficient Data

- **Issue**: Not enough historical data for analysis
- **Solution**: Increase lookback period in config

```python
# us_market_regime_engine.py
lookback_days = 365  # Increase from 252
```

#### 4. Memory Issues

```bash
# Reduce batch size
python run_screening.py --market us --stocks 20

# Run one sector at a time
python run_screening.py --market us --sectors Technology
```

### Debug Mode

Enable detailed logging:

```python
# In us_overnight_pipeline.py
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. Check logs: `logs/screening/us/us_overnight_pipeline.log`
2. Review error state: `logs/screening/us/errors/`
3. Test components individually
4. Verify configuration files

---

## 📈 Performance

### Expected Execution Times

| Phase | Duration | Notes |
|-------|----------|-------|
| Market Sentiment | 10-20s | S&P 500, VIX, indices |
| Regime Analysis | 20-30s | HMM fitting |
| Stock Scanning | 5-10min | 240 stocks, rate-limited |
| Predictions | 2-5min | LSTM inference |
| Scoring | 1-2min | Multi-factor analysis |
| Report Gen | 30-60s | HTML generation |
| **Total** | **~15-20min** | Full pipeline |

### Optimization Tips

1. **Parallel Execution**: Use `--parallel` for both markets
2. **Reduce Stocks**: Use `--stocks 20` for faster testing
3. **Cache Data**: Enable data caching (future enhancement)
4. **Sector Focus**: Screen high-priority sectors only

---

## 🔄 Scheduling

### Run Daily Before Market Open

```bash
# Cron job (7 AM ET, before market opens at 9:30 AM)
0 7 * * 1-5 cd /home/user/webapp && python run_screening.py --market us

# Both markets
0 6 * * 1-5 cd /home/user/webapp && python run_screening.py --market both
```

### Windows Task Scheduler

```bash
# Create batch file: run_us_screening.bat
@echo off
cd C:\path\to\webapp
python run_screening.py --market us
pause

# Schedule daily at 7 AM
# Task Scheduler > Create Basic Task > Daily > 7:00 AM > Start Program > run_us_screening.bat
```

---

## 📚 Additional Resources

### Related Documentation

- [ASX Pipeline Documentation](./ASX_PIPELINE_README.md)
- [Event Risk Guard Guide](./EVENT_RISK_GUARD_GUIDE.md)
- [Market Regime Engine Technical Spec](./MARKET_REGIME_ENGINE.md)

### API Reference

- [yahooquery Documentation](https://yahooquery.dpguthrie.com/)
- [hmmlearn Documentation](https://hmmlearn.readthedocs.io/)

---

## 📝 Changelog

### v1.0.0 (2025-11-21)

- ✅ Initial release
- ✅ 240 US stocks across 8 sectors
- ✅ S&P 500 and VIX sentiment analysis
- ✅ HMM-based regime detection
- ✅ Unified launcher for ASX + US
- ✅ Complete documentation

---

## 🎯 Future Enhancements

- [ ] Options market data integration
- [ ] Sector rotation analysis
- [ ] Fed policy impact modeling
- [ ] Earnings surprise prediction
- [ ] Real-time intraday monitoring
- [ ] Multi-timeframe analysis
- [ ] Portfolio optimization
- [ ] Risk parity weighting

---

## 📄 License

This project is for educational and research purposes. Use at your own risk. Not financial advice.

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: 2025-11-21  
**Maintainer**: Event Risk Guard Team
