# Resume Point: Market Timing Fix (v1.3.15.171)

**Date**: 2026-02-23  
**Status**: 21% Complete (3/14 tasks done)  
**Branch**: market-timing-critical-fix  
**Last Commit**: 8ff2704

## Quick Context

You asked me to fix the **2026-02-23 forecast failure** where:
- Forecast: ASX +0.46%, STRONG_BUY, Risk LOW
- Reality: ASX -2.0%, STO.AX -2.67%, ORG.AX -1.23%
- Error: -2.46% (complete directional failure)

Root cause: **Missing market data fetch** → regime detected as "Unknown" → no risk adjustment

## What's Done ✅

### 1. Added MarketDataFetcher Import
**File**: `pipelines/models/screening/overnight_pipeline.py` (lines 81-105)
- Imports `models.market_data_fetcher.MarketDataFetcher`
- Falls back gracefully if not available

### 2. Added _fetch_overnight_market_data() Method
**File**: `pipelines/models/screening/overnight_pipeline.py` (lines 410-475)
- Fetches S&P 500, NASDAQ, oil, AUD/USD, VIX
- Logs all key metrics
- Returns dict with `data_quality` flag

### 3. Added Phase 0.5 to Pipeline
**File**: `pipelines/models/screening/overnight_pipeline.py` (line 263-274)
- Runs BEFORE Phase 1 (market sentiment)
- Calls `_fetch_overnight_market_data()`
- Passes result to `_fetch_market_sentiment(market_data)`

## What's Next ⏳

### Priority 1: Wire market_data to Regime Detector (HIGH)
**Goal**: Make regime detector use the fetched market_data

**Steps**:
1. Update `SPIMonitor.get_overnight_summary()` to accept `market_data` parameter
2. Pass `market_data` to regime detection in `report_generator.py`
3. Update regime calculation to use real US market changes, VIX, commodities

**Expected Result**:
- Regime changes from "Unknown" → "High Risk" / "Neutral" / "Bullish"
- Daily/Annual volatility show real values (not 0%)

**Files to Edit**:
- `pipelines/models/screening/spi_monitor.py`
- `pipelines/models/screening/report_generator.py`

**Time Estimate**: 30-45 minutes

---

### Priority 2: Add Sector-Specific Analysis (HIGH)
**Goal**: Detect weak sectors (e.g., energy) and downgrade stocks in those sectors

**Steps**:
1. Add sector classification to stock metadata
2. Calculate sector performance from market_data (e.g., energy ← oil price)
3. Apply sector multiplier to opportunity scores:
   ```python
   if sector == 'Energy' and market_data['oil_change'] < -2.0:
       opportunity_score *= 0.6  # Downgrade by 40%
   ```
4. Log sector downgrades

**Expected Result**:
- STO.AX and ORG.AX downgraded from top-5 when oil is weak
- Avoids recommending stocks in struggling sectors

**Files to Edit**:
- `pipelines/models/screening/opportunity_scorer.py`
- `pipelines/models/screening/overnight_pipeline.py`

**Time Estimate**: 45-60 minutes

---

### Priority 3: Implement Regime-Aware Gap Damping (HIGH)
**Goal**: Reduce bullish signals in high-risk regimes

**Steps**:
1. Detect regime before calculating gap prediction
2. Apply regime multiplier:
   ```python
   if regime == 'High Risk' and predicted_gap > 0:
       predicted_gap *= 0.3  # Damp by 70%
       confidence *= 0.5
   ```
3. Adjust sentiment thresholds:
   - STRONG_BUY: 70 → 85
   - BUY: 60 → 75
4. Update risk label based on regime + VIX

**Expected Result**:
- On Feb 23: +0.46% gap damped to +0.14%
- Sentiment 76.9 → labeled "BUY" (not STRONG_BUY)
- Risk: "MODERATE-HIGH" (not LOW)

