# Trading Dashboard Signal Generation Error Fix

**Date**: 2026-02-16  
**Component**: Unified Trading Dashboard  
**Error**: SwingSignalGenerator method name mismatch

---

## Error Analysis

### Error Message
```
ERROR - [X] Failed to generate ML signal for HSBA.L: 'SwingSignalGenerator' object has no attribute 'generate_swing_signal'
ERROR - Error generating signal for HSBA.L: 'float' object is not subscriptable
```

### Root Cause

**File**: `scripts/pipeline_signal_adapter_v3.py`  
**Line**: 258

**Incorrect Code:**
```python
signal = self.swing_signal_generator.generate_swing_signal(symbol, price_data)
```

**Issue**: The `SwingSignalGenerator` class has a method called `generate_signal()`, NOT `generate_swing_signal()`.

### Correct Method Name

Looking at `ml_pipeline/swing_signal_generator.py`:

```python
class SwingSignalGenerator:
    def generate_signal(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        news_data: Optional[pd.DataFrame] = None,
        current_date: Optional[datetime] = None
    ) -> Dict:
        """Generate trading signal..."""
```

**Note**: There IS a module-level function called `generate_swing_signal()` (line 702), but it's NOT a class method!

---

## Fix Required

### Change in `scripts/pipeline_signal_adapter_v3.py` Line 258

**Before:**
```python
signal = self.swing_signal_generator.generate_swing_signal(symbol, price_data)
```

**After:**
```python
signal = self.swing_signal_generator.generate_signal(symbol, price_data)
```

---

## Impact

### Current Behavior (BROKEN)
- Dashboard fails to generate signals for UK stocks
- Error: `'SwingSignalGenerator' object has no attribute 'generate_swing_signal'`
- Fallback error: `'float' object is not subscriptable` (because signal is None)
- Users cannot get trading recommendations

### Expected Behavior (AFTER FIX)
- Dashboard successfully generates ML signals
- Users see trading recommendations with confidence scores
- Signal combines:
  - FinBERT Sentiment (25%)
  - LSTM Neural Network (25%)
  - Technical Analysis (25%)
  - Momentum Analysis (15%)
  - Volume Analysis (10%)

---

## Related Context

### This is a DIFFERENT Error from the Pipeline Issue

1. **Pipeline LSTM Error** (FIXED in v1.3.15.151):
   - Error: `'FinBERTSentimentAnalyzer' object has no attribute 'get_mock_sentiment'`
   - Location: `finbert_v4.4.4/models/lstm_predictor.py` line 487
   - Status: ✅ FIXED

2. **Dashboard Signal Error** (THIS ISSUE):
   - Error: `'SwingSignalGenerator' object has no attribute 'generate_swing_signal'`
   - Location: `scripts/pipeline_signal_adapter_v3.py` line 258
   - Status: ❌ NEEDS FIX

### Both Affect Different Components

| Component | Issue | Status |
|-----------|-------|--------|
| **Overnight Pipeline** | LSTM get_mock_sentiment() | ✅ Fixed v1.3.15.151 |
| **Trading Dashboard** | Signal method name | ❌ Needs fix |

---

## Testing After Fix

### Test Signal Generation
```python
# In trading dashboard
symbol = "HSBA.L"
# Should see:
# [OK] ML Signal for HSBA.L: 0.75 (conf: 68%)
# Instead of:
# [X] Failed to generate ML signal for HSBA.L
```

### Expected Log Output
```
INFO - [OK] Fetched 63 days of data for HSBA.L (yahooquery)
INFO - [ADAPTER] Generating ENHANCED signal for HSBA.L (75-85% target)
INFO - [OK] ML Signal for HSBA.L: BUY (conf: 68%)
INFO - [OK] Combined signal: STRONG_BUY (overnight + ML)
```

---

## Recommendation

This is a simple method name typo that needs to be fixed in the trading dashboard code. It's separate from the LSTM pipeline fix.

### Priority
- **Medium**: Affects trading dashboard functionality
- Does NOT affect overnight pipeline (different component)
- Users can still view scanned stocks, just can't generate new signals

### Fix Complexity
- **Simple**: One-line change (method name)
- No architecture changes needed
- No data structure changes

---

**Status**: Identified, ready to fix  
**Component**: Trading Dashboard Signal Generator  
**Fix**: Change `generate_swing_signal()` → `generate_signal()`  
**Location**: `scripts/pipeline_signal_adapter_v3.py` line 258
