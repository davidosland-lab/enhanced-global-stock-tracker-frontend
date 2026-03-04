# Market-Specific Regime Engine Fix (v1.3.15.38)

## 🔍 **PROBLEM FOUND**

User spotted **Australian data** appearing in the UK pipeline logs:

```
_extract_close: symbols requested=["^AXJO", "AUDUSD=X"]
Using calculated volatility from ASX 200 returns
```

**Root Cause:** The `EventRiskGuard` and `MarketRegimeEngine` had **hardcoded Australian symbols**:
- `^AXJO` (ASX 200 index)
- `AUDUSD=X` (Australian dollar)

When the UK or US pipelines initialized EventRiskGuard, they were using **wrong market data**!

---

## ✅ **SOLUTION IMPLEMENTED**

### **Market-Specific Configuration**

The `EventRiskGuard` now accepts a `market` parameter and creates appropriate regime engine configs:

| Market | Index Symbol | Volatility | FX Symbol | Purpose |
|--------|--------------|------------|-----------|---------|
| **UK** | `^FTSE` | Calculated | `GBPUSD=X` | FTSE 100, GBP strength |
| **US** | `^GSPC` | `^VIX` | `DX-Y.NYB` | S&P 500, VIX, USD Index |
| **AU** | `^AXJO` | Calculated | `AUDUSD=X` | ASX 200, AUD strength |

---

## 🔧 **CODE CHANGES**

### **1. EventRiskGuard (event_risk_guard.py)**

**Before:**
```python
def __init__(self, extra_providers=None, csv_path=None):
    # ...
    self.regime_engine = MarketRegimeEngine()  # ❌ Always used AU config!
```

**After:**
```python
def __init__(self, extra_providers=None, csv_path=None, market='AU'):
    self.market = market
    # ...
    if market == 'UK':
        regime_config = MarketRegimeConfig(
            index_symbol="^FTSE",
            vol_symbol=None,  # Use calculated volatility
            fx_symbol="GBPUSD=X"
        )
    elif market == 'US':
        regime_config = MarketRegimeConfig(
            index_symbol="^GSPC",  # S&P 500
            vol_symbol="^VIX",
            fx_symbol="DX-Y.NYB"  # USD Index
        )
    else:  # AU (default)
        regime_config = MarketRegimeConfig(
            index_symbol="^AXJO",
            vol_symbol=None,  # ASX VIX not available
            fx_symbol="AUDUSD=X"
        )
    
    self.regime_engine = MarketRegimeEngine(config=regime_config)
```

### **2. UK Pipeline (uk_overnight_pipeline.py)**

**Before:**
```python
self.event_guard = EventRiskGuard()  # ❌ Used AU config
```

**After:**
```python
self.event_guard = EventRiskGuard(market='UK')  # ✅ UK config
```

### **3. US Pipeline (us_overnight_pipeline.py)**

**Before:**
```python
self.event_guard = EventRiskGuard()  # ❌ Used AU config
```

**After:**
```python
self.event_guard = EventRiskGuard(market='US')  # ✅ US config
```

### **4. AU Pipeline (overnight_pipeline.py)**

**Before:**
```python
self.event_guard = EventRiskGuard()  # ✅ Was correct but implicit
```

**After:**
```python
self.event_guard = EventRiskGuard(market='AU')  # ✅ Explicit
```

---

## 📊 **EXPECTED LOG OUTPUT**

### **UK Pipeline (After Fix):**
```
2026-01-26 - models.screening.market_regime_engine - INFO - _extract_close: symbols requested=["^FTSE", "GBPUSD=X"]
2026-01-26 - models.screening.market_regime_engine - INFO - Using calculated volatility from FTSE 100 returns
2026-01-26 - models.screening.event_risk_guard - INFO - [OK] Market Regime Engine initialized successfully (UK market)
```

### **US Pipeline (After Fix):**
```
2026-01-26 - models.screening.market_regime_engine - INFO - _extract_close: symbols requested=["^GSPC", "^VIX", "DX-Y.NYB"]
2026-01-26 - models.screening.market_regime_engine - INFO - Using VIX volatility data
2026-01-26 - models.screening.event_risk_guard - INFO - [OK] Market Regime Engine initialized successfully (US market)
```

### **AU Pipeline (After Fix):**
```
2026-01-26 - models.screening.market_regime_engine - INFO - _extract_close: symbols requested=["^AXJO", "AUDUSD=X"]
2026-01-26 - models.screening.market_regime_engine - INFO - Using calculated volatility from ASX 200 returns
2026-01-26 - models.screening.event_risk_guard - INFO - [OK] Market Regime Engine initialized successfully (AU market)
```

---

## 🎯 **MARKET-SPECIFIC SYMBOLS EXPLAINED**

### **UK Market Symbols**

**Index:** `^FTSE` (FTSE 100)
- London Stock Exchange's main index
- 100 largest UK companies by market cap
- Trading hours: 08:00-16:30 GMT

