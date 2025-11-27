# Momentum-Focused Scoring: Intraday vs. Overnight

## Overview

This document explains the **difference between overnight scoring and momentum-focused intraday scoring**, how they relate, and why each approach is optimal for its specific use case.

---

## 📊 Current Scoring System (Overnight Mode)

### **Purpose**
Designed for **next-day opportunities** based on overnight predictions and market gap analysis.

### **Scoring Formula**
```
Opportunity Score (0-100) = 
    Prediction Confidence (30%) +
    Technical Strength (20%) +
    SPI Alignment (15%) +
    Liquidity (15%) +
    Volatility (10%) +
    Sector Momentum (10%) +
    AI Enhancement (15%, when enabled)
```

### **Weight Breakdown**

| Factor | Weight | Purpose | Best For |
|--------|--------|---------|----------|
| **Prediction Confidence** | 30% | LSTM/FinBERT ML predictions | Next-day forecasts |
| **Technical Strength** | 20% | RSI, MA, screening score | Position strength |
| **SPI Alignment** | 15% | Alignment with overnight gap | Market direction |
| **Liquidity** | 15% | Volume, market cap | Trade execution |
| **Volatility** | 10% | Risk assessment (lower is better) | Overnight risk |
| **Sector Momentum** | 10% | Sector positioning | Long-term trends |

**Total**: 100%

---

## ⚡ Momentum-Focused Scoring (Intraday Mode)

### **Purpose**
Designed for **same-day opportunities** based on real-time price momentum and intraday volatility.

### **Proposed Scoring Formula**
```
Intraday Opportunity Score (0-100) = 
    Intraday Momentum (30%) +       ← NEW: Most important
    Technical Strength (25%) +      ← Increased (was 20%)
    Liquidity (20%) +               ← Increased (was 15%)
    Volatility Score (15%) +        ← Increased (was 10%)
    Prediction Confidence (10%) +   ← Decreased (was 30%)
    SPI Alignment (5%)              ← Decreased (was 15%)
```

### **Weight Breakdown**

| Factor | Overnight | Intraday | Change | Rationale |
|--------|-----------|----------|--------|-----------|
| **Prediction Confidence** | 30% | **10%** | -20% | Less reliable intraday (incomplete data) |
| **Technical Strength** | 20% | **25%** | +5% | Real-time technicals more relevant |
| **SPI Alignment** | 15% | **5%** | -10% | Market already open (gap irrelevant) |
| **Liquidity** | 15% | **20%** | +5% | Critical for rapid entry/exit |
| **Volatility** | 10% | **15%** | +5% | Opportunity for intraday traders |
| **Sector Momentum** | 10% | **0%** | -10% | Removed (too slow for intraday) |
| **Intraday Momentum** | 0% | **30%** | +30% | NEW: Core intraday factor |

**Total**: 100%

---

## 🎯 Key Difference: What is "Intraday Momentum"?

### **Definition**
**Intraday Momentum** measures price movement velocity and direction during the current trading session.

### **Components** (Proposed Implementation)

#### 1. **Price Rate of Change (40% of momentum score)**
```python
# 15-minute momentum
mom_15m = (current_price - price_15min_ago) / price_15min_ago * 100

# 60-minute momentum
mom_60m = (current_price - price_60min_ago) / price_60min_ago * 100

# Since market open momentum
mom_session = (current_price - open_price) / open_price * 100

momentum_score = (
    abs(mom_15m) * 0.4 +   # Short-term velocity
    abs(mom_60m) * 0.3 +   # Medium-term trend
    abs(mom_session) * 0.3  # Session trend
)
```

**What it captures:**
- ✅ Short-term price acceleration (15 min)
- ✅ Sustained intraday trends (60 min)
- ✅ Overall session direction (since open)

---

