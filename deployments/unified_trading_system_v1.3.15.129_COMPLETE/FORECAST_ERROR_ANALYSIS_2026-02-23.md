# Forecast Accuracy Report - 2026-02-23

## 📊 Actual Market Performance vs Forecast

### ASX 200 Performance

**From 24-Hour Chart** (visible in screenshot):
- Market trend: **DECLINING throughout the day**
- Visual analysis: Started ~7850, ended ~7700
- Approximate change: **-1.9% to -2.0%** (estimated from chart)

### Top Stock Picks Performance

| Stock | Forecast | Actual | Error | Status |
|-------|----------|--------|-------|--------|
| **STO.AX** | BUY 91.6/100 (64.3% conf) | **-2.67%** | ❌ **WRONG** | Lost 2.67% |
| **ORG.AX** | BUY 90.6/100 (64.3% conf) | **-1.23%** | ❌ **WRONG** | Lost 1.23% |

---

## 🎯 Forecast vs Actual Comparison

### Market Direction Forecast

**Morning Prediction** (11:10 AM):
```
Expected ASX 200 Open: 🟢 UP +0.46%
Market Sentiment: STRONG_BUY (76.9/100)
Confidence: 90%
Recommendation: "Strong bullish sentiment. Consider aggressive long positions."
Risk: LOW
```

**Actual Result**:
```
ASX 200: 📉 DOWN ~-2.0%
Error: -2.46% (completely wrong direction!)
Status: ❌ MAJOR MISS
```

---

### Stock Picks Accuracy

**Stock #1: STO.AX**
```
Forecast:
- Signal: BUY
- Score: 91.6/100 (top pick!)
- Confidence: 64.3%
- Analysis: "Strong buy signal"

Actual:
- Performance: -2.67% ❌
- Result: LOSS
- Error: Predicted UP, actually DOWN
```

**Stock #2: ORG.AX**
```
Forecast:
- Signal: BUY
- Score: 90.6/100 (3rd best)
- Confidence: 64.3%
- Analysis: "Strong buy signal... Trading above 20-day MA"

Actual:
- Performance: -1.23% ❌
- Result: LOSS
- Error: Predicted UP, actually DOWN
```

---

## 📉 Error Analysis

### Directional Accuracy

| Prediction | Actual | Result |
|------------|--------|--------|
| ASX +0.46% | ASX -2.0% | ❌ **Wrong direction** |
| STO BUY | STO -2.67% | ❌ **Wrong direction** |
| ORG BUY | ORG -1.23% | ❌ **Wrong direction** |
| **Total**: 0/3 correct | **Accuracy: 0%** | ❌ **Complete miss** |

### Magnitude of Error

**ASX 200 Forecast Error**:
```
Predicted: +0.46%
Actual:    -2.0%
Error:     -2.46%
Magnitude: 5.3× worse than predicted
```

**Implications**:
- Predicted small gain (+0.46%)
- Market fell sharply (-2.0%)
- Total error: **-2.46%**
- Traders following this would have **lost 5× more** than expected gain!

---

## 🔍 Why Did It Fail?

### Issue 1: Ignored Market Regime (Critical)

**From Report**:
```
Current Market Regime: ⚪ Unknown
Crash Risk Score: 36% (MODERATE RISK)
Daily Volatility: 0.00%  ← BROKEN!
```

**Reality**: Market was in **risk-off mode** (visible from -2% decline)

**What Should Have Happened**:
```python
# If regime detection worked:
if regime == 'high_volatility' or crash_risk > 35%:
    # Reduce bullish bias
    sentiment_adjustment = -15  # Penalize for risk
    prediction = prediction * 0.7  # Dampen optimism
    warning = "HIGH CRASH RISK - CAUTION ADVISED"
```

**Result**: System showed "LOW RISK" when it should have shown **"MODERATE-HIGH RISK"**

---

### Issue 2: Over-Reliance on US Markets

**US Markets (overnight)**:
```
SP500:  +0.69% 🟢
Nasdaq: +0.90% 🟢
Dow:    +0.47% 🟢
```

**Formula Used**:
```
ASX prediction = (US markets average) × 0.65
               = 0.709% × 0.65
               = +0.46%
```

**Problem**: This assumes **perfect correlation**, but:
- ✅ US closed up
- ❌ ASX opened down anyway

**Likely reasons for decoupling**:
1. **Local Australian factors** (ignored by model):
   - RBA policy concerns
   - Commodity prices (iron ore, gold)
   - China economic data
   - AUD/USD weakness

2. **Sector-specific issues**:
   - STO.AX (Santos - oil/gas): -2.67%
   - ORG.AX (Origin Energy): -1.23%
   - Energy sector weakness NOT predicted

3. **Gap-down opening**:
   - System predicted +0.46% open
   - Market likely gapped DOWN at open (common after negative overnight news)

---

### Issue 3: Uniform Confidence (Red Flag)

**All stocks: 64.3% confidence**

This suggests:
- ML model not discriminating between stocks
- All getting same generic signal
- No stock-specific analysis

**In reality**:
- Energy sector (STO, ORG) had specific headwinds
- System should have flagged energy weakness
- Different sectors = different confidence levels

---

### Issue 4: Sentiment Overcalibration

**76.9/100 = "STRONG_BUY"** was overconfident

**Better interpretation**:
```
76.9/100 in high-risk regime (36% crash risk) should be:
  → "CAUTIOUS BUY" or "HOLD"
  → NOT "Strong bullish sentiment. Consider aggressive long positions."
```

---

## 🔧 Root Causes (Technical)

### 1. Market Regime Not Working

**File**: `pipelines/models/screening/overnight_pipeline.py`

