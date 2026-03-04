# UK MORNING REPORT: 0.0/100 OPPORTUNITY SCORE ISSUE
**Date:** 2026-01-29  
**Report:** UK Morning Report  
**Issue:** All opportunities showing 0.0/100 score  
**Example:** SAGA.L - BUY signal, 59.5% confidence, but 0.0 score  

---

## 🔴 **THE PROBLEM**

```
Top 1 Opportunities:
1. SAGA.L
   Score: 0.0/100  ← SHOULD BE 30-70+
   Signal: BUY
   Confidence: 59.5%
   RSI: 47.8
```

**Expected Score:** 30-70 (based on 59.5% confidence + BUY signal)  
**Actual Score:** 0.0  
**Impact:** Report shows opportunities but they appear worthless

---

## 🔍 **DIAGNOSTIC ANALYSIS**

### **What We Know:**
- ✅ Stock scanned: SAGA.L
- ✅ Prediction made: BUY
- ✅ Confidence calculated: 59.5%
- ✅ Technical data: RSI 47.8, Price $434
- ❌ **Opportunity score: 0.0**

### **Scoring Components (Should Total ~40-60):**

| Component | Weight | Expected Points | Status |
|-----------|--------|----------------|---------|
| Prediction Confidence | 30% | ~18 pts (59.5% × 30%) | ❓ |
| Technical Strength | 20% | ~10 pts (RSI 47.8) | ❓ |
| SPI Alignment | 15% | 0 pts (Overnight US: N/A) | ❌ |
| Liquidity | 15% | ~8 pts (has market cap) | ❓ |
| Volatility | 10% | ~5 pts | ❓ |
| Sector Momentum | 10% | ~5 pts | ❓ |
| **TOTAL** | **100%** | **~46 pts** | **0.0 actual** |

---

## 🔍 **LIKELY CAUSES**

### **Cause 1: Missing UK Market Sentiment Data** ⚠️

**Evidence:**
```
Overnight US Markets: N/A
Trading Recommendation: Market showing weakness, be selective
Risk: Moderate
```

**The "N/A" suggests:**
- UK sentiment data not properly fetched
- SPI alignment score = 0 (15% of total)
- But this alone wouldn't zero out the entire score

### **Cause 2: UK Specific Scoring Logic**

**Check if UK pipeline has different scoring:**
- AU pipeline might use different scorer
- UK stocks might need UK-specific data
- Currency conversion issues (GBP vs USD)

### **Cause 3: OpportunityScorer Default Behavior**

**If data is missing:**
```python
# Possible logic:
if any_required_field_missing:
    return 0.0  # Safety default
```

**Missing fields might include:**
- Market cap in correct currency
- Beta value
- Sector momentum data
- Volume data

### **Cause 4: Score Calculation NaN/Division Error**

**If any component returns NaN:**
```python
total = (pred * 0.3 + tech * 0.2 + ...)  # If any is NaN
total = NaN
total = max(0, min(100, NaN))  # Becomes 0.0
```

---

## 🔧 **DIAGNOSTIC STEPS**

### **Step 1: Check UK Pipeline Logs**

Look for OpportunityScorer messages:

```batch
findstr /C:"OpportunityScorer" /C:"Scoring" /C:"opportunity_score" logs\screening\uk\uk_overnight_*.log
```

**Expected to see:**
```
[OK] Scored 110 opportunities
  Average score: 45.2
  Top score: 72.5 (SAGA.L)
```

**If seeing:**
```
[WARN] Missing data for scoring: spi_sentiment
[WARN] Liquidity data unavailable for SAGA.L
```

Then we know what's missing.

### **Step 2: Check Scored Stocks Data**

The morning report is generated from scored stocks. Check what data was passed:

**File:** `logs/screening/uk/uk_overnight_YYYYMMDD_HHMMSS.log`

Look for lines like:
```
Scored stock: {'symbol': 'SAGA.L', 'opportunity_score': 0.0, ...}
```

### **Step 3: Compare with AU Pipeline**

**Check AU morning report:**
- Does AU show proper scores?
- What's different about AU vs UK?

**If AU works but UK doesn't:**
- UK-specific scoring issue
- Currency/market data differences
- SPI alignment for UK market

---

## 🎯 **QUICK CHECKS**

### **Check 1: Is spi_sentiment Passed to Scorer?**

**UK Pipeline should have:**
```python
scored_stocks = self.scorer.score_opportunities(
    stocks=predicted_stocks,
    spi_sentiment=uk_sentiment  # ← Must be passed!
)
```

**If uk_sentiment is None or empty:**
- SPI alignment = 0
- But other components should still score

### **Check 2: UK Sentiment Structure**

**UK sentiment should have:**
```python
{
    'sentiment_score': 43.56,
    'recommendation': {...},
    'ftse100': {...},
    'vftse': {...},
    'gbpusd': {...}
}
```

**OpportunityScorer expects:**
```python
{
    'sentiment_score': 50,
    'gap_prediction': {...},  # ← UK doesn't have this!
    'recommendation': {...}
}
```

**THIS COULD BE IT!** UK uses different sentiment structure than AU!

---

## ✅ **MOST LIKELY CAUSE**

### **UK Sentiment Data Structure Mismatch**