#### 2. **Volume Surge Detection (30% of momentum score)**
```python
# Current volume rate vs. typical
current_volume_rate = current_volume / hours_elapsed
typical_hourly_volume = avg_daily_volume / 6  # ASX trades 6 hours

volume_surge_ratio = current_volume_rate / typical_hourly_volume

if volume_surge_ratio > 2.0:
    volume_score = 100  # Major surge
elif volume_surge_ratio > 1.5:
    volume_score = 80   # Moderate surge
elif volume_surge_ratio > 1.2:
    volume_score = 60   # Slight increase
else:
    volume_score = 40   # Normal/low
```

**What it captures:**
- ✅ Abnormal buying/selling pressure
- ✅ Institutional activity
- ✅ News-driven spikes
- ✅ Breakout confirmations

---

#### 3. **Price Volatility Score (20% of momentum score)**
```python
# Intraday high-low range
intraday_range_pct = ((high - low) / open) * 100

# Volatility bands (compare to ATR)
if intraday_range_pct > atr_14_day * 2:
    volatility_score = 100  # High volatility (opportunity)
elif intraday_range_pct > atr_14_day:
    volatility_score = 70
else:
    volatility_score = 40
```

**What it captures:**
- ✅ Intraday price swings (opportunity for profit)
- ✅ Breakout potential
- ✅ Active trading environment

---

#### 4. **Breakout Detection (10% of momentum score)**
```python
# Support/resistance levels
supports = [ma_20, ma_50, recent_low]
resistances = [recent_high, 52_week_high]

if current_price > max(resistances):
    breakout_score = 100  # Breakout above resistance
elif current_price < min(supports):
    breakout_score = 100  # Breakdown below support
elif near_resistance(current_price, resistances):
    breakout_score = 60   # Approaching resistance
else:
    breakout_score = 40   # Range-bound
```

**What it captures:**
- ✅ Technical breakouts
- ✅ Support/resistance violations
- ✅ Potential trend changes

---

## 📈 Example Comparison: Same Stock, Different Modes

### **Stock Example: BHP.AX**

**Market Conditions:**
- **Time**: 2:00 PM AEST (67% of trading day complete)
- **Open**: $45.00
- **Current Price**: $45.75 (+1.67%)
- **Intraday High**: $46.00
- **Intraday Low**: $44.80
- **Volume**: 15M (typical: 10M for full day)
- **ML Prediction**: BUY (65% confidence)
- **SPI Gap**: +0.5% (bullish)

---

### **Overnight Mode Scoring** (Run at 10 PM, market closed)

| Factor | Score | Weight | Contribution |
|--------|-------|--------|--------------|
| **Prediction Confidence** | 78/100 | 30% | **23.4** |
| **Technical Strength** | 65/100 | 20% | **13.0** |
| **SPI Alignment** | 90/100 | 15% | **13.5** (perfect BUY + bullish) |
| **Liquidity** | 85/100 | 15% | **12.8** |
| **Volatility** | 70/100 | 10% | **7.0** |
| **Sector Momentum** | 75/100 | 10% | **7.5** |
| **Total** | | | **77.2/100** |

**Interpretation:** Strong overnight opportunity. High confidence in next-day BUY signal aligned with bullish market gap.

---

### **Intraday Mode Scoring** (Run at 2 PM, market open)

| Factor | Score | Weight | Contribution |
|--------|-------|--------|--------------|
| **Intraday Momentum** | | 30% | |
| - 15m momentum | +0.4% | | Fast acceleration |
| - 60m momentum | +1.2% | | Strong trend |
| - Session momentum | +1.67% | | Bullish day |
| - Volume surge | 1.5x typical | | Moderate interest |
| - Volatility | $1.20 range | | Active trading |
| - Breakout status | Near resistance | | Could break higher |
| **→ Momentum Score** | **85/100** | 30% | **25.5** |
| **Technical Strength** | 75/100 | 25% | **18.8** (real-time RSI, MACD) |
| **Liquidity** | 90/100 | 20% | **18.0** (high intraday volume) |
| **Volatility Score** | 80/100 | 15% | **12.0** (opportunity) |
| **Prediction Confidence** | 65/100 | 10% | **6.5** (less reliable intraday) |
| **SPI Alignment** | 50/100 | 5% | **2.5** (irrelevant now) |
| **Total** | | | **83.3/100** |