**Files to Edit**:
- `pipelines/models/screening/spi_monitor.py` (gap prediction)
- `pipelines/models/screening/report_generator.py` (thresholds, risk label)

**Time Estimate**: 45-60 minutes

---

### Priority 4: Testing (CRITICAL)
**Goal**: Verify all fixes work end-to-end

**Tests**:
1. Market data fetch test:
   ```bash
   python -c "from pipelines.models.screening.overnight_pipeline import OvernightPipeline; p = OvernightPipeline(); print(p._fetch_overnight_market_data())"
   ```
   Expected: S&P, NASDAQ, oil, AUD/USD, VIX all logged

2. Full pipeline test:
   ```bash
   python pipelines/run_au_pipeline.py
   ```
   Expected: Regime is NOT "Unknown", daily/annual volatility show real values

3. Report check:
   ```bash
   cat reports/screening/au_morning_report.json | grep regime
   ```
   Expected: `"regime": "High Risk"` (not "Unknown")

4. Sector downgrade test:
   - If oil down -2.5%, verify STO.AX/ORG.AX are downgraded

**Time Estimate**: 30 minutes

---

## Total Time to Complete
**Estimated**: 2.5 - 3.5 hours

**Breakdown**:
- Fix 4 (regime wiring): 30-45 min
- Fix 5 (sector analysis): 45-60 min
- Fix 6 (regime damping): 45-60 min
- Testing: 30 min

---

## How to Resume

### Step 1: Review Documentation
```bash
cd /home/user/webapp/deployments/unified_trading_system_v1.3.15.129_COMPLETE
cat FIX_REGIME_DETECTION_v171_INPROGRESS.md
```

This has the **complete implementation plan** with:
- All code changes needed
- Expected before/after behavior
- Testing procedures

### Step 2: Start with Fix 4 (Wire market_data to Regime Detector)

**File to edit**: `pipelines/models/screening/spi_monitor.py`

**Change #1**: Update method signature (line 481)
```python
# OLD:
def get_overnight_summary(self) -> Dict:

# NEW:
def get_overnight_summary(self, market_data: Optional[Dict] = None) -> Dict:
```

**Change #2**: Pass market_data to sentiment calculation (line 488)
```python
# OLD:
sentiment = self.get_market_sentiment()

# NEW:
sentiment = self.get_market_sentiment(market_data)
```

**Change #3**: Update `get_market_sentiment` signature (line 77)
```python
# OLD:
def get_market_sentiment(self) -> Dict:

# NEW:
def get_market_sentiment(self, market_data: Optional[Dict] = None) -> Dict:
```

**Change #4**: Use market_data in sentiment calculation (line 96)
```python
# After calculating sentiment_score, add regime detection:
if market_data and market_data.get('data_quality') == 'live':
    # Calculate regime from market_data
    regime_info = self._detect_regime(market_data, asx_data)
    sentiment['market_regime'] = regime_info
```

**Change #5**: Add `_detect_regime()` method (new, after line 540)
```python
def _detect_regime(self, market_data: Dict, asx_data: Dict) -> Dict:
    """
    Detect market regime from overnight data
    
    Args:
        market_data: Overnight market data (US indices, commodities, FX, rates, VIX)
        asx_data: Current ASX 200 data
        
    Returns:
        Dictionary with regime info
    """
    import math
    
    # Extract data
    vix = market_data.get('vix_level', 15)
    sp500_change = market_data.get('sp500_change', 0)
    asx_vol_7d = abs(asx_data.get('seven_day_change_pct', 0))
    asx_vol_14d = abs(asx_data.get('fourteen_day_change_pct', 0))
    
    # Calculate daily volatility (annualized std dev)
    daily_volatility = asx_vol_7d / math.sqrt(7)  # Simple estimate
    annual_volatility = daily_volatility * math.sqrt(252)
    
    # Calculate crash risk from VIX
    if vix > 30:
        crash_risk = 65
        regime = 'Very High Risk'
    elif vix > 25:
        crash_risk = 50
        regime = 'High Risk'
    elif vix > 20:
        crash_risk = 36
        regime = 'High Risk'
    elif vix > 15:
        crash_risk = 15
        regime = 'Neutral'
    else:
        crash_risk = 5
        regime = 'Bullish'
    
    return {
        'regime': regime,
        'daily_volatility_pct': round(daily_volatility, 2),
        'annual_volatility_pct': round(annual_volatility, 1),
        'crash_risk_pct': crash_risk,
        'vix_level': vix,
        'confidence': 'high' if market_data.get('data_quality') == 'live' else 'low'
    }
```