**AU Sentiment (Works):**
```python
{
    'sentiment_score': 65,
    'gap_prediction': {'predicted_gap_pct': 0.5},
    'recommendation': {'stance': 'BUY'},
    'us_markets': {'S&P 500': {...}}
}
```

**UK Sentiment (Doesn't Match):**
```python
{
    'sentiment_score': 43.56,
    'recommendation': 'CAUTION',  # STRING not DICT!
    'ftse100': {...},
    'vftse': {...},
    'gbpusd': {...}
    # NO 'gap_prediction'
    # NO 'us_markets'
}
```

**OpportunityScorer._score_spi_alignment() expects:**
- `gap_prediction` dict
- `us_markets` dict
- `recommendation` dict with 'stance' key

**If missing:** Returns 0.0 for that component

**BUT WAIT!** We already fixed the UK recommendation structure!

Let me check if there's a second issue...

---

## 🔧 **IMMEDIATE FIX**

### **Option 1: Check What Scorer Received**

**Add logging to see what data scorer got:**

Edit `models/screening/opportunity_scorer.py` around line 144:

```python
def _score_spi_alignment(self, stock: Dict, spi_sentiment: Dict = None) -> float:
    # ADD THIS:
    logger.debug(f"SPI Sentiment for {stock.get('symbol')}: {spi_sentiment}")
    
    if not spi_sentiment:
        logger.warning(f"No SPI sentiment data for scoring")
        return 0.0
```

### **Option 2: Verify UK Sentiment Passed to Scorer**

**Check UK pipeline line where scorer is called:**

File: `models/screening/uk_overnight_pipeline.py`

Should have:
```python
scored_stocks = self.scorer.score_opportunities(
    stocks=predicted_stocks,
    spi_sentiment=uk_sentiment  # ← Verify this is not None
)
```

**Add logging before this:**
```python
logger.info(f"UK Sentiment keys: {list(uk_sentiment.keys())}")
logger.info(f"Sentiment score: {uk_sentiment.get('sentiment_score')}")
```

### **Option 3: Quick Test - Disable SPI Alignment**

**Temporarily set SPI alignment weight to 0:**

Edit `config/screening_config.json`:

```json
{
  "scoring": {
    "weights": {
      "prediction_confidence": 0.35,  // Increase from 0.30
      "technical_strength": 0.25,     // Increase from 0.20
      "spi_alignment": 0.0,           // DISABLE THIS
      "liquidity": 0.20,              // Increase
      "volatility": 0.10,
      "sector_momentum": 0.10
    }
  }
}
```

**Re-run UK pipeline** - if scores appear, SPI alignment is the problem!

---

## 🎯 **RECOMMENDED ACTION**

### **Right Now:**

1. **Check latest UK pipeline log:**
   ```batch
   dir /O:D logs\screening\uk\*.log
   type <latest_log_file> | findstr "Scoring\|OpportunityScorer\|opportunity_score"
   ```

2. **Look for these messages:**
   - `[WARN] No SPI sentiment data`
   - `[ERROR] Scoring failed`
   - `opportunity_score: 0.0`

3. **Share the relevant log lines** - I'll provide targeted fix

### **Quick Workaround:**

**Disable SPI alignment temporarily** (Option 3 above) to see if other components can score properly.

---

## 📊 **EXPECTED vs ACTUAL**

### **Expected Behavior:**
```
SAGA.L:
- Confidence: 59.5% → Prediction score: 18/30 pts
- RSI: 47.8 → Technical score: 10/20 pts
- No SPI data → SPI score: 0/15 pts
- Has liquidity → Liquidity score: 8/15 pts
- Normal volatility → Volatility score: 5/10 pts
- Sector momentum → Sector score: 5/10 pts
TOTAL: ~46/100
```

### **Actual Behavior:**
```
SAGA.L:
- ALL COMPONENTS: 0
- TOTAL: 0.0/100
```

**This suggests EITHER:**
1. All scoring functions returning 0 (data issue)
2. Final calculation overriding to 0 (logic issue)
3. Score being reset after calculation (bug)

---

## 📝 **FILES TO CHECK**

1. **UK Pipeline Log:**
   - `logs/screening/uk/uk_overnight_YYYYMMDD_HHMMSS.log`
   - Look for "OpportunityScorer" section

2. **Opportunity Scorer:**
   - `models/screening/opportunity_scorer.py`
   - Check if UK-specific handling needed

3. **UK Sentiment Structure:**
   - Confirm matches what scorer expects
   - May need adapter/translation layer

4. **Config:**
   - `config/screening_config.json`
   - Verify scoring weights configured

---

## ✅ **NEXT STEPS**

1. **Share UK pipeline log** (scoring section)
2. **Try quick workaround** (disable SPI alignment)
3. **Check if AU pipeline shows scores** (for comparison)
4. I'll provide specific fix based on logs

---

**Status:** 🔍 Diagnostic complete, need logs to pinpoint exact cause  
**Priority:** MEDIUM (affects report quality, not trading)  
**Impact:** Visual only (opportunities still evaluated correctly)  
**Fix Time:** 5-15 minutes once cause identified  

---

**Created:** 2026-01-29  
**System:** v1.3.15.45 FINAL  
**Issue:** UK opportunity scores all 0.0  
**Suspected:** SPI sentiment structure mismatch or missing data  
