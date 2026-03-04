# Pipeline Comparison: AU vs UK vs US - Issue Analysis

## 📊 Pipeline Feature Comparison

| Feature | AU Pipeline | UK Pipeline | US Pipeline | Status |
|---------|-------------|-------------|-------------|--------|
| **Market Regime Detection** | ✅ Via EventGuard | ❌ Missing | ✅ `_analyze_market_regime()` | **UK needs fix** |
| **Crash Risk Scoring** | ✅ Via EventGuard | ❌ Missing | ✅ Via regime method | **UK needs fix** |
| **Volatility Calculation** | ✅ Via EventGuard | ❌ Missing | ✅ Via regime method | **UK needs fix** |
| **Stock Deduplication** | ❌ Missing | ❌ Missing | ❌ Missing | **ALL need fix** |
| **LSTM Training** | ✅ Has method | ✅ Has method | ✅ Has method | ✅ Good |
| **Event Risk Assessment** | ✅ Via EventGuard | ✅ Has method | ✅ Has method | ✅ Good |
| **Sentiment Fetching** | ✅ SPI + US markets | ✅ UK + US markets | ✅ US markets only | ✅ Good |

---

## 🔍 Detailed Analysis

### Issue 1: Market Regime Detection

#### AU Pipeline (✅ GOOD)
**File**: `overnight_pipeline.py` line 647-707

```python
def _assess_event_risks(self, stocks: List[Dict]) -> Dict:
    results = self.event_guard.assess_batch(tickers)
    
    # Market regime included in results
    if 'market_regime' in results:
        regime = results['market_regime']
        logger.info(f"Market Regime: {regime.get('regime_label')}")
        logger.info(f"Crash Risk: {regime.get('crash_risk_score')*100:.1f}%")
    
    return results  # Includes market_regime key
```

