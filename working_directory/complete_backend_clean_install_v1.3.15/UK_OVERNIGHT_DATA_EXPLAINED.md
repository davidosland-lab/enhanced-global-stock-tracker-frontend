# UK Overnight Market Sentiment - Data Sources Explained

## 📊 OVERVIEW

The UK pipeline now fetches **real overnight/weekend trading data** to determine market sentiment, similar to how the Australian pipeline uses SPI futures and the US pipeline uses VIX.

---

## 🇬🇧 UK OVERNIGHT INSTRUMENTS

### **1. FTSE 100 Index (^FTSE)**
**What It Is:**
- The main UK stock market index (100 largest companies)
- Like the S&P 500 for the US or ASX 200 for Australia

**How It's Used:**
- **Symbol:** `^FTSE`
- **Current Price:** Shows market level
- **Day Change %:** Direction indicator
- **Impact:** ±30 sentiment points (±1% = ±10 points)

**Example:**
- FTSE 100 up +1.5% → Sentiment +15 points (bullish)
- FTSE 100 down -2.0% → Sentiment -20 points (bearish)

---

### **2. VFTSE (UK VIX Equivalent)**
**What It Is:**
- **FTSE 100 Volatility Index**
- UK's version of the US VIX ("fear gauge")
- Measures expected 30-day volatility

**How It's Used:**
- **Symbol:** `^VFTSE`
- **Normal Level:** ~15
- **High Fear:** >20 (sentiment -8 points)
- **Very High Fear:** >25 (sentiment -15 points)
- **Low Fear:** <12 (sentiment +5 points)

**Example:**
- VFTSE at 12 → Low fear, bullish market (+5 points)
- VFTSE at 22 → High fear, nervous market (-8 points)
- VFTSE at 28 → Panic mode (-15 points)

---

### **3. GBP/USD (Cable)**
**What It Is:**
- British Pound vs US Dollar exchange rate
- **"Cable"** is the forex nickname (from transatlantic telegraph cables)

**Why It Matters:**
- **60% of FTSE 100 revenue** comes from overseas
- **Strong GBP** = Lower overseas earnings when converted back
- **Weak GBP** = Higher overseas earnings (good for exporters)

**How It's Used:**
- **Symbol:** `GBPUSD=X`
- **Impact:** -5 points per +1% GBP strength
- **Trades:** 24/5 forex market (overnight data available)

**Example:**
- GBP/USD rises +1.0% (stronger pound) → Sentiment -5 points (bad for FTSE exporters)
- GBP/USD falls -1.5% (weaker pound) → Sentiment +7.5 points (good for FTSE exporters)

---

## 🧮 SENTIMENT CALCULATION

### **Formula:**
```python
Sentiment Score = 50.0 (neutral baseline)
                + (FTSE % change × 10)      # ±30 points max
                - (VFTSE impact)             # -15 to +5 points
                - (GBP/USD % change × 5)     # GBP strength hurts FTSE
```

### **Range:** 0-100
- **0-35:** Bearish → AVOID
- **35-45:** Slightly Bearish → CAUTION
- **45-55:** Neutral → HOLD
- **55-65:** Slightly Bullish → WATCH
- **65-100:** Bullish → BUY

---

## 📈 REAL-WORLD EXAMPLE

### **Scenario 1: Risk-Off Market**
```
FTSE 100:     -1.2% (down overnight)
VFTSE:        24.5 (high fear)
GBP/USD:      +0.5% (strong pound)

Calculation:
  Base:       50.0
  FTSE:       -12.0  (down 1.2% × 10)
  VFTSE:      -8.0   (high fear penalty)
  GBP/USD:    -2.5   (strong GBP hurts exports)
  ─────────────────
  Total:      27.5/100 → BEARISH → AVOID
```

### **Scenario 2: Bull Market**
```
FTSE 100:     +0.8% (up overnight)
VFTSE:        11.5 (low fear)
GBP/USD:      -0.6% (weak pound)

Calculation:
  Base:       50.0
  FTSE:       +8.0   (up 0.8% × 10)
  VFTSE:      +5.0   (low fear bonus)
  GBP/USD:    +3.0   (weak GBP helps exports)
  ─────────────────
  Total:      66.0/100 → BULLISH → BUY
```

### **Scenario 3: Neutral Market**
```
FTSE 100:     +0.1% (flat)
VFTSE:        15.2 (normal)
GBP/USD:      -0.1% (stable)

Calculation:
  Base:       50.0
  FTSE:       +1.0   (up 0.1% × 10)
  VFTSE:      0.0    (normal range)
  GBP/USD:    +0.5   (minimal move)
  ─────────────────
  Total:      51.5/100 → NEUTRAL → HOLD
```

---