**Interpretation:** Strong intraday momentum opportunity. Actively rising with volume support. Consider buying dips or riding the trend.

---

## 🔍 Deep Dive: Why the Weights Change

### **1. Prediction Confidence: 30% → 10%** ⬇️

**Overnight (30%):**
- ML models trained on **full trading days**
- Predictions based on **complete daily data**
- Overnight gap predictions highly relevant
- Next-day forecasts are the core output

**Intraday (10%):**
- ML models see **incomplete trading day** (2-5 hours of 6)
- Only 33-83% of data available
- Predictions less reliable (incomplete patterns)
- Today's outcome partially visible already

**Example:**
- **Overnight**: "BUY with 65% confidence for tomorrow" ← Full data, high trust
- **Intraday at 2 PM**: "BUY with 65% confidence for... today?" ← Already happening, less useful

---

### **2. SPI Alignment: 15% → 5%** ⬇️

**Overnight (15%):**
- SPI futures predict ASX **opening gap** (+0.5%, -0.3%, etc.)
- Critical for next-day positioning
- Stock prediction + SPI alignment = powerful signal

**Intraday (5%):**
- Market **already opened** (gap already occurred)
- SPI prediction realized (or invalidated)
- Current price action more important than gap

**Example:**
- **Overnight**: "SPI predicts +0.5% gap, BHP forecast BUY" ← Aligned bullish signal
- **Intraday at 2 PM**: "Market opened +0.3%, now +1.67%" ← Gap old news, momentum matters

---

### **3. Technical Strength: 20% → 25%** ⬆️

**Overnight (20%):**
- Uses **yesterday's closing data**
- RSI, MACD, MA crossovers from EOD
- Static snapshot

**Intraday (25%):**
- Uses **real-time technical indicators**
- Live RSI, MACD updating every minute
- Dynamic support/resistance tests
- More relevant for current action

**Example:**
- **Overnight**: "RSI was 55 at close" ← Static
- **Intraday**: "RSI is 62 and rising, MACD bullish crossover 30 min ago" ← Actionable

---

### **4. Liquidity: 15% → 20%** ⬆️

**Overnight (15%):**
- Ensures stock is tradeable tomorrow
- Average volume sufficient for entry/exit
- Market cap adequate

**Intraday (20%):**
- **Critical for rapid execution**
- Need to enter/exit within minutes
- Slippage risk if low liquidity
- Bid-ask spread matters

**Example:**
- **Overnight**: "Avg volume 10M, market cap $50B" ← Can trade tomorrow
- **Intraday**: "Current volume 15M (1.5x typical), bid-ask $0.02" ← Can trade NOW

---

### **5. Volatility: 10% → 15%** ⬆️

**Overnight (10%):**
- Measures **historical volatility**
- Lower volatility = less overnight risk
- Prefer stability for next-day holds

**Intraday (15%):**
- Measures **intraday price swings**
- Higher volatility = more profit opportunity
- Prefer movement for intraday trades

**Example:**
- **Overnight**: "Stock has 2% daily volatility (low risk)" ← Good for holding
- **Intraday**: "Stock moved $1.20 in 4 hours (high volatility)" ← Good for trading

---

### **6. Sector Momentum: 10% → 0%** ⬇️

**Overnight (10%):**
- Sector trends develop over days/weeks
- Banking sector strength supports bank stocks
- Useful for multi-day positioning

**Intraday (0%):**
- Sector trends **too slow for intraday**
- Individual stock momentum dominates
- Removed to make room for momentum factors

**Example:**
- **Overnight**: "Banking sector up 5% this week" ← BHP might continue
- **Intraday**: "Banking sector +0.1% today, but CBA +2%" ← Individual stock matters

---

### **7. Intraday Momentum: 0% → 30%** ⬆️ **NEW**

**Overnight (0%):**
- Doesn't exist (market closed, no momentum)
- Uses prediction + SPI instead

