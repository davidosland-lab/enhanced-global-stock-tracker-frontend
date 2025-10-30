# FinBERT v4.0 - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Stock Analysis Features](#stock-analysis-features)
4. [Understanding Results](#understanding-results)
5. [Advanced Features](#advanced-features)
6. [Tips and Best Practices](#tips-and-best-practices)

---

## Getting Started

### Launching the Application

**Windows 11:**
```cmd
cd C:\FinBERT_v4\FinBERT_v4.0_Windows11_Deployment
START_FINBERT_V4.bat
```

**Browser Access:**
- Automatic: Browser opens to http://127.0.0.1:5001
- Manual: Navigate to `http://127.0.0.1:5001`

### First Analysis

1. **Enter Stock Symbol** in the search box:
   - US Stocks: `AAPL`, `TSLA`, `MSFT`, `GOOGL`
   - International: `CBA.AX` (Australia), `BP.L` (UK)
   
2. **Click "Analyze Stock"** button

3. **Wait 5-30 seconds:**
   - First analysis: 20-30 seconds (downloading FinBERT model)
   - Subsequent analyses: 5-10 seconds (using cache)

4. **View Results:**
   - Price charts with candlesticks
   - Volume analysis
   - Technical indicators
   - Sentiment from news (FULL install only)
   - Price predictions

---

## Interface Overview

### Main Components

```
┌─────────────────────────────────────────────────┐
│  FinBERT v4.0 - Stock Analysis System           │
├─────────────────────────────────────────────────┤
│  [Stock Symbol: AAPL    ] [Analyze Stock]      │
├─────────────────────────────────────────────────┤
│  📊 Price Chart (Candlestick)                   │
│  ┌───────────────────────────────────────────┐ │
│  │    /\  /\      /\                         │ │
│  │   /  \/  \    /  \    /\                  │ │
│  │  /        \  /    \  /  \                 │ │
│  └───────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│  📈 Volume Chart                                │
│  ┌───────────────────────────────────────────┐ │
│  │  ||  ||    ||      ||  ||                 │ │
│  └───────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│  📊 Technical Indicators                        │
│  • SMA (20, 50): $150.25, $148.50             │
│  • RSI (14): 62.5 (Neutral)                    │
│  • MACD: 1.25 (Bullish)                        │
├─────────────────────────────────────────────────┤
│  📰 Sentiment Analysis (FULL Install Only)      │
│  • Overall: Positive (0.75)                    │
│  • Articles: 9 recent news items               │
│  • Source: Yahoo Finance, Finviz               │
├─────────────────────────────────────────────────┤
│  🔮 Price Predictions                           │
│  • Next Day: $152.30 (+1.2%)                   │
│  • 7-Day: $155.00 (+3.1%)                      │
│  • Confidence: Medium                           │
└─────────────────────────────────────────────────┘
```

### Search Bar

**Location:** Top of page

**Supported Formats:**
- Simple symbol: `AAPL`, `TSLA`, `MSFT`
- With exchange: `CBA.AX`, `BP.L`, `SAP.DE`
- Lowercase works: `aapl` → automatically converted to `AAPL`

**Invalid Symbols:**
- Empty input → Error message
- Non-existent symbol → "Symbol not found" error
- Special characters → Cleaned automatically

### Status Indicators

**Loading States:**
```
⏳ Loading... → Fetching data
⏳ Analyzing sentiment... → Scraping news (FULL only)
⏳ Generating predictions... → Running LSTM model
✅ Analysis complete! → Ready to view
❌ Error: [message] → Something went wrong
```

---

## Stock Analysis Features

### 1. Price Chart (Candlestick)

**What it shows:**
- Historical price movement over time
- Open, High, Low, Close (OHLC) for each day
- Green candles = Price increased (Close > Open)
- Red candles = Price decreased (Close < Open)

**How to read:**
```
Green Candle:           Red Candle:
    |  High                 |  High
    ▓                       |
    ▓  Close           Open ▓
    ▓                       ▓
    ▓  Open          Close  ▓
    |  Low                  |  Low
```

**Features:**
- **Zoom:** Drag to select time range
- **Reset:** Double-click to reset zoom
- **Tooltip:** Hover over candle for exact values
- **Fixed Spacing:** No overlapping candles (ECharts auto-spacing)

**Time Range:** Last 90 days by default

### 2. Volume Chart

**What it shows:**
- Trading volume for each day
- Higher bars = More shares traded
- Color matched to price movement

**Interpretation:**
- **High volume + price increase** = Strong buying interest
- **High volume + price decrease** = Strong selling pressure
- **Low volume** = Weak conviction, consolidation

**Features:**
- Synchronized with price chart (same dates)
- Hover for exact volume numbers
- Zoom capability

### 3. Technical Indicators

#### Simple Moving Average (SMA)

**What it is:** Average price over N days

**Displayed:**
- SMA(20) = 20-day moving average (short-term trend)
- SMA(50) = 50-day moving average (medium-term trend)

**How to use:**
- **Price > SMA(50)** = Uptrend (bullish)
- **Price < SMA(50)** = Downtrend (bearish)
- **SMA(20) crosses above SMA(50)** = "Golden Cross" (very bullish)
- **SMA(20) crosses below SMA(50)** = "Death Cross" (very bearish)

**Example:**
```
Current Price: $150.00
SMA(20): $148.50  → Price above short-term average ✓
SMA(50): $145.00  → Price above long-term average ✓
Signal: Strong uptrend
```

#### Relative Strength Index (RSI)

**What it is:** Momentum oscillator (0-100 scale)

**Interpretation:**
- **RSI > 70** = Overbought (possible pullback)
- **RSI 30-70** = Neutral (normal range)
- **RSI < 30** = Oversold (possible bounce)

**How to use:**
- **RSI divergence:** Price makes new high, RSI doesn't → Bearish
- **RSI trend:** Rising RSI = Strengthening momentum

**Example:**
```
RSI = 75
Status: Overbought
Action: Consider taking profits or waiting for pullback
```

#### MACD (Moving Average Convergence Divergence)

**What it is:** Trend-following momentum indicator

**Components:**
- MACD Line = 12-day EMA - 26-day EMA
- Signal Line = 9-day EMA of MACD Line
- Histogram = MACD Line - Signal Line

**Displayed:** MACD value and trend direction

**Interpretation:**
- **MACD > 0** = Bullish momentum
- **MACD < 0** = Bearish momentum
- **MACD crosses above Signal** = Buy signal
- **MACD crosses below Signal** = Sell signal

**Example:**
```
MACD: 2.35
Signal: Bullish
Histogram: Positive and growing
Interpretation: Strong upward momentum
```

### 4. Sentiment Analysis (FULL Install Only)

**What it does:**
- Scrapes recent financial news from Yahoo Finance and Finviz
- Analyzes text using FinBERT (97% accuracy financial sentiment model)
- Aggregates sentiment across all articles

**Displayed Information:**
- **Overall Sentiment Score:** -1.0 (very negative) to +1.0 (very positive)
- **Sentiment Label:** Negative, Neutral, Positive
- **Article Count:** Number of news items analyzed
- **Recent Headlines:** Top 5 headlines with individual sentiment

**Example Output:**
```
📰 Sentiment Analysis
Overall Sentiment: Positive (0.68)
Confidence: High
Articles Analyzed: 9

Recent News:
1. "Apple Reports Record Q4 Earnings" [Positive: 0.92]
2. "iPhone 15 Sales Exceed Expectations" [Positive: 0.85]
3. "Supply Chain Concerns Easing" [Neutral: 0.15]
4. "Competition Intensifies in AI Space" [Negative: -0.45]
5. "Analyst Upgrades AAPL to Buy" [Positive: 0.78]

Average: 0.68 (Positive)
```

**How it's calculated:**
1. Fetch news from multiple sources (Yahoo Finance, Finviz)
2. Filter to last 7 days
3. Run each headline through FinBERT model
4. Get sentiment score (-1 to +1) for each article
5. Average all scores for overall sentiment

**No Mock Data:**
- If no news found → Returns "No recent news" (not fake data)
- Real articles only → Genuine market sentiment
- Cached for 15 minutes → Reduces API calls

**Use Cases:**
- **Pre-earnings:** Check sentiment before earnings report
- **News events:** Gauge market reaction to announcements
- **Trend confirmation:** Positive sentiment + uptrend = Strong signal
- **Divergence detection:** Negative sentiment + rising price = Warning

### 5. Price Predictions

**What it does:**
- Uses TensorFlow LSTM (Long Short-Term Memory) neural network
- Trained on historical price data
- Incorporates sentiment analysis (FULL install)
- Considers technical indicators

**Displayed:**
- **Next Day Prediction:** Tomorrow's expected closing price
- **7-Day Prediction:** Price in one week
- **Confidence Level:** Low, Medium, High
- **Change Percentage:** Expected % gain/loss

**Example Output:**
```
🔮 Price Predictions (LSTM + Sentiment)

Next Day (2024-10-31):
  Predicted: $152.30
  Change: +$2.30 (+1.53%)
  Confidence: High

7-Day (2024-11-07):
  Predicted: $155.00
  Change: +$5.00 (+3.33%)
  Confidence: Medium

Factors:
  • Historical trend: Bullish
  • Sentiment: Positive (0.68)
  • Volume: Above average
  • Technical: MACD bullish, RSI neutral
```

**Confidence Levels:**
- **High (>80%):** Strong historical patterns, clear trend
- **Medium (50-80%):** Moderate confidence, some uncertainty
- **Low (<50%):** High volatility, weak signals

**Important Notes:**
- **Not financial advice** - Predictions are estimates only
- **Past performance ≠ future results** - Markets are unpredictable
- **Use as guidance** - Combine with other analysis
- **Risk management** - Always use stop-losses and position sizing

---

## Understanding Results

### Complete Analysis Example

**Stock:** Apple Inc. (AAPL)
**Date:** October 30, 2024

**Price Data:**
- Current: $150.00
- Day Change: +$2.50 (+1.69%)
- 52-Week High: $198.00
- 52-Week Low: $125.00

**Chart Analysis:**
```
Price Chart:
  • Pattern: Ascending triangle (bullish)
  • Resistance: $155.00 (tested 3 times)
  • Support: $145.00 (holding strong)
  • Breakout target: $165.00
  
Volume Chart:
  • Average daily volume: 50M shares
  • Recent spike: 75M shares (high interest)
  • Volume trend: Increasing on up days (bullish)
```

**Technical Indicators:**
```
SMA(20): $148.50  → Price above (bullish)
SMA(50): $145.00  → Strong uptrend confirmed
RSI(14): 62.5     → Neutral (room to run)
MACD: +1.25       → Bullish momentum
```

**Sentiment Analysis (FULL):**
```
Overall: Positive (0.68)
Sources: 9 articles from Yahoo Finance, Finviz

Key Themes:
  • Earnings beat expectations (3 articles)
  • iPhone 15 strong sales (2 articles)
  • AI features driving upgrades (2 articles)
  • Supply chain improving (1 article)
  • Analyst upgrades (1 article)
  
Sentiment Distribution:
  Positive: 7 articles (78%)
  Neutral: 1 article (11%)
  Negative: 1 article (11%)
```

**Predictions:**
```
Next Day: $152.30 (+1.53%) - Confidence: High
  Reasoning: Bullish technicals + positive sentiment

7-Day: $155.00 (+3.33%) - Confidence: Medium
  Reasoning: Approaching resistance, may consolidate
  
Risk Factors:
  • Resistance at $155.00 (3 failed breakouts)
  • Market-wide volatility possible
  • Earnings season unpredictability
```

**Trading Signals:**
```
Buy Signal Strength: 7/10
  ✓ Price above SMA(50)
  ✓ MACD bullish
  ✓ Positive sentiment
  ✓ Volume increasing
  ✗ RSI approaching overbought
  ✗ Near resistance level
  
Suggested Action:
  • Entry: $149.00-$151.00 (current range)
  • Target: $165.00 (breakout target)
  • Stop Loss: $144.00 (below support)
  • Risk/Reward: 1:2.5 (favorable)
```

### Interpreting Conflicting Signals

**Scenario 1: Positive Sentiment + Bearish Technicals**
```
Sentiment: Positive (0.75)
MACD: Negative (-1.5)
RSI: 35 (oversold)

Interpretation:
  • Market overreacted to temporary bad news
  • Fundamental outlook remains positive
  • Technical bounce likely (oversold conditions)
  • Action: Look for entry on bounce

Example: TSLA after delivery miss but strong guidance
```

**Scenario 2: Negative Sentiment + Bullish Technicals**
```
Sentiment: Negative (-0.60)
MACD: Positive (+2.0)
RSI: 68 (near overbought)

Interpretation:
  • Market ignoring negative news
  • Strong technical momentum
  • Possible disconnect (caution)
  • Action: Wait for confirmation or pullback

Example: Stock rallying despite CEO scandal (momentum trade)
```

**Scenario 3: All Signals Aligned**
```
Sentiment: Positive (0.80)
MACD: Bullish (+2.5)
RSI: 60 (neutral)
Price: Above all SMAs

Interpretation:
  • High conviction setup
  • All factors confirming trend
  • Best risk/reward opportunity
  • Action: Enter with confidence

Example: Post-earnings beat with raised guidance
```

---

## Advanced Features

### Custom Configuration

Edit `config_dev.py` for advanced options:

```python
# Technical Indicator Settings
SMA_SHORT = 20    # Change short-term SMA period
SMA_LONG = 50     # Change long-term SMA period
RSI_PERIOD = 14   # Change RSI calculation period

# Data Settings
LOOKBACK_DAYS = 90     # Historical data period
CACHE_EXPIRY = 900     # Cache duration (seconds)

# Prediction Settings
LSTM_EPOCHS = 50       # Training iterations (more = slower but better)
LSTM_BATCH_SIZE = 32   # Training batch size
SEQUENCE_LENGTH = 60   # Days of history for prediction

# Sentiment Settings
NEWS_DAYS = 7          # How many days of news to analyze
MIN_ARTICLES = 3       # Minimum articles for valid sentiment
```

### Batch Analysis Mode

Analyze multiple stocks sequentially:

```python
# Create custom script: batch_analyze.py
stocks = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']
results = {}

for symbol in stocks:
    print(f"Analyzing {symbol}...")
    # Call analysis function
    results[symbol] = analyze_stock(symbol)
    
# Export to CSV
import pandas as pd
df = pd.DataFrame(results).T
df.to_csv('batch_analysis_results.csv')
```

### Export Data

Access raw data for further analysis:

```python
# In Python console or custom script
from app_finbert_v4_dev import FinBERTStockAnalyzer

analyzer = FinBERTStockAnalyzer()
data = analyzer.analyze_stock('AAPL')

# Export price data
import pandas as pd
price_df = pd.DataFrame(data['historical_data'])
price_df.to_csv('aapl_prices.csv', index=False)

# Export sentiment data
sentiment_df = pd.DataFrame(data['sentiment'])
sentiment_df.to_csv('aapl_sentiment.csv', index=False)
```

### API Mode (Programmatic Access)

Use Flask API endpoints directly:

```python
import requests

# Analyze stock
response = requests.post('http://127.0.0.1:5001/analyze', 
                         json={'symbol': 'AAPL'})
data = response.json()

# Get predictions
predictions = data['predictions']
print(f"Next day: ${predictions['next_day']:.2f}")
```

---

## Tips and Best Practices

### For Beginners

1. **Start with well-known stocks:** AAPL, MSFT, TSLA
2. **Focus on one indicator:** Start with SMA crossovers
3. **Understand sentiment:** Read the actual news articles
4. **Don't overtrade:** Use predictions as guidance, not gospel
5. **Learn gradually:** Master basics before advanced features

### For Intermediate Users

1. **Combine multiple signals:** Technical + Sentiment + Fundamental
2. **Look for divergences:** Price vs sentiment disconnects
3. **Monitor volume:** Confirms price movement validity
4. **Use stop losses:** Protect capital with RSI levels
5. **Track prediction accuracy:** Note when predictions are right/wrong

### For Advanced Users

1. **Custom indicators:** Modify config for personal strategy
2. **Backtesting:** Export data and test strategies historically
3. **Correlation analysis:** Compare predictions across sectors
4. **Sentiment deep dive:** Analyze individual article themes
5. **Model tuning:** Adjust LSTM parameters for your style

### Common Mistakes to Avoid

**❌ Trusting predictions blindly**
- Predictions are probabilistic, not guarantees
- Always use risk management (stops, position sizing)

**❌ Ignoring sentiment context**
- Read the actual headlines, not just the score
- Context matters: "Beat expectations" vs "Beat lowered expectations"

**❌ Overtrading on noise**
- Don't react to every tiny price movement
- Focus on significant signals and trends

**❌ Analysis paralysis**
- Too many indicators can be confusing
- Keep it simple: 2-3 key indicators + sentiment

**❌ Not considering market conditions**
- Individual stock analysis should consider broader market
- Bull market → More bullish, Bear market → More cautious

### Best Workflow

**Step 1: Screening (Find Candidates)**
- Run analysis on watchlist
- Filter by positive sentiment + bullish technicals

**Step 2: Deep Dive (Validate)**
- Review charts for patterns
- Read actual news articles
- Check volume and momentum

**Step 3: Planning (Set Levels)**
- Entry: Current price or specific level
- Target: Resistance or prediction
- Stop: Support or % below entry

**Step 4: Execution (Trade)**
- Enter position with defined risk
- Monitor sentiment for changes
- Adjust stops as price moves

**Step 5: Review (Learn)**
- Track prediction accuracy
- Note what worked and didn't
- Refine strategy over time

---

## Example Workflows

### Swing Trading Workflow

**Goal:** Hold 3-7 days for 5-10% gain

**Steps:**
1. Find stock with positive sentiment + bullish MACD
2. Wait for pullback to SMA(20)
3. Enter when RSI < 50 (not overbought)
4. Target: Next resistance or 7-day prediction
5. Stop: Below SMA(50)

**Example:**
```
AAPL Analysis:
  • Sentiment: Positive (0.75)
  • MACD: Bullish (+2.0)
  • Price: $150, pulled back to SMA(20) = $148
  • RSI: 45 (neutral, not overbought)
  
Action:
  • Enter: $148-$150
  • Target: $165 (resistance)
  • Stop: $144 (below SMA(50))
  • Risk: $6 per share
  • Reward: $15 per share
  • R:R = 1:2.5 ✓
```

### Earnings Play Workflow

**Goal:** Capitalize on pre-earnings sentiment

**Steps:**
1. Analyze 1-2 weeks before earnings
2. Check sentiment trend (improving vs deteriorating)
3. Look for analyst upgrades (positive sentiment spikes)
4. Enter if sentiment positive + price consolidating
5. Exit before earnings (avoid event risk)

**Example:**
```
TSLA Pre-Earnings (5 days before):
  • Sentiment: Improving (0.60 → 0.75 over 3 days)
  • News: "Delivery numbers beat estimates"
  • Price: Consolidating at $250 (low volatility)
  • RSI: 55 (neutral, room to run)
  
Action:
  • Enter: $250
  • Target: $270 (pre-earnings high)
  • Exit: Day before earnings (lock gains)
  • Stop: $240 (10% risk acceptable for 8% reward)
```

### Long-Term Investment Workflow

**Goal:** Buy and hold for months/years

**Steps:**
1. Check fundamental health (not just technicals)
2. Sentiment should be positive or improving
3. Price above SMA(50) for uptrend confirmation
4. Buy on pullbacks (RSI < 40)
5. Hold through volatility, focus on trend

**Example:**
```
MSFT Long-Term:
  • Sentiment: Consistently positive (0.65-0.80 range)
  • Price: Above SMA(200) for 2 years (strong uptrend)
  • Business: Cloud growth, AI leadership
  • Current: $380, RSI = 38 (oversold on pullback)
  
Action:
  • Enter: $380 (pullback opportunity)
  • Target: None (hold for trend)
  • Stop: Below $350 (major support break)
  • Review quarterly: Check if sentiment deteriorates
```

---

## Keyboard Shortcuts

**Search Bar:**
- `Tab` - Jump to search input
- `Enter` - Trigger analysis
- `Esc` - Clear input

**Charts:**
- `Click + Drag` - Zoom to selection
- `Double Click` - Reset zoom
- `Hover` - Show tooltip
- `Scroll` - Zoom in/out (when mouse over chart)

**Browser:**
- `F5` - Refresh page
- `Ctrl + F5` - Hard refresh (clear cache)
- `F12` - Open developer console (troubleshooting)

---

## Troubleshooting

See **TROUBLESHOOTING.md** for detailed solutions to common issues.

**Quick Fixes:**

- **Charts not loading:** Refresh page (F5)
- **Slow analysis:** First run downloads models (be patient)
- **No sentiment data:** Stock may have limited news coverage
- **Connection refused:** Restart server with START_FINBERT_V4.bat

---

## Next Steps

1. **Practice:** Analyze different stocks across sectors
2. **Learn patterns:** Note common price/sentiment relationships
3. **Track performance:** Keep log of predictions vs actual
4. **Refine strategy:** Adjust based on what works for you
5. **Stay updated:** Check for FinBERT v4.x updates

**Happy Analyzing!** 📈🚀