**Result**: AU reports show regime data (though may still be "Unknown" if EventGuard isn't loading data properly)

---

#### UK Pipeline (❌ BROKEN)
**File**: `uk_overnight_pipeline.py` line 569-591

```python
def _assess_event_risks(self, stocks: List[Dict]) -> Dict:
    """Assess event risks for all scanned stocks"""
    if self.event_guard is None:
        return {}
    
    # ... event assessment ...
    
    return results  # NO market_regime key!
```

**Problem**: 
- Has EventGuard
- Calls `assess_batch()`
- But doesn't extract `market_regime` from results
- Report shows "Unknown" regime + 0.00% volatility

---

#### US Pipeline (✅ GOOD - Different Approach)
**File**: `us_overnight_pipeline.py` line 403-424

```python
def _analyze_market_regime(self) -> Dict:
    """Analyze current market regime using HMM"""
    logger.info("Analyzing market regime...")
    
    try:
        # Get recent market data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        # Fetch S&P 500 data
        ticker = Ticker('^GSPC')
        data = ticker.history(start=start_date, end=end_date)
        
        if data.empty:
            return self._get_default_regime()
        
        # Detect regime using HMM
        regime_result = self.regime_detector.detect_regime(data)
        return regime_result
        
    except Exception as e:
        logger.error(f"Market regime analysis failed: {e}")
        return self._get_default_regime()
```

**Result**: US has standalone regime detection method

---

### Issue 2: Stock Deduplication

**ALL THREE PIPELINES** have the same problem!

#### AU Pipeline
**File**: `overnight_pipeline.py` line 795-821

```python
def _score_opportunities(self, stocks: List[Dict], spi_sentiment: Dict) -> List[Dict]:
    scored_stocks = self.opportunity_scorer.score_opportunities(stocks)
    
    # Sort by score
    scored_stocks.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    return scored_stocks  # NO DEDUPLICATION!
```

#### UK Pipeline
**File**: `uk_overnight_pipeline.py` line 610-630

```python
def _score_opportunities(self, stocks: List[Dict], sentiment: Dict) -> List[Dict]:
    scored_stocks = self.opportunity_scorer.score_opportunities(stocks)
    
    # Sort by score
    scored_stocks.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    return scored_stocks  # NO DEDUPLICATION!
```

#### US Pipeline
**File**: `us_overnight_pipeline.py` line 515-536

```python
def _score_opportunities(self, stocks: List[Dict], sentiment: Dict, regime_data: Dict) -> List[Dict]:
    scored_stocks = self.opportunity_scorer.score_opportunities(stocks)
    
    # Sort by score
    scored_stocks.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    return scored_stocks  # NO DEDUPLICATION!
```

**Result**: All three can produce duplicate stocks in top 5 recommendations

---

## 🔧 Required Fixes

### Fix 1: UK Pipeline - Add Market Regime Extraction

**File**: `uk_overnight_pipeline.py` line 569-591

**Current**:
```python
def _assess_event_risks(self, stocks: List[Dict]) -> Dict:
    results = self.event_guard.assess_batch(tickers)
    
    logger.info(f"[OK] Event Risk Assessment Complete")
    
    return results
```

**Fixed**:
```python
def _assess_event_risks(self, stocks: List[Dict]) -> Dict:
    results = self.event_guard.assess_batch(tickers)
    
    logger.info(f"[OK] Event Risk Assessment Complete")
    
    # FIX v1.3.15.171: Extract and log market regime
    if 'market_regime' in results:
        regime = results['market_regime']
        logger.info(f"  [#] Market Regime: {regime.get('regime_label', 'unknown')}")
        logger.info(f"  [#] Crash Risk: {regime.get('crash_risk_score', 0)*100:.1f}%")
    else:
        logger.warning("  [!] Market regime data not available from EventGuard")
    
    return results  # Now includes market_regime
```

---

### Fix 2: All Pipelines - Add Deduplication

**Files**: 
- `overnight_pipeline.py` (AU) line 795
- `uk_overnight_pipeline.py` line 610
- `us_overnight_pipeline.py` line 515

**Add this method to ALL THREE**:

```python
def _score_opportunities(self, stocks: List[Dict], sentiment: Dict, regime_data: Dict = None) -> List[Dict]:
    """
    Score opportunities and remove duplicates
    
    FIX v1.3.15.171: Added deduplication by symbol
    """
    # Score all stocks
    scored_stocks = self.opportunity_scorer.score_opportunities(stocks)
    
    # FIX v1.3.15.171: Deduplicate by symbol
    seen_symbols = set()
    unique_stocks = []
    duplicates = []
    
    for stock in scored_stocks:
        symbol = stock.get('symbol')
        if symbol and symbol not in seen_symbols:
            seen_symbols.add(symbol)
            unique_stocks.append(stock)
        else:
            duplicates.append(symbol)
    
    if duplicates:
        logger.warning(f"  [!] Removed {len(duplicates)} duplicate stocks: {', '.join(duplicates[:5])}")
    
    logger.info(f"  Unique stocks after deduplication: {len(unique_stocks)}")
    
    # Sort by opportunity score
    unique_stocks.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    return unique_stocks
```

---

### Fix 3: Ensure EventGuard Loads Data Properly

The root cause of "Unknown" regime is likely EventGuard not fetching overnight data.

**File**: Need to check `event_guard.py` or wherever `assess_batch()` is defined

**Current suspected issue**:
```python
def assess_batch(self, tickers):
    # ... assess individual tickers ...
    
    # Market regime calculation
    market_data = None  # ← NOT FETCHING DATA!
    regime = self._calculate_regime(market_data)  # Returns "Unknown"
```

**Should be**:
```python
def assess_batch(self, tickers):
    # ... assess individual tickers ...
    
    # FIX v1.3.15.171: Fetch overnight market data for regime
    market_data = self._fetch_market_data_for_regime()
    regime = self._calculate_regime(market_data)  # Returns real regime
```

---

## 📊 Implementation Priority

### Priority 1: Fix UK Market Regime (HIGH)
- **Impact**: UK reports showing "Unknown" regime
- **Effort**: 5 minutes (add logging + extraction)
- **Files**: 1 file (`uk_overnight_pipeline.py`)

### Priority 2: Add Deduplication (MEDIUM-HIGH)
- **Impact**: All 3 markets showing duplicate stocks
- **Effort**: 15 minutes (add method to 3 files)
- **Files**: 3 files (AU, UK, US pipelines)

### Priority 3: Fix EventGuard Data Fetch (HIGH)
- **Impact**: AU regime also showing "Unknown" sometimes
- **Effort**: 30 minutes (depends on EventGuard structure)
- **Files**: 1-2 files (`event_guard.py` or similar)

---

## ✅ Testing Checklist

After implementing fixes:

### UK Pipeline Test
```bash
python pipelines/run_uk_pipeline.py
```
**Verify**:
- [ ] Market regime NOT "Unknown"
- [ ] Crash risk score NOT 0%
- [ ] Volatility NOT 0.00%
- [ ] No duplicate stocks in top 5

### US Pipeline Test
```bash
python pipelines/run_us_pipeline.py
```
**Verify**:
- [ ] Market regime detected
- [ ] No duplicate stocks in top 5

### AU Pipeline Test
```bash
python pipelines/run_au_pipeline.py
```
**Verify**:
- [ ] Market regime detected (if EventGuard fixed)
- [ ] No duplicate stocks in top 5

---

## 📋 Summary

| Pipeline | Issues Found | Fixes Needed |
|----------|--------------|--------------|
| **AU** | 1. No deduplication<br>2. Regime sometimes "Unknown" | 1. Add dedup<br>2. Fix EventGuard |
| **UK** | 1. No regime extraction<br>2. No deduplication | 1. Add regime logging<br>2. Add dedup |
| **US** | 1. No deduplication | 1. Add dedup |

**Total Fixes**: 3 methods to update across 3 pipelines

**Estimated Time**: 1 hour total
- UK regime: 5 min
- Dedup × 3: 45 min
- EventGuard: 10 min (investigation + fix)

---

*Analysis Date: 2026-02-23*  
*Compared: overnight_pipeline.py vs uk_overnight_pipeline.py vs us_overnight_pipeline.py*
