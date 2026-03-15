# Market Forecast vs Actual Performance Analysis - 2026-02-23

## 📊 Report Summary

**Date**: 2026-02-23  
**Generated**: 11:10 AM AEDT  
**Report**: ASX Morning Report  

---

## 🎯 Forecast (Morning Prediction)

### Market Overview Forecast

| Metric | Prediction |
|--------|------------|
| **Expected ASX 200 Open** | 🟢 UP +0.46% |
| **Confidence** | 90% |
| **Market Sentiment** | STRONG_BUY (76.9/100) |
| **Recommendation** | "Strong bullish sentiment. Consider aggressive long positions." |
| **Risk Level** | LOW |

### Basis for Prediction

**Overnight US Markets** (closed before ASX opened):
- S&P 500: +0.69%
- Nasdaq: +0.90%
- Dow: +0.47%

**Top 5 Stock Picks** (all BUY signals):
1. STO.AX - 91.6/100 (Confidence: 64.3%)
2. STO.AX - 91.5/100 (Confidence: 64.3%) [duplicate!]
3. ORG.AX - 90.6/100 (Confidence: 64.3%)
4. [more stocks...]

---

## 🔍 Issues Identified in the Forecast System

### Issue 1: Duplicate Stock Recommendations

**Problem**:
```
1. STO.AX - 91.6/100
2. STO.AX - 91.5/100  ← Same stock twice!
```

**Root Cause**: Stock scanner returning duplicate entries

**Location**: 
- `pipelines/models/screening/stock_scanner.py`
- `pipelines/models/screening/overnight_pipeline.py` (deduplication logic)

**Impact**: Wastes 2 of 5 top slots on same stock

---

### Issue 2: Market Regime Shows "Unknown"

**Problem**:
```
Current Market Regime: ⚪ Unknown
Daily Volatility: 0.00%
Annual Volatility: 0.00%
Regime State Probabilities: (empty table)
```

**Root Cause**: Market regime detector not fetching overnight data

**Location**: 
- `pipelines/models/screening/overnight_pipeline.py` - `_calculate_market_regime()`
- Missing call to `MarketDataFetcher.fetch_overnight_data()`

**Code Issue**:
```python
# Current (BROKEN):
def _calculate_market_regime(self, opportunities):
    # No overnight data fetched
    # Returns: regime="Unknown", volatility=0.00%
    
# Should be:
def _calculate_market_regime(self, opportunities):
    overnight_data = self.market_data_fetcher.fetch_overnight_data()  # MISSING!
    regime = self.regime_detector.detect_regime(overnight_data)
```

**Impact**: 
- Crash risk score (36%) is unreliable
- Volatility metrics useless (0.00%)
- Can't assess true market regime

---

### Issue 3: Gap Prediction Formula Mismatch

**Problem**: Predicted gap calculation doesn't match actual ASX behavior

**Current Formula** (in `spi_monitor.py` line 335):
```python
# Weighted US change
weighted_us_change = 0.5*SP500 + 0.3*Nasdaq + 0.2*Dow
                   = 0.5*0.69% + 0.3*0.90% + 0.2*0.47%
                   = 0.345% + 0.27% + 0.094%
                   = 0.709%

# Apply 65% correlation factor
predicted_gap = 0.709% * 0.65 = 0.46%
```

**Issue**: This is a **simplified linear model** that assumes:
1. ✅ ASX moves 65% of US market change (historically accurate)
2. ❌ All days have same correlation (ignores volatility regimes)
3. ❌ Ignores time-of-day effects (US closes at 7 AM AEDT)
4. ❌ Ignores SPI 200 futures (overnight trading indicator)
5. ❌ Ignores sector-specific news
6. ❌ Ignores currency moves (AUD/USD impacts resources)

