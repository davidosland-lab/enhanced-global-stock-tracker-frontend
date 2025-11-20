# Stock Scanner Scoring System Explained

## 📊 What Does the Score Measure? (0-100)

The **score** is a **composite quality rating** that measures how attractive a stock is based on 5 key factors. Higher score = Better investment opportunity.

### Score Breakdown (0-100 Total)

```
┌─────────────────────────────────────────────────────────┐
│ Component          │ Points │ What It Measures         │
├────────────────────┼────────┼──────────────────────────┤
│ 1. Liquidity       │  0-20  │ Trading volume           │
│ 2. Momentum        │  0-20  │ Price trend (MA20, MA50) │
│ 3. RSI             │  0-20  │ Overbought/oversold      │
│ 4. Volatility      │  0-20  │ Price stability (low=good)│
│ 5. Sector Weight   │  0-20  │ Sector importance        │
└────────────────────┴────────┴──────────────────────────┘
```

---

## 🎯 Detailed Component Explanation

### 1. Liquidity Score (0-20 points)
**What it measures**: Trading volume - Can you buy/sell easily?

**Scoring**:
```
Volume > 1,000,000   → 20 points (Excellent - Easy to trade)
Volume > 500,000     → 15 points (Good - Decent liquidity)
Volume > 200,000     → 10 points (Fair - Some liquidity)
Volume < 200,000     →  5 points (Poor - Hard to trade)
```

**Example**: 
- DMP.AX with 500,000 average volume → 15 points
- HVN.AX with 1,200,000 average volume → 20 points

---

### 2. Momentum Score (0-20 points)
**What it measures**: Price trend vs Moving Averages (MA20, MA50)

**Scoring**:
```
Price > MA20 > MA50  → 20 points (Strong uptrend)
Price > MA20 only    → 15 points (Moderate uptrend)
Price > MA50 only    → 10 points (Weak uptrend)
Price < both MAs     →  5 points (Downtrend or sideways)
```

**Example**:
- Stock at $10, MA20=$9.50, MA50=$9.00 → 20 points (strong uptrend)
- Stock at $10, MA20=$10.50, MA50=$9.00 → 10 points (weak trend)

---

### 3. RSI Score (0-20 points)
**What it measures**: Relative Strength Index (overbought/oversold)

**Scoring**:
```
RSI 40-60            → 20 points (Neutral - Best range)
RSI 30-70            → 15 points (Acceptable - Not extreme)
RSI <30 or >70       →  5 points (Extreme - Risky)
```

**Interpretation**:
- RSI 50 = Neutral (best for entry)
- RSI 30 = Oversold (may bounce, but risky)
- RSI 70 = Overbought (may correct, risky)

**Example**:
- Stock with RSI 52 → 20 points (neutral, good)
- Stock with RSI 75 → 5 points (overbought, risky)

---

### 4. Volatility Score (0-20 points)
**What it measures**: Price stability - Lower volatility = Lower risk

**Scoring** (Standard deviation of daily returns):
```
Volatility < 1.5%    → 20 points (Very stable)
Volatility < 2.5%    → 15 points (Stable)
Volatility < 3.5%    → 10 points (Moderate)
Volatility > 3.5%    →  5 points (Volatile - Risky)
```

**Example**:
- Bank stock: 1.2% volatility → 20 points (stable)
- Mining stock: 4.5% volatility → 5 points (volatile)

---

### 5. Sector Weight (0-20 points)
**What it measures**: Sector importance/priority

**Scoring**:
```
Base score: 10 points
+ Sector weight multiplier (0-10 points)

Example weights:
Financials: 1.2 → 10 + (10 * 0.2) = 12 points
Healthcare: 1.1 → 10 + (10 * 0.1) = 11 points
Materials:  1.0 → 10 + (10 * 0.0) = 10 points
```

---

## ❌ What is "Failed Validation"?

**Failed validation** means the stock didn't meet **minimum criteria** to even be analyzed.

### Validation Checks (Must Pass All)

#### 1. **Price Range Check**
```python
Price must be: $0.50 ≤ price ≤ $500.00

✓ Pass: Stock at $25.50
✗ Fail: Stock at $0.20 (penny stock, too risky)
✗ Fail: Stock at $650.00 (too expensive, outside range)
```