**FX:** `GBPUSD=X` (Cable)
- British Pound vs US Dollar
- Impact: Strong GBP hurts UK exporters (60% FTSE revenue overseas)
- 24/5 trading

**Volatility:** Calculated from FTSE 100 returns
- No dedicated VFTSE ticker on Yahoo Finance
- Alternative: Use 20-day rolling volatility

### **US Market Symbols**

**Index:** `^GSPC` (S&P 500)
- US stock market's main benchmark
- 500 largest US companies
- Trading hours: 09:30-16:00 EST

**Volatility:** `^VIX` (CBOE Volatility Index)
- The original "fear gauge"
- Measures expected 30-day volatility
- Normal ~15, High >20, Panic >25

**FX:** `DX-Y.NYB` (US Dollar Index)
- Measures USD strength vs basket of currencies
- Higher = stronger dollar (impacts US exporters)
- Reserve currency benchmark

### **AU Market Symbols**

**Index:** `^AXJO` (ASX 200)
- Australian stock market's main index
- 200 largest ASX companies
- Trading hours: 10:00-16:00 AEST

**FX:** `AUDUSD=X` (Aussie)
- Australian Dollar vs US Dollar
- Commodity currency (tracks iron ore, coal, gold)
- 24/5 trading

**Volatility:** Calculated from ASX 200 returns
- No dedicated ASX VIX ticker available
- Alternative: Use 20-day rolling volatility

---

## 🔍 **WHY THIS MATTERS**

### **1. Crash Risk Scores**
EventRiskGuard uses regime engine to calculate crash risk scores. Using wrong market data would give:
- UK stocks assessed against ASX volatility (incorrect)
- US stocks using AUD/USD correlation (meaningless)

### **2. Beta Calculations**
EventRiskGuard calculates stock beta vs market index for hedge suggestions:
- UK: Beta vs FTSE 100 ✅
- US: Beta vs S&P 500 ✅
- AU: Beta vs ASX 200 ✅

**Before fix:** All markets were using beta vs ASX 200 ❌

### **3. Volatility Context**
Regime engine provides volatility context for risk scoring:
- UK: FTSE 100 volatility
- US: VIX (actual fear gauge)
- AU: ASX 200 volatility

**Before fix:** All markets used ASX 200 volatility ❌

---

## 🎉 **BENEFITS**

### **1. Correct Market Data**
- UK pipeline now uses FTSE 100, GBP/USD
- US pipeline now uses S&P 500, VIX, USD Index
- AU pipeline explicitly uses ASX 200, AUD/USD

### **2. Accurate Risk Assessment**
- Crash risk scores based on correct market volatility
- Beta calculations vs appropriate benchmark
- Hedge suggestions use correct correlations

### **3. Clearer Logging**
- Log messages now show which market: "(UK market)", "(US market)", "(AU market)"
- Symbols in logs match the market being analyzed

---

## 📋 **FILES MODIFIED**

| File | Change | Impact |
|------|--------|--------|
| `models/screening/event_risk_guard.py` | Added `market` parameter | Market-specific config |
| `models/screening/uk_overnight_pipeline.py` | Pass `market='UK'` | UK symbols |
| `models/screening/us_overnight_pipeline.py` | Pass `market='US'` | US symbols |
| `models/screening/overnight_pipeline.py` | Pass `market='AU'` | AU symbols |

---

## 🚀 **NO USER ACTION REQUIRED**

This fix works **automatically** - no config changes needed!

Just run any pipeline and it will use the correct market data:

**UK:**
```bash
python run_uk_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
```

**US:**
```bash
python run_us_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
```

**AU:**
```bash
python run_au_full_pipeline.py --full-scan --capital 100000 --ignore-market-hours
```

---

## 🔍 **HOW TO VERIFY THE FIX**

After running any pipeline, check the logs for:

**UK Pipeline - Should see:**
```
symbols requested=["^FTSE", "GBPUSD=X"]
```

**NOT:**
```
symbols requested=["^AXJO", "AUDUSD=X"]  ❌ Wrong!
```

---

## 📊 **VERSION SUMMARY**

| Version | Issue | Status |
|---------|-------|--------|
| v1.3.15.37 | Tiered validation all markets | ✅ |
| **v1.3.15.38** | **UK pipeline using AU data** | **✅ FIXED** |

---

## 🎯 **USER FEEDBACK ADDRESSED**

**User Report:**
> "There still seems to be mentions of australian indicies in the UK pipeline"

**Fix Applied:**
✅ EventRiskGuard now market-aware  
✅ UK pipeline uses ^FTSE + GBPUSD=X  
✅ US pipeline uses ^GSPC + ^VIX + USD Index  
✅ AU pipeline explicitly uses ^AXJO + AUDUSD=X  

---

*Version: v1.3.15.38*  
*Feature: Market-Specific Regime Engine*  
*Impact: Correct market data for UK, US, and AU pipelines*  
*Date: January 26, 2026*