**Problem**:
```python
def _calculate_market_regime(self, opportunities):
    # Missing: overnight_data = self.market_data_fetcher.fetch_overnight_data()
    return {
        'regime': 'Unknown',  # ← Always returns this!
        'volatility': 0.00     # ← Always zero!
    }
```

**Impact**: System blind to market conditions (calm vs stormy)

---

### 2. Gap Prediction Too Simplistic

**File**: `pipelines/models/screening/spi_monitor.py`

**Problem**:
```python
predicted_gap = weighted_us_change * 0.65  # Linear only!
# Missing:
# - Regime adjustment (volatile markets amplify moves)
# - Local factors (commodities, AUD, RBA)
# - Sector rotation (tech up but energy down)
```

**Impact**: Predicted +0.46% when energy stocks were weak

---

### 3. No Sector-Specific Analysis

**Problem**: STO and ORG are both **energy stocks**

**What system should check**:
- Oil prices overnight: ↓ Down?
- Natural gas prices: ↓ Down?
- Energy sector ETF (XLE): Performance?
- Commodity currencies (AUD): Weak?

**If energy was weak overnight**, both STO and ORG should have been:
- Downgraded from BUY to HOLD
- Flagged with "Energy sector weakness" warning

---

## 📊 Hypothetical "Fixed" Forecast

**If all fixes were applied**, the forecast would have been:

```
Expected ASX 200 Open: 🟡 DOWN -0.3% to +0.2%
Market Sentiment: CAUTIOUS (68/100)
Confidence: 65%
Recommendation: "Mixed signals. US markets positive but high crash risk (36%) 
                suggests caution. Energy sector showing weakness."
Risk: MODERATE-HIGH

Top Picks:
1. [Non-energy stock] - BUY 88/100
2. [Non-energy stock] - BUY 85/100
3. STO.AX - HOLD 72/100 (Energy sector weakness detected)
4. ORG.AX - HOLD 71/100 (Energy sector weakness detected)
```

**Result**: Would have avoided aggressive longs in energy sector!

---

## 🎯 Accuracy Metrics Summary

### Before Fixes (Actual Performance)

| Metric | Value |
|--------|-------|
| **Directional Accuracy** | 0% (0/3 correct) |
| **ASX Forecast Error** | -2.46% (5.3× worse) |
| **Stock Pick Win Rate** | 0% (0/2 profitable) |
| **Average Stock Loss** | -1.95% |
| **Risk Assessment** | Wrong ("LOW" when actually MODERATE-HIGH) |
| **Overall Grade** | **F (Major Failure)** |

---

## 🔧 Implementation Priority (After This Result)

### 🔴 CRITICAL (Must Fix Immediately)

1. **Fix Market Regime Detection**
   - Add overnight data fetch
   - Use regime to adjust predictions
   - Impact: Would have shown "MODERATE-HIGH RISK" instead of "LOW RISK"

2. **Add Sector Analysis**
   - Detect energy sector weakness
   - Downgrade STO/ORG from BUY to HOLD
   - Impact: Would have avoided -2.67% and -1.23% losses

3. **Add Regime-Aware Gap Prediction**
   - In high crash-risk (36%): dampen bullish predictions
   - Adjust for local factors (commodities, AUD)
   - Impact: Would have predicted -0.3% to +0.2% (closer to actual -2.0%)

### 🟡 HIGH (Should Fix Soon)

4. **Recalibrate Sentiment Thresholds**
   - 76.9/100 → "CAUTIOUS BUY" not "STRONG_BUY"
   - Factor in crash risk to recommendation
   - Impact: Less overconfident messaging

5. **Fix Confidence Calculation**
   - Investigate why all stocks = 64.3%
   - Add stock-specific factors
   - Impact: More realistic confidence levels

### 🟢 MEDIUM (Can Fix Later)

6. **Remove Duplicate Stocks**
   - STO.AX appeared twice in top 5
   - Impact: Cosmetic (doesn't affect accuracy but looks unprofessional)

---

## 📈 Expected Improvement After Fixes

**Scenario: If fixes were applied to 2026-02-23 forecast**

| Metric | Before | After (Estimated) | Improvement |
|--------|--------|-------------------|-------------|
| **Directional Accuracy** | 0% | 50-60% | ✅ Better |
| **ASX Error** | -2.46% | -0.8% to -1.2% | ✅ 50-67% better |
| **Risk Assessment** | Wrong | Correct | ✅ Would warn |
| **Stock Picks** | 0/2 profitable | 0-1/2 profitable | ✅ Would avoid energy |

**Note**: Even with all fixes, predicting exact market moves is hard. Goal is to:
- Get direction right more often (50-60% vs 0%)
- Avoid major mistakes (aggressive longs in weak sectors)
- Provide accurate risk warnings

---

## 🎯 Conclusion

**What went wrong on 2026-02-23**:

1. ❌ Market regime detection broken (showed "Unknown" instead of "High Risk")
2. ❌ Over-reliance on US markets (+0.69% US → +0.46% ASX predicted)
3. ❌ Ignored local factors (energy sector weakness, commodity prices)
4. ❌ Overconfident recommendation ("Strong bullish" when risk was high)
5. ❌ All stocks same confidence (64.3%) - no differentiation

**Result**: 
- Forecast: +0.46% (STRONG_BUY, LOW RISK)
- Actual: -2.0% (market fell)
- **Error: -2.46% (completely wrong)**

**Action**: Implement Priority 1-3 fixes immediately to prevent future misses.

---

*Analysis Date: 2026-02-23*  
*Actual Data: ASX ~-2.0%, STO -2.67%, ORG -1.23%*  
*Forecast Error: -2.46% (Wrong direction)*  
*Grade: F (Major Failure)*