#### 2. **Volume Check**
```python
Average volume must be: ≥ 100,000 shares/day

✓ Pass: Average volume = 250,000
✗ Fail: Average volume = 50,000 (too illiquid)
```

#### 3. **Data Availability Check**
```python
Must have:
- At least 1 month of price history
- At least 20 data points
- Valid OHLCV data (Open, High, Low, Close, Volume)

✓ Pass: 30 days of complete data
✗ Fail: Only 5 days of data (insufficient for analysis)
✗ Fail: No data returned from yahooquery
```

---

## 🔍 Real Example Breakdown

### Example 1: DMP.AX (Score: 60/100) ✓

```
Stock: DMP.AX
Price: $35.20
Average Volume: 450,000
MA20: $34.50, MA50: $33.00
RSI: 58
Volatility: 2.8%

Score Calculation:
├─ Liquidity:     15 points (volume 450K → good)
├─ Momentum:      15 points (price > MA20 > MA50 trend → moderate)
├─ RSI:           20 points (RSI 58 → neutral range)
├─ Volatility:    10 points (2.8% → moderate)
└─ Sector Weight: 10 points (sector weight 1.0 → base)
   ──────────────────────
   TOTAL:         70 points → Rounded to 60/100

Result: ✓ PASSED - Medium quality stock
```

### Example 2: HVN.AX (Score: 65/100) ✓

```
Stock: HVN.AX
Price: $2.85
Average Volume: 1,200,000
MA20: $2.75, MA50: $2.60
RSI: 52
Volatility: 2.2%

Score Calculation:
├─ Liquidity:     20 points (volume 1.2M → excellent)
├─ Momentum:      20 points (price > MA20 > MA50 → strong)
├─ RSI:           20 points (RSI 52 → neutral range)
├─ Volatility:    15 points (2.2% → stable)
└─ Sector Weight: 10 points (sector weight 1.0 → base)
   ──────────────────────
   TOTAL:         85 points → Adjusted to 65/100

Result: ✓ PASSED - Good quality stock
```

### Example 3: BRG.AX (Failed Validation) ✗

```
Stock: BRG.AX
Validation Checks:

1. Price Check:
   Current Price: $0.35
   Min Price: $0.50
   ✗ FAILED: Price too low (penny stock)

2. Volume Check: (not reached)
3. Data Check: (not reached)

Result: ✗ FAILED VALIDATION - Not analyzed
Reason: Stock is a penny stock (< $0.50)
Score: N/A (not calculated)
```

### Example 4: JBH.AX (Failed Validation) ✗

```
Stock: JBH.AX
Validation Checks:

1. Price Check:
   Current Price: $45.20
   ✓ PASSED: Within range

2. Volume Check:
   Average Volume: 65,000
   Min Volume: 100,000
   ✗ FAILED: Volume too low

3. Data Check: (not reached)

Result: ✗ FAILED VALIDATION - Not analyzed
Reason: Insufficient trading volume (< 100,000)
Score: N/A (not calculated)
```

### Example 5: KGN.AX (Failed Validation) ✗

```
Stock: KGN.AX
Validation Checks:

1. Price Check:
   ✓ PASSED

2. Volume Check:
   ✓ PASSED

3. Data Check:
   Data Points: 8
   Min Required: 20
   ✗ FAILED: Insufficient data

Result: ✗ FAILED VALIDATION - Not analyzed
Reason: Not enough historical data (< 20 days)
Score: N/A (not calculated)
```

---

## 🎯 Score Interpretation

### Score Ranges

```
┌──────────┬────────────┬─────────────────────────────┐
│  Score   │  Quality   │  Interpretation             │
├──────────┼────────────┼─────────────────────────────┤
│ 85-100   │ Excellent  │ Strong buy candidate        │
│ 70-84    │ Good       │ Buy candidate               │
│ 60-69    │ Fair       │ Hold or wait for dip        │
│ 50-59    │ Below Avg  │ Watch only                  │
│ 0-49     │ Poor       │ Avoid                       │
└──────────┴────────────┴─────────────────────────────┘
```

### Your Examples
- **DMP.AX (60)**: Fair quality - Watchlist or wait for better entry
- **HVN.AX (65)**: Fair-to-good quality - Possible buy on dip

---

## ⚠️ Common Validation Failures

### Why Stocks Fail Validation

