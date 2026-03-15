# Trading Decision System - How Sentiment Gates Work

**Your Question**: "What is the platform using to identify if it is appropriate to enter the market? How does it take into account that the market might be dropping or rising?"

---

## Current Sentiment Gating System

### 1. Sentiment Score Calculation (realtime_sentiment.py)

**Formula** (CURRENT - HAS BUG):
```python
sentiment_score = 50 + (pct_change * 10) + (momentum * 5)
# Range: 0-100
```

**Example with AORD -0.9%**:
- If intraday momentum is +3.3%: score = 50 - 9 + 16.5 = **57.5** ❌
- Shows as **SLIGHTLY BULLISH** despite market being down
- **THIS IS THE BUG YOU IDENTIFIED**

---

### 2. Trading Gates (paper_trading_coordinator.py)

The system uses **multiple layers of protection** based on sentiment:

#### **Layer 1: Hard Blocks (No Trading)**

```python
# Block threshold (default 30)
if sentiment_score < 30:
    BLOCK TRADE
    reason: "Sentiment too low"
```

**Current behavior with 66.7 sentiment**: ✅ PASSES (66.7 > 30)

#### **Layer 2: Morning Report Recommendations**

```python
if recommendation == 'STRONG_SELL' or 'AVOID':
    BLOCK TRADE
    
if recommendation == 'SELL' and sentiment_score < 35:
    BLOCK TRADE
    
if recommendation in ['CAUTION', 'HOLD'] and sentiment_score < 45:
    if negative_sentiment > 60%:
        BLOCK TRADE
    elif negative_sentiment > 45%:
        ALLOW WITH CAUTION
```

**Current behavior**: 
- Morning report missing, so these checks are skipped
- With sentiment 66.7, even if report existed, it would ALLOW trading

#### **Layer 3: Position Sizing (BROKEN - Returns 2 values, needs 3)**

```python
def should_allow_trade(self, symbol, signal, sentiment_score) -> (bool, str):
    # Should return: (gate_decision, position_multiplier, reason)
    # Currently returns: (gate_decision, reason)
    # MISSING: position_multiplier
```

**Expected behavior**:
- sentiment < 30: BLOCK, multiplier = 0.0
- sentiment 30-45: REDUCE, multiplier = 0.5 (half size)
- sentiment 45-55: CAUTION, multiplier = 0.75
- sentiment 55-65: ALLOW, multiplier = 1.0
- sentiment > 65: BOOST, multiplier = 1.2

**Current behavior**: ❌ BROKEN - unpacking error

---

## The Problems

### Problem 1: Sentiment Calculation is Wrong
**AORD -0.9%** → shows as **66.7 (BULLISH)**

**Impact**:
- System thinks market is bullish when it's actually bearish
- Allows full-size long positions in falling market
- No defensive reduction in position size

### Problem 2: Position Sizing is Broken
**Method returns 2 values**, calls expect 3

**Impact**:
- All trades fail with "not enough values to unpack"
- No trades are being executed at all

### Problem 3: Missing Market-Specific Context
**Dashboard shows 66.7** but unclear if this is:
- AU-specific (AORD -0.9%)
- Global weighted (US 50%, UK 25%, AU 25%)

**If it's global**: 66.7 might be correct if US/UK are up
**If it's AU-specific**: 66.7 is WRONG for AORD -0.9%

---

## How the System SHOULD Work

### Scenario 1: Strong Bearish Market (AORD -2%)

**Correct Sentiment Score**: ~30-35

**Trading Behavior**:
- ✅ BLOCK all new long positions
- ✅ Or reduce position size to 0.5x (50%)
- ✅ Preserve capital
- ✅ Wait for better conditions

### Scenario 2: Slightly Bearish (AORD -0.9%)

**Correct Sentiment Score**: ~40-45

**Trading Behavior**:
- ✅ CAUTION mode
- ✅ Reduce position size to 0.75x (75%)
- ✅ Only take high-confidence signals (>55%)
- ✅ Defensive positioning

### Scenario 3: Neutral Market (AORD -0.2% to +0.2%)

**Correct Sentiment Score**: ~48-52

**Trading Behavior**:
- ✅ ALLOW normal trading
- ✅ Full position sizes (1.0x)
- ✅ Standard confidence threshold (52%)

### Scenario 4: Bullish Market (AORD +1.5%)

**Correct Sentiment Score**: ~65-70

**Trading Behavior**:
- ✅ BOOST confidence
- ✅ Increase position sizes to 1.2x (120%)
- ✅ More aggressive entry

### Scenario 5: Strong Bullish (AORD +3%)

**Correct Sentiment Score**: ~75-80

**Trading Behavior**:
- ✅ BOOST maximum
- ✅ Position sizes 1.5x (150%)
- ✅ Take advantage of momentum

---

## How Market Drops/Rises Affect Decisions

