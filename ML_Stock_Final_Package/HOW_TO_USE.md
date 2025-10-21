# How to Use the ML Stock Predictor

## 🌍 Supported Markets

### US Stocks
- **Format:** Just use the ticker symbol
- **Examples:** AAPL, MSFT, GOOGL, AMZN, TSLA
- **Data Source:** Yahoo Finance ✅, Alpha Vantage ✅

### Australian Stocks (ASX)
- **Format:** Add `.AX` suffix
- **Examples:** 
  - CBA.AX (Commonwealth Bank)
  - BHP.AX (BHP Group)
  - CSL.AX (CSL Limited)
  - WBC.AX (Westpac)
  - ANZ.AX (ANZ Bank)
  - RIO.AX (Rio Tinto)
  - WOW.AX (Woolworths)
  - WES.AX (Wesfarmers)
- **Data Source:** Yahoo Finance ✅

### Other International Markets
- **UK:** `.L` suffix (e.g., BP.L, HSBA.L)
- **Germany:** `.DE` suffix (e.g., BMW.DE, SAP.DE)
- **Hong Kong:** `.HK` suffix (e.g., 0005.HK)
- **Japan:** `.T` suffix (e.g., 7203.T for Toyota)
- **Canada:** `.TO` suffix (e.g., RY.TO for Royal Bank)

## 📊 Getting Predictions

### Method 1: Web Interface
1. Open http://localhost:8000
2. Go to "Market Data" tab
3. Enter symbol (e.g., CBA.AX for Commonwealth Bank)
4. Fetch data and view real-time prices
5. Train model and generate predictions

### Method 2: Command Line
```bash
# US Stock
python3 universal_predictor.py AAPL 2

# Australian Stock
python3 universal_predictor.py CBA.AX 2

# Any symbol with custom months
python3 universal_predictor.py BHP.AX 3
```

## 📈 What You Get

For each stock analysis:
- **Current Price** in local currency
- **Technical Indicators:**
  - Moving Averages (20, 50, 200 day)
  - RSI (Relative Strength Index)
  - MACD trend
  - Bollinger Band position
  - Annual volatility
- **Performance Metrics:**
  - 30-day return
  - 90-day return
  - 52-week range position
- **Predictions:**
  - Monthly targets up to 6 months
  - Expected return percentages
  - Price ranges (low/high)
  - Confidence scores
- **Support/Resistance Levels**

## 🎯 Example Output

### Apple (AAPL) - US Stock
```
Current Price: $252.29
1-Month Target: $264.90 (+5.0%)
2-Month Target: $277.52 (+10.0%)
Confidence: 90%
```

### Commonwealth Bank (CBA.AX) - Australian Stock
```
Current Price: AUD $172.70
1-Month Target: AUD $182.03 (+5.4%)
2-Month Target: AUD $191.35 (+10.8%)
Confidence: 85%
```

## 🔧 Technical Details

The system uses:
1. **35+ Technical Indicators**
2. **Machine Learning Models** (when trained)
3. **Real-time data** from Yahoo Finance
4. **Automatic currency detection**
5. **Market-specific adjustments**

## ⚠️ Important Notes

- Australian stocks typically show higher volatility
- Predictions adjust for local market conditions
- All prices shown in local currency (AUD for .AX, USD for US)
- Confidence scores reflect data quality and trend strength

## 🚀 Quick Start Commands

```bash
# Start the system
python3 unified_system.py

# Get prediction for any stock
python3 universal_predictor.py [SYMBOL] [MONTHS]

# Examples
python3 universal_predictor.py MSFT 3      # Microsoft, 3 months
python3 universal_predictor.py BHP.AX 2    # BHP Australia, 2 months
python3 universal_predictor.py BP.L 1      # BP London, 1 month
```