**Intraday (30%):**
- **Core factor for intraday trading**
- Captures price velocity, volume surges, breakouts
- Most predictive of short-term moves

**What it measures:**
- 📈 Is price accelerating? (15m/60m momentum)
- 📊 Is volume surging? (vs. typical hourly rate)
- 💥 Is it breaking out? (support/resistance)
- 🌊 What's the intraday range? (volatility opportunity)

---

## 💡 Real-World Use Cases

### **Scenario 1: Overnight Pipeline (Run at 10 PM)**

**Stock: NAB.AX**
- ML Prediction: **BUY** (70% confidence)
- SPI Sentiment: **Bullish** (+0.6% gap expected)
- Technical: RSI 52, above MA20
- Liquidity: High (20M avg volume)

**Overnight Score: 82/100**
- ✅ Strong prediction confidence (30% weight)
- ✅ Aligned with bullish market gap (15% weight)
- ✅ Solid technicals
- 📝 **Action**: Add to watchlist for market open

---

### **Scenario 2: Intraday Pipeline (Run at 1:30 PM)**

**Stock: NAB.AX**
- Current: $30.50 (+1.8% from open)
- 15m momentum: +0.5%
- 60m momentum: +1.2%
- Volume: 18M (1.6x typical)
- Breaking above $30.40 resistance

**Intraday Score: 87/100**
- ✅ **Strong intraday momentum (30% weight)**
- ✅ Volume surge confirmation (20% liquidity weight)
- ✅ Active volatility (15% weight)
- ✅ Breakout above resistance
- 📝 **Action**: Enter long position NOW, set stop-loss at $30.20

---

### **Scenario 3: Why Overnight Score ≠ Intraday Score**

**Stock: BHP.AX at 2 PM**

| Mode | Score | Top Factor | Action |
|------|-------|------------|--------|
| **Overnight** | 77/100 | Prediction Confidence (30%) | Buy tomorrow at open |
| **Intraday** | 83/100 | **Momentum (30%)** | Buy NOW (momentum strong) |

**Key Insight:** Same stock, different context:
- **Overnight**: Predicting tomorrow's performance
- **Intraday**: Reacting to today's momentum

---

## 📊 Implementation Code (Proposed)

### **New Function: `score_intraday_momentum()`**