### Rising Market (+ve momentum):
1. **Sentiment score increases** (50 → 65 → 75)
2. **Position multiplier increases** (0.75 → 1.0 → 1.2)
3. **More trades allowed** (confidence threshold relaxed)
4. **System becomes more aggressive**

### Falling Market (-ve momentum):
1. **Sentiment score decreases** (50 → 40 → 30)
2. **Position multiplier decreases** (1.0 → 0.75 → 0.5 → 0.0)
3. **Fewer trades allowed** (confidence threshold raised)
4. **System becomes defensive**

### Sideways Market (flat):
1. **Sentiment stays neutral** (~50)
2. **Normal position sizes** (1.0x)
3. **Standard rules apply**

---

## The Fixes Needed

### Fix 1: Sentiment Calculation (CRITICAL)

**Current formula**:
```python
score = 50 + (pct_change * 10) + (momentum * 5)
```

**Proposed fix** (Option A - recommended):
```python
# Daily close is primary signal
base_score = 50 + (pct_change * 15)

# Momentum provides context but bounded to ±5 points
momentum_modifier = max(-5, min(5, momentum * 2))

final_score = base_score + momentum_modifier
final_score = max(0, min(100, final_score))
```

**With AORD -0.9%**:
```
base_score = 50 + (-0.9 * 15) = 36.5
momentum_modifier = +5 (best case)
final_score = 36.5 + 5 = 41.5
Label: SLIGHTLY BEARISH ✓
Position multiplier: 0.75x (defensive)
```

### Fix 2: Position Multiplier (CRITICAL)

**Add position_multiplier to return value**:
```python
def should_allow_trade(self, symbol: str, signal: Dict, sentiment_score: float) -> Tuple[bool, float, str]:
    """
    Returns:
        - gate_decision (bool): Allow trade?
        - position_multiplier (float): 0.0 to 1.5
        - reason (str): Explanation
    """
    
    # Calculate position multiplier based on sentiment
    if sentiment_score < 30:
        return False, 0.0, "Sentiment too low (BLOCK)"
    elif sentiment_score < 45:
        return True, 0.5, "Bearish sentiment (REDUCE 50%)"
    elif sentiment_score < 55:
        return True, 0.75, "Neutral sentiment (REDUCE 25%)"
    elif sentiment_score < 65:
        return True, 1.0, "Normal sentiment"
    elif sentiment_score < 75:
        return True, 1.2, "Bullish sentiment (BOOST 20%)"
    else:
        return True, 1.5, "Strong bullish (BOOST 50%)"
```

### Fix 3: Market-Specific Display

**Show which market** the sentiment refers to:
```
Market Sentiment: 66.7 (BULLISH)
Source: GLOBAL (US 50%, UK 25%, AU 25%)

AU Market: 42 (SLIGHTLY BEARISH) - AORD -0.9%
US Market: 72 (BULLISH) - S&P +1.2%
UK Market: 68 (BULLISH) - FTSE +0.8%
```

This way you know if you're seeing global or market-specific sentiment.

---

## Recommended Fix Package

### v1.3.15.52 Should Include:

1. **Fixed sentiment formula** (daily close priority)
2. **Fixed position multiplier** (3-value return)
3. **Market-specific display** (show AU vs global)
4. **FinBERT local cache** (already done in v1.3.15.51)

### Expected Results After Fix:

With **AORD -0.9%**:
- Sentiment score: **~42** (not 66.7)
- Label: **SLIGHTLY BEARISH** (not BULLISH)
- Position multiplier: **0.75x** (defensive)
- Trading: **CAUTION mode** (reduced sizing)

With **AORD +1.5%**:
- Sentiment score: **~70**
- Label: **BULLISH**
- Position multiplier: **1.2x** (aggressive)
- Trading: **BOOST mode** (larger positions)

---

## Your Questions Answered

### Q: "What is the platform using to identify if it is appropriate to enter the market?"

**A**: Multi-layer system:
1. **Sentiment score** (0-100) from market data
2. **Morning report recommendation** (SELL/HOLD/BUY)
3. **Signal confidence** (technical analysis)
4. **Hard sentiment threshold** (default 30)
5. **Position multiplier** (adjusts size based on conditions)

### Q: "How does it take into account that the market might be dropping or rising?"

**A**: 
- **Dropping market**: Sentiment score decreases → smaller positions or blocking
- **Rising market**: Sentiment score increases → larger positions and more aggressive
- **Formula weights daily close more than intraday momentum** (when fixed)

---

## What Should I Fix First?

**Priority 1** (CRITICAL - stops all trading):
- Fix position_multiplier return value (3 values not 2)

**Priority 2** (CRITICAL - wrong decisions):
- Fix sentiment calculation formula (daily close priority)

**Priority 3** (IMPORTANT - clarity):
- Show market-specific vs global sentiment

**All three can be done in v1.3.15.52**

Do you want me to implement all three fixes now?
