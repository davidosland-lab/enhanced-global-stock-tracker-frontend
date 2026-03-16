# 🔍 Backtest Sentiment Analysis: What Data Is Used?

**Question**: *"What sentiment is the backtest using. Historical?"*

**Short Answer**: **NO SENTIMENT DATA IS USED AT ALL** ❌

---

## 📊 What the Backtest ACTUALLY Uses

### Ensemble Model (Default) Combines:

**1. LSTM (40% weight)**:
- Pattern recognition from price history
- Trend continuation analysis
- Uses last 60 days of price data

**2. Technical Analysis (35% weight)**:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Moving Averages (SMA 20, SMA 50, EMA 12, EMA 26)
- Volatility calculations

**3. Momentum (25% weight)**:
- Price momentum
- Rate of change
- Trend strength

### Data Sources:
✅ **Historical price data** (OHLCV - Open, High, Low, Close, Volume)  
✅ **Technical indicators** (calculated from price)  
✅ **Price patterns** (LSTM learns from past movements)  
❌ **NO sentiment data**  
❌ **NO news data**  
❌ **NO FinBERT sentiment**  
❌ **NO social media sentiment**

---

## 🚫 Why No Sentiment?

### From `prediction_engine.py` Code:

```python
def _predict_ensemble(self, training_window, current_price):
    """
    Generate ensemble prediction (combines LSTM + Technical + Momentum)
    
    New improved ensemble without synthetic FinBERT.
    Uses three complementary approaches:
    - LSTM: Pattern recognition and trend continuation
    - Technical: Classical technical indicators (RSI, MACD, BB)
    - Momentum: Price momentum and rate of change
    """
    # Get predictions from all three models
    lstm_pred = self._predict_lstm(training_window, current_price)
    technical_pred = self._predict_technical(training_window, current_price)
    momentum_pred = self._predict_momentum(training_window, current_price)
    
    # Weighted voting (LSTM: 40%, Technical: 35%, Momentum: 25%)
    # NO SENTIMENT COMPONENT!
```

**Key Quote**: *"New improved ensemble without synthetic FinBERT"*

---

## 💡 Why This Matters

### The Problem with No Sentiment:

**Price data alone misses fundamental catalysts:**
- Company earnings announcements
- Market sentiment shifts
- News events (mergers, scandals, regulatory changes)
- Macroeconomic news (interest rates, inflation)
- Sector-specific news

**Example**: Your WBC.AX (Westpac Bank) test:
- 20% win rate, -0.93% return, 5 trades
- Bank stocks are HIGHLY sensitive to:
  - Interest rate announcements (RBA decisions)
  - Banking sector news
  - Economic outlook reports
  - Dividend announcements

**Without sentiment, the model can't anticipate these events!**

---

## 📈 What Historical Sentiment WOULD Look Like

If sentiment was being used (it's NOT), here's what it would need:

### 1. **Real Historical Sentiment** (Ideal):
```
Date: 2024-03-15
News: "RBA raises interest rates by 0.25%"
Sentiment: NEGATIVE for banks (mortgage business affected)
Impact: WBC price drops 2%
```

**Benefit**: Model would learn that negative rate news → sell signal

---

### 2. **Walk-Forward Sentiment** (No Look-Ahead Bias):
```
Prediction Date: 2024-03-20
News Available Up To: 2024-03-19 (NO future news)
Sentiment Score: -0.3 (based on past 7 days news)
Combined with: Technical indicators, price patterns
```

**Benefit**: Predicts based on sentiment trend, not future events

---

### 3. **Current Limitation** (What You Have):
```
Prediction Date: 2024-03-20
News: NONE
Sentiment: NONE
Data Used: Only price/volume from 2024-01-20 to 2024-03-19
Prediction: Based purely on price patterns
```

**Limitation**: Misses fundamental drivers!

---

## 🎯 Impact on Your Results

### Why Results Are Poor (-0.86% to -0.93%):

**1. No Anticipation of News Events**:
- Model can't predict earnings surprises
- Can't anticipate regulatory changes
- Misses sentiment shifts before price moves

**2. Lagging Indicators Only**:
- Technical indicators FOLLOW price (lagging)
- LSTM learns from PAST patterns (lagging)
- Momentum is based on PAST moves (lagging)

**3. Missing Leading Indicators**:
- Sentiment can be LEADING (news before price move)
- Example: Negative news → sentiment drops → THEN price drops
- Without sentiment, model only reacts AFTER price already moved

---

## 🔧 HOW TO ADD SENTIMENT (If You Want)

### Option 1: Real Historical News Sentiment

**Required**:
1. Historical news data for each stock
2. FinBERT sentiment model
3. Date-aligned sentiment scores
4. No look-ahead bias (only use news BEFORE prediction date)

**Process**:
```python
# Pseudo-code
for prediction_date in backtest_period:
    # Get historical news up to (but not including) prediction date
    news = get_news(symbol, start=prediction_date-7days, end=prediction_date-1day)
    
    # Calculate sentiment (no future data)
    sentiment_score = finbert_analyze(news)
    
    # Combine with technical
    final_prediction = ensemble(
        technical_score=0.35,
        momentum_score=0.25,
        lstm_score=0.30,
        sentiment_score=0.10  # Add sentiment weight
    )
```

**Cost**: Requires news API (expensive) or scraping (complex)

---

### Option 2: Proxy Sentiment (Free Alternative)

**Use VIX (Volatility Index) as sentiment proxy**:
- High VIX = Fear (negative sentiment)
- Low VIX = Greed (positive sentiment)

**Or use sector ETF performance**:
- Bank sector ETF up = Positive bank sentiment
- Sector down = Negative sentiment

**Benefit**: Free, historical data available, no look-ahead bias

---

### Option 3: Accept Limitations

**Just use what you have**:
- Price + technical + momentum
- Optimize parameters (confidence, stop loss)
- Focus on stocks with clear technical trends
- Accept that fundamental news will cause whipsaw

**Reality**: Many profitable traders use ONLY technicals (no sentiment)!

---

## ✅ BOTTOM LINE

**Current Backtest**:
- ❌ NO sentiment data (historical or otherwise)
- ✅ Price data only (OHLCV)
- ✅ Technical indicators (RSI, MACD, etc.)
- ✅ Pattern recognition (LSTM)
- ✅ Momentum indicators

**This Explains**:
- Why model has low confidence (60% threshold → only 5-11 trades/year)
- Why win rate is low (20-45%)
- Why it misses major moves (no fundamental catalysts)
- Why results are poor in news-driven markets

**Recommendation**:
1. **Accept limitation**: Focus on technical optimization
2. **Test technical-friendly stocks**: Momentum stocks, trending markets
3. **Lower confidence threshold**: 50-55% to get more signals
4. **OR add sentiment**: Requires significant development work

---

## 🎯 SUMMARY

**Question**: What sentiment is used?  
**Answer**: **NONE** - Only price, technical, and momentum data

**Impact**:
- Model misses fundamental catalysts
- Reacts to price AFTER news already moved it
- Why results are poor in news-driven stocks (banks, tech)

**Solution Options**:
1. Accept limitation, optimize technical parameters
2. Trade technical-friendly stocks (trending, high-volume)
3. Add sentiment (major dev work, needs news data API)

**Your current backtest is 100% technical/quantitative with ZERO sentiment/fundamental analysis!**

---

**Created**: 2025-12-06  
**Based on**: `prediction_engine.py` code analysis  
**Commit**: c9579ff