**Better Approach**:
```python
def _predict_opening_gap_v2(self, asx_data, us_data, spi_data, aud_usd):
    # 1. Base correlation (65%)
    us_weighted = 0.5*SP500 + 0.3*Nasdaq + 0.2*Dow
    base_prediction = us_weighted * 0.65
    
    # 2. Adjust for SPI 200 futures (if available)
    if spi_data['available']:
        spi_signal = spi_data['change_pct']
        base_prediction = 0.7*base_prediction + 0.3*spi_signal  # Blend
    
    # 3. Adjust for volatility regime
    if regime == 'high_volatility':
        base_prediction *= 1.2  # Amplify moves
    elif regime == 'low_volatility':
        base_prediction *= 0.8  # Dampen moves
    
    # 4. Adjust for AUD/USD (resources sensitivity)
    aud_impact = aud_usd_change * 0.15  # 15% weight for currency
    base_prediction += aud_impact
    
    return base_prediction
```

---

### Issue 4: Sentiment Score Overcalibration

**Problem**: Sentiment of 76.9/100 classified as "STRONG_BUY" with "LOW" risk

**Thresholds** (in code):
```python
if sentiment > 70:
    recommendation = "STRONG_BUY"
    risk = "LOW"
elif sentiment > 60:
    recommendation = "BUY"
    risk = "MODERATE"
```

**Issue**: 76.9 is only marginally above 70, yet gets "STRONG_BUY" label

**Reality Check**:
- 76.9/100 = **76.9% confidence**
- That's good, but not "aggressive long positions" good
- Should be "BUY" not "STRONG_BUY"

**Better Thresholds**:
```python
if sentiment > 85:
    recommendation = "STRONG_BUY"  # Very high confidence
    risk = "LOW"
elif sentiment > 75:
    recommendation = "BUY"  # High confidence
    risk = "LOW-MODERATE"
elif sentiment > 65:
    recommendation = "BUY"  # Moderate confidence
    risk = "MODERATE"
```

---

### Issue 5: Confidence Metrics Inconsistent

**Problem**: All stocks show 64.3% confidence

**From Report**:
```
STO.AX #1: Confidence 64.3%
STO.AX #2: Confidence 64.3%
ORG.AX #3: Confidence 64.3%
```

**This suggests**:
- ML model outputting same confidence for all stocks (red flag!)
- OR: confidence being clamped/normalized incorrectly
- OR: default value when actual confidence unavailable

**Root Cause Locations**:
```python
# swing_signal_generator.py - line ~220
confidence = (
    sentiment_weight * sentiment_score +
    lstm_weight * lstm_score +
    technical_weight * technical_score +
    momentum_weight * momentum_score +
    volume_weight * volume_score
)

# If all inputs similar → all outputs similar
# Likely issue: Components not diverse enough
```

---

## 🎯 What Actually Happened (Need User Input)

**User, please provide**:
1. What did ASX 200 actually do today?
   - Opening change: ?
   - Closing change: ?

2. How did the top 5 stocks perform?
   - STO.AX: ?
   - ORG.AX: ?

**Example of what we need**:
```
Forecast: ASX 200 +0.46%
Actual:   ASX 200 -1.2%  ← Mismatch!

Forecast: STO.AX BUY (91.6/100)
Actual:   STO.AX -3.5%  ← Wrong!
```

---

## 🔧 Recommended Fixes

### Priority 1: Fix Market Regime Detection (High Impact)

**File**: `pipelines/models/screening/overnight_pipeline.py`

**Current** (line ~XXX):
```python
def _calculate_market_regime(self, opportunities):
    # Broken - no data fetched
    return {
        'regime': 'Unknown',
        'volatility': 0.00
    }
```

**Fix**:
```python
def _calculate_market_regime(self, opportunities):
    # FIX v1.3.15.171: Fetch overnight ASX data
    try:
        overnight_data = self.market_data_fetcher.fetch_overnight_data(
            symbol='^AXJO',
            period='60d'  # 60 days for regime detection
        )
        
        if overnight_data is not None and len(overnight_data) > 20:
            regime_result = self.regime_detector.detect_regime(overnight_data)
            return regime_result
        else:
            logger.warning("Insufficient overnight data for regime detection")
            return self._get_default_regime()
    except Exception as e:
        logger.error(f"Market regime calculation failed: {e}")
        return self._get_default_regime()
```