```python
def score_intraday_momentum(self, stock: Dict, market_status: Dict) -> float:
    """
    Score intraday momentum (0-1)
    
    Components:
    1. Price rate of change (15m, 60m, session)
    2. Volume surge vs. typical
    3. Intraday volatility (range)
    4. Breakout detection
    
    Args:
        stock: Stock data with intraday prices
        market_status: Market hours status (elapsed %, etc.)
        
    Returns:
        Momentum score (0-1)
    """
    scores = {}
    
    # 1. Price Momentum (40% of momentum score)
    if 'intraday_prices' in stock:
        prices = stock['intraday_prices']
        current_price = prices[-1]
        
        # 15-minute momentum
        if len(prices) >= 15:
            mom_15m = (current_price - prices[-15]) / prices[-15] * 100
            scores['mom_15m'] = min(abs(mom_15m) * 10, 100)  # Scale: 1% = 10 points
        else:
            scores['mom_15m'] = 50
        
        # 60-minute momentum
        if len(prices) >= 60:
            mom_60m = (current_price - prices[-60]) / prices[-60] * 100
            scores['mom_60m'] = min(abs(mom_60m) * 8, 100)
        else:
            scores['mom_60m'] = 50
        
        # Session momentum
        open_price = stock.get('open', current_price)
        mom_session = (current_price - open_price) / open_price * 100
        scores['mom_session'] = min(abs(mom_session) * 15, 100)
        
        momentum_score = (
            scores['mom_15m'] * 0.4 +
            scores['mom_60m'] * 0.3 +
            scores['mom_session'] * 0.3
        )
    else:
        momentum_score = 50  # Neutral if no intraday data
    
    # 2. Volume Surge (30% of momentum score)
    hours_elapsed = market_status.get('trading_hours_elapsed_pct', 50) / 100 * 6
    if hours_elapsed > 0.5:  # At least 30 minutes elapsed
        current_volume = stock.get('current_volume', 0)
        avg_daily_volume = stock.get('volume', 1_000_000)
        
        current_volume_rate = current_volume / hours_elapsed
        typical_hourly_volume = avg_daily_volume / 6
        
        surge_ratio = current_volume_rate / typical_hourly_volume
        
        if surge_ratio > 2.0:
            volume_score = 100
        elif surge_ratio > 1.5:
            volume_score = 80
        elif surge_ratio > 1.2:
            volume_score = 60
        else:
            volume_score = 40
    else:
        volume_score = 50  # Too early to assess
    
    # 3. Intraday Volatility (20% of momentum score)
    high = stock.get('intraday_high', stock.get('price', 0))
    low = stock.get('intraday_low', stock.get('price', 0))
    open_price = stock.get('open', stock.get('price', 0))
    
    if open_price > 0:
        intraday_range_pct = ((high - low) / open_price) * 100
        
        # Higher range = more opportunity
        if intraday_range_pct > 3.0:
            volatility_score = 100
        elif intraday_range_pct > 2.0:
            volatility_score = 80
        elif intraday_range_pct > 1.0:
            volatility_score = 60
        else:
            volatility_score = 40
    else:
        volatility_score = 50
    
    # 4. Breakout Detection (10% of momentum score)
    current_price = stock.get('price', 0)
    ma_20 = stock.get('technical', {}).get('ma_20', current_price)
    recent_high = stock.get('52_week_high', current_price * 1.05)
    recent_low = stock.get('52_week_low', current_price * 0.95)
    
    # Check for breakout
    if current_price > recent_high * 0.995:  # Within 0.5% of high
        breakout_score = 100
    elif current_price < recent_low * 1.005:  # Within 0.5% of low
        breakout_score = 100
    elif current_price > ma_20 * 1.02:  # 2% above MA20
        breakout_score = 70
    else:
        breakout_score = 40
    
    # Combine all momentum components
    total_momentum = (
        momentum_score * 0.40 +
        volume_score * 0.30 +
        volatility_score * 0.20 +
        breakout_score * 0.10
    )
    
    # Normalize to 0-1
    return total_momentum / 100
```

---

### **Modified: `score_opportunities()` with Mode Detection**

```python
def score_opportunities(
    self,
    stocks_with_predictions: List[Dict],
    spi_sentiment: Dict = None,
    ai_scores: Dict = None,
    market_status: Dict = None  # NEW
) -> List[Dict]:
    """
    Calculate opportunity scores with mode awareness
    
    Args:
        stocks_with_predictions: List of stocks
        spi_sentiment: Market sentiment
        ai_scores: AI scoring data
        market_status: Market hours status (NEW)
    """
    # Detect pipeline mode
    if market_status and market_status.get('is_open', False):
        pipeline_mode = 'intraday'
        logger.info("📈 Intraday scoring mode active")
    else:
        pipeline_mode = 'overnight'
        logger.info("🌙 Overnight scoring mode active")
    
    scored_stocks = []
    
    for stock in stocks_with_predictions:
        if pipeline_mode == 'intraday':
            # Use intraday weights
            score = self._calculate_intraday_score(stock, market_status)
        else:
            # Use overnight weights
            score = self._calculate_opportunity_score(stock, spi_sentiment)
        
        # Add AI enhancement
        if ai_scores and stock['symbol'] in ai_scores:
            score = self._integrate_ai_score(score, ai_scores[stock['symbol']])
        
        stock['opportunity_score'] = score['total_score']
        stock['score_breakdown'] = score['breakdown']
        stock['pipeline_mode'] = pipeline_mode
        
        scored_stocks.append(stock)
    
    # Sort by score
    scored_stocks.sort(key=lambda x: x['opportunity_score'], reverse=True)
    
    return scored_stocks
```

---

## 📋 Summary Table: Overnight vs. Intraday

