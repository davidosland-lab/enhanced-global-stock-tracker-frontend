# FinBERT v4.0 - User Guide

## Getting Started

### Launch Application
```cmd
START_FINBERT_V4.bat
```
Browser opens to http://127.0.0.1:5001

### Analyze a Stock
1. Enter stock symbol (e.g., AAPL, TSLA, MSFT)
2. Click "Analyze Stock"
3. Wait 5-10 seconds
4. View results

## Features (FULL Install)

### Real Sentiment Analysis
- ProsusAI/finbert model (97% accuracy)
- Yahoo Finance + Finviz news
- Article-level sentiment scores
- NO MOCK DATA

### LSTM Predictions
- TensorFlow neural networks
- Next-day forecasts
- 7-day predictions
- Confidence levels

### Fixed Charts
- ECharts candlesticks (no overlapping!)
- Volume bars
- Interactive tooltips
- Zoom and pan

### Technical Indicators
- SMA (20, 50) - Moving averages
- RSI (14) - Relative strength
- MACD - Momentum

## Recommended Stocks

**Good news coverage:**
- AAPL, TSLA, MSFT, GOOGL, AMZN
- NVDA, META, NFLX

**Limited news (expected):**
- Small caps, international stocks
- Returns empty (not fake data)

## Performance

**First run:** 20-30 seconds (downloads FinBERT model)
**Cached:** 5-10 seconds
**News scraping:** 2-3 seconds per source

For troubleshooting, see README.md