### Step 3: Test the Changes
```bash
# Run pipeline
python pipelines/run_au_pipeline.py

# Check for "PHASE 0.5: OVERNIGHT MARKET DATA FETCH" in logs
# Verify regime is NOT "Unknown"
```

### Step 4: Continue to Fix 5 (Sector Analysis)
Follow the steps in `FIX_REGIME_DETECTION_v171_INPROGRESS.md` section "Fix 5"

### Step 5: Continue to Fix 6 (Regime Damping)
Follow the steps in `FIX_REGIME_DETECTION_v171_INPROGRESS.md` section "Fix 6"

### Step 6: Final Testing
Run all tests from the testing plan

---

## Expected Results (After All Fixes)

### Feb 23 Scenario
**Market Conditions**:
- US: S&P +0.69%, NASDAQ +0.90%
- Commodities: Oil -2.5%
- FX: AUD/USD -0.3%
- Volatility: VIX 20

**Before v171**:
- Regime: "Unknown"
- Forecast: ASX +0.46%, STRONG_BUY, Risk LOW
- STO.AX: Top-5 BUY (91.6/100)
- Reality: ASX -2.0%, STO.AX -2.67%

**After v171 (Expected)**:
- Regime: "High Risk" (VIX 20, crash risk 36%)
- Market data: ✅ S&P, NASDAQ, oil, AUD/USD all fetched
- Gap: +0.14% (damped from +0.46% by 70%)
- Sentiment: 76.9/100 → "BUY" (not STRONG_BUY)
- Risk: MODERATE-HIGH
- STO.AX: Downgraded to 54.9 (oil -2.5% → 40% downgrade)
- STO.AX: Drops out of top-5
- Forecast error: -0.8% to -1.2% (vs -2.46%)
- Directional accuracy: 50-60% (vs 0%)

---

## Quick Reference

### Files Modified (So Far)
- `pipelines/models/screening/overnight_pipeline.py` (~100 lines added)

### Files To Modify (Next)
1. `pipelines/models/screening/spi_monitor.py` (Fix 4: regime detection)
2. `pipelines/models/screening/report_generator.py` (Fix 4: report regime)
3. `pipelines/models/screening/opportunity_scorer.py` (Fix 5: sector analysis)
4. `pipelines/models/screening/spi_monitor.py` (Fix 6: gap damping)

### Key Documentation
- `FIX_REGIME_DETECTION_v171_INPROGRESS.md` - Complete implementation guide
- `FORECAST_ERROR_ANALYSIS_2026-02-23.md` - Original error analysis
- `FORECAST_MISMATCH_ANALYSIS_2026-02-23.md` - Root cause analysis

### Git
- Branch: market-timing-critical-fix
- Last commit: 8ff2704
- Commit message: "fix(wip): Add market data fetch for regime detection (v1.3.15.171 - 21% complete)"

---

## Contact / Questions
If you have questions when resuming:
1. Read `FIX_REGIME_DETECTION_v171_INPROGRESS.md` for details
2. Check git log for recent changes: `git log --oneline -5`
3. Check what's pending: See "Fixes Pending" section in inprogress doc

**You're 21% done. Next: Wire market_data to regime detector (30-45 min).**

Good luck! 🚀