| Aspect | Overnight Mode | Intraday Mode |
|--------|----------------|---------------|
| **Primary Goal** | Predict next-day opportunities | Capture same-day momentum |
| **Top Factor** | Prediction Confidence (30%) | Intraday Momentum (30%) |
| **Data Used** | Yesterday's close + overnight data | Real-time prices (1-min bars) |
| **Time Horizon** | Next trading day (24 hours) | Current session (minutes to hours) |
| **SPI Relevance** | High (15%) - predicts gap | Low (5%) - gap already occurred |
| **Volatility View** | Risk (lower is better) | Opportunity (higher is better) |
| **Liquidity Need** | Moderate (15%) | Critical (20%) |
| **Best Run Time** | After market close | During market hours |
| **ML Predictions** | Highly relevant (30%) | Less relevant (10%) |
| **Execution Speed** | Next day (hours) | Immediate (minutes) |

---

## 🎯 When to Use Each Mode

### **Use Overnight Mode When:**
- ✅ Market is closed
- ✅ Planning next-day positions
- ✅ Swing trading (multi-day holds)
- ✅ Leveraging overnight gap predictions
- ✅ ML predictions are core to strategy

### **Use Intraday Mode When:**
- ✅ Market is open
- ✅ Day trading (same-day in/out)
- ✅ Momentum trading
- ✅ Reacting to live price action
- ✅ Need rapid entry/exit signals

---

## 💰 Cost Impact (No Change)

Both modes have the same AI cost:
- **Overnight**: ~$0.033 per run
- **Intraday**: ~$0.033 per run
- **Data Fetching**: $0 (yfinance free)

**Auto-rescan feature (Phase 3):**
- 10 intraday rescans: ~$0.33 per day

---

## 🚀 Implementation Status

### **Current (Phase 1):**
- ✅ Market hours detection
- ✅ Mode awareness (overnight vs. intraday)
- ✅ Warnings during intraday runs
- ❌ Still using overnight weights

### **Phase 2 (Proposed):**
- ⚡ Implement `score_intraday_momentum()`
- ⚡ Fetch 1-minute price bars
- ⚡ Adjust weights based on mode
- ⚡ Calculate volume surge ratios
- ⚡ Real-time technical indicators

### **Phase 3 (Future):**
- ⚡ Auto-rescan every 15-30 minutes
- ⚡ Push notifications for breakouts
- ⚡ Intraday-specific reports

---

## 📚 Key Takeaways

1. **Overnight Scoring**: Optimized for **predicting tomorrow** (confidence, SPI gap alignment)
2. **Intraday Scoring**: Optimized for **reacting to now** (momentum, volume, breakouts)
3. **Same Data, Different Weights**: Both use similar stock data but prioritize different factors
4. **Momentum is King Intraday**: 30% weight on real-time price movement and volume
5. **Predictions Less Useful Intraday**: Only 10% weight (incomplete day, less predictive)
6. **Volatility Flips**: From risk (overnight) to opportunity (intraday)
7. **Zero Additional Cost**: Both modes use same AI budget

---

## ❓ FAQs

### Q: Why not use intraday momentum for overnight runs?
**A:** No intraday data exists when market is closed. Momentum factors require real-time prices.

### Q: Can I manually force intraday mode?
**A:** Phase 2 will add this. Currently, mode is auto-detected based on market hours.

### Q: Will this change my existing recommendations?
**A:** No. Overnight mode remains default. Intraday mode only activates when market is open.

### Q: Do I need Phase 2 if I only run overnight?
**A:** No. Phase 1 (current) is sufficient for overnight runs. Phase 2 is for active day traders.

---

## 📖 Related Documentation

- `INTRADAY_FEATURE_README.md` - Current implementation (Phase 1)
- `INTRADAY_ENHANCEMENT_PLAN.md` - Full Phase 2-4 roadmap
- `HOW_STOCK_RECOMMENDATIONS_WORK.md` - General scoring explanation

---

**Ready for Phase 2?** See `INTRADAY_ENHANCEMENT_PLAN.md` for implementation timeline! 🚀