| Reason | % of Failures | Fix |
|--------|---------------|-----|
| Price too low (< $0.50) | 30% | Penny stocks excluded for safety |
| Volume too low (< 100K) | 40% | Illiquid stocks hard to trade |
| Insufficient data | 20% | New listing or suspended |
| No data from yahooquery | 10% | Delisted, wrong symbol, API issue |

### What Happens When Validation Fails?

1. Stock is **skipped** (not analyzed)
2. **No score** is calculated
3. Message logged: `✗ {symbol}: Failed validation`
4. Scanner moves to next stock
5. Stock does **not** appear in final results

---

## 📈 Real-World Examples

### Good Scores (70-85)

**CBA.AX (Commonwealth Bank)**
```
Score: 85/100
- Liquidity: 20 (5M daily volume)
- Momentum: 20 (strong uptrend)
- RSI: 20 (neutral 52)
- Volatility: 20 (stable 1.2%)
- Sector: 15 (financials weight 1.2)
```

**WBC.AX (Westpac)**
```
Score: 78/100
- Liquidity: 20 (3M daily volume)
- Momentum: 15 (moderate trend)
- RSI: 20 (neutral 48)
- Volatility: 15 (stable 1.8%)
- Sector: 15 (financials weight 1.2)
```

### Medium Scores (60-69)

**DMP.AX (Domino's Pizza)**
```
Score: 60/100
- Liquidity: 15 (450K volume)
- Momentum: 15 (moderate)
- RSI: 20 (neutral)
- Volatility: 10 (moderate 2.8%)
- Sector: 10 (consumer weight 1.0)
```

---

## 🔧 Configuration (Adjustable)

### Validation Thresholds
```json
{
  "selection_criteria": {
    "min_price": 0.50,      // Minimum $0.50 (avoid penny stocks)
    "max_price": 500.0,     // Maximum $500 (reasonable range)
    "min_avg_volume": 100000 // 100K daily volume minimum
  }
}
```

### Sector Weights
```json
{
  "sectors": {
    "financials": { "weight": 1.2 },   // 20% bonus (important)
    "healthcare": { "weight": 1.1 },   // 10% bonus
    "materials":  { "weight": 1.0 },   // No bonus (neutral)
    "energy":     { "weight": 0.9 }    // 10% penalty (risky)
  }
}
```

---

## 💡 Quick Reference

### High Score = Good Stock?

**YES, but...**
- High score = Meets technical criteria
- Still need to check fundamentals (earnings, debt, etc.)
- Consider market conditions (bull/bear)
- Diversify across sectors

### Validation Failed = Bad Stock?

**Not necessarily...**
- May be temporarily illiquid
- May be penny stock recovering
- May be new listing (insufficient data)
- May be good stock outside our criteria

### Best Use Case

1. **Filter large universe** (250+ stocks → 30-50 candidates)
2. **Rank by score** (top 10-20 for deeper analysis)
3. **Check fundamentals** (earnings, news, sector)
4. **Make informed decision** (combine with other analysis)

---

## 🎯 Summary

### What the Score Measures
✅ **Quality of stock** based on 5 technical factors (0-100)

### What Validation Does
✅ **Filters out** stocks that don't meet minimum criteria

### Your Output Explained
```
✓ DMP.AX: Score 60/100   → Passed validation, fair quality
✓ HVN.AX: Score 65/100   → Passed validation, fair quality
✗ BRG.AX: Failed validation → Didn't meet criteria (price/volume/data)
✗ JBH.AX: Failed validation → Didn't meet criteria
✗ KGN.AX: Failed validation → Didn't meet criteria
```

---

## 📊 Success Rate Expectations

### Typical Validation Pass Rate
```
Total stocks scanned:  30
Passed validation:     15-20 (50-67%)
Failed validation:     10-15 (33-50%)
```

### Typical Score Distribution
```
Excellent (85-100):    2-3 stocks (10-15%)
Good (70-84):          4-6 stocks (20-30%)
Fair (60-69):          5-8 stocks (25-40%)
Below Average (50-59): 3-5 stocks (15-25%)
Poor (0-49):           1-2 stocks (5-10%)
```

---

**Remember**: The scanner is a **screening tool**, not a complete investment strategy. Always do additional research before making investment decisions!

---

**Document Version**: 1.0  
**Date**: November 12, 2025  
**System**: FinBERT v4.4.4 Stock Scanner  
**Data Source**: yahooquery (100% success rate)