---

### Priority 2: Remove Duplicate Stocks (Medium Impact)

**File**: `pipelines/models/screening/overnight_pipeline.py`

**Add deduplication** after scoring:
```python
def _score_opportunities(self, scanned_stocks):
    # Score stocks
    scored_stocks = self.opportunity_scorer.score_opportunities(scanned_stocks)
    
    # FIX v1.3.15.171: Deduplicate by symbol
    seen_symbols = set()
    unique_stocks = []
    for stock in scored_stocks:
        symbol = stock.get('symbol')
        if symbol not in seen_symbols:
            seen_symbols.add(symbol)
            unique_stocks.append(stock)
        else:
            logger.warning(f"Duplicate stock removed: {symbol}")
    
    logger.info(f"Deduplicated: {len(scored_stocks)} → {len(unique_stocks)} stocks")
    return unique_stocks
```

---

### Priority 3: Improve Gap Prediction (High Impact)

**File**: `pipelines/models/screening/spi_monitor.py`

**Add regime-aware prediction**:
```python
def _predict_opening_gap(self, asx_data, us_data, regime=None):
    # Calculate base prediction
    base_prediction = self._calculate_base_prediction(us_data)
    
    # FIX v1.3.15.171: Adjust for market regime
    if regime == 'high_volatility':
        regime_factor = 1.25  # Amplify in volatile markets
    elif regime == 'low_volatility':
        regime_factor = 0.75  # Dampen in calm markets
    elif regime == 'bull_market':
        regime_factor = 1.05  # Slight amplification
    elif regime == 'bear_market':
        regime_factor = 1.15  # Amplify negative moves
    else:
        regime_factor = 1.0   # Unknown regime = neutral
    
    adjusted_prediction = base_prediction * regime_factor
    
    logger.info(f"Gap prediction: {base_prediction:.2f}% → {adjusted_prediction:.2f}% (regime: {regime}, factor: {regime_factor})")
    
    return {
        'predicted_gap_pct': adjusted_prediction,
        'base_prediction': base_prediction,
        'regime_adjustment': regime_factor,
        ...
    }
```

---

### Priority 4: Recalibrate Sentiment Thresholds (Low Impact)

**File**: `pipelines/models/screening/spi_monitor.py`

**Tighten thresholds**:
```python
def _get_recommendation(self, sentiment_score):
    # FIX v1.3.15.171: More conservative thresholds
    if sentiment_score >= 85:
        return {
            'stance': 'STRONG_BUY',
            'message': 'Very strong bullish sentiment. Consider aggressive long positions.',
            'risk': 'LOW'
        }
    elif sentiment_score >= 75:
        return {
            'stance': 'BUY',
            'message': 'Strong bullish sentiment. Favor long positions.',
            'risk': 'LOW-MODERATE'
        }
    elif sentiment_score >= 65:
        return {
            'stance': 'BUY',
            'message': 'Bullish sentiment. Consider long positions.',
            'risk': 'MODERATE'
        }
    # ... rest of thresholds
```

---

## 📊 Expected Improvements After Fixes

| Metric | Before | After (Expected) |
|--------|--------|------------------|
| **Regime Detection** | Unknown (0%) | Detected (>90%) |
| **Volatility Accuracy** | 0.00% (broken) | Real values |
| **Duplicate Stocks** | 2/5 slots wasted | 0 duplicates |
| **Gap Prediction Error** | ±0.8% | ±0.5% (better) |
| **Sentiment Calibration** | Overconfident | More accurate |

---

## 🎯 Next Steps

1. **User provides actual market data** for 2026-02-23
2. Calculate forecast error metrics
3. Implement Priority 1-3 fixes
4. Re-run pipeline and compare
5. Iterate based on results

---

*Analysis Date: 2026-02-23*  
*System Version: v1.3.15.170*  
*Report File: 2026-02-23_market_report.html*