## 🌍 COMPARISON WITH OTHER MARKETS

| Market | Overnight Indicator | Volatility Gauge | Currency Impact |
|--------|---------------------|------------------|-----------------|
| **Australia** | SPI Futures | ASX VIX | AUD/USD (commodity proxy) |
| **US** | S&P Futures | VIX | USD Index (reserve currency) |
| **UK** | FTSE Futures | VFTSE | GBP/USD (export sensitivity) |

---

## ⏰ WHEN IS THIS DATA AVAILABLE?

### **FTSE 100 (^FTSE)**
- **Regular Hours:** 08:00-16:30 GMT (London)
- **Futures Trading:** Nearly 24/5 on ICE Futures Europe
- **Weekend:** Limited (Sunday evening futures open)

### **VFTSE (^VFTSE)**
- **Updates:** During FTSE 100 trading hours
- **Calculation:** Real-time during market hours
- **Futures Sessions:** Extended hours via FTSE futures

### **GBP/USD (GBPUSD=X)**
- **Trading:** 24 hours, 5 days per week
- **Opens:** Sunday 5pm EST (10pm GMT)
- **Closes:** Friday 5pm EST (10pm GMT)
- **Best Liquidity:** London session (08:00-16:30 GMT)

---

## 🎯 PRACTICAL USE IN UK PIPELINE

### **Morning Pipeline Run (Before LSE Open)**
1. **Fetch overnight data:**
   - FTSE 100 previous close + any futures movement
   - VFTSE to gauge market fear
   - GBP/USD overnight change

2. **Calculate sentiment score (0-100)**

3. **Generate recommendation:**
   - **BUY:** Score 65+ → Scan for long opportunities
   - **HOLD:** Score 45-55 → Neutral, selective screening
   - **AVOID:** Score <35 → Consider cash, short bias

4. **Apply to stock screening:**
   - Bullish sentiment → Favor growth/tech stocks
   - Bearish sentiment → Favor defensives (utilities, healthcare)
   - High VFTSE → Reduce position sizes, favor low-beta stocks

---

## 🆕 WHAT CHANGED IN v1.3.15.35

### **Before (v1.3.15.34):**
```python
# Hardcoded placeholder values
ftse100 = 7500.0  # Static
sentiment_score = 50.0  # Always neutral
recommendation = 'HOLD'  # Never changes
```

### **After (v1.3.15.35):**
```python
# Real overnight data from Yahoo Finance
ftse_ticker = Ticker('^FTSE')  # Real FTSE 100 price
vftse_ticker = Ticker('^VFTSE')  # Real UK VIX
gbp_ticker = Ticker('GBPUSD=X')  # Real forex rate

# Dynamic sentiment calculation
sentiment_score = calculate_from_real_data()
recommendation = determine_from_score()  # BUY/HOLD/AVOID
```

---

## 📝 OUTPUT EXAMPLE

### **Previous Output (Placeholder):**
```
[OK] UK Market Sentiment Retrieved:
  FTSE 100: 7500.00
  Sentiment Score: 50.0/100
  Recommendation: HOLD
```

### **New Output (Real Data):**
```
[OK] UK Market Sentiment Retrieved:
  FTSE 100: 8,234.56 (+0.45%)
  VFTSE (UK VIX): 16.25 (Normal)
  GBP/USD: 1.2687 (-0.32%)
  Sentiment Score: 58.2/100 (Slightly Bullish)
  Risk Rating: Moderate
  Recommendation: WATCH
```

---

## 🔍 DATA SOURCE RELIABILITY

### **Yahoo Finance (yahooquery)**
- ✅ **Free:** No API key required
- ✅ **Reliable:** Industry-standard data provider
- ✅ **Real-time:** 15-minute delayed for indices (free tier)
- ✅ **24/5 Coverage:** Forex and futures data available overnight

### **Fallback Behavior**
If Yahoo Finance is unavailable:
- Uses last known values with warning log
- Defaults to neutral sentiment (50.0)
- Pipeline continues without crashing

---

## 🎉 BENEFITS

1. **Real Market Conditions:** No more placeholder data
2. **Overnight Direction:** See where FTSE is heading before LSE opens
3. **Volatility Awareness:** VFTSE shows if it's time to reduce risk
4. **Currency Impact:** GBP strength affects UK export earnings
5. **Dynamic Recommendations:** BUY/HOLD/AVOID based on real conditions

---

## 🚀 READY TO USE

After installing v1.3.15.35, your UK pipeline will show **real overnight market data** every time it runs!

**No additional setup required** - it fetches data automatically from Yahoo Finance.

---

*Version: v1.3.15.35*  
*Feature: Real UK Overnight Sentiment*  
*Date: January 26, 2026*
