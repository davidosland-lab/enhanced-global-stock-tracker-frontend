# Root Cause Analysis: Financial Stocks Bought During Risk-Off Environment
## March 4, 2026 - Post-Mortem

### Executive Summary
The trading system purchased 3 financial stocks (BP.L, BOQ.AX, NAB.AX) on March 4, 2026 despite:
- **World Event Risk: 100/100** (EXTREME - nuclear threat)
- **US Market Performance: -2.47% to -2.74%** (S&P, NASDAQ)
- **VIX: 59.3** (elevated fear index)
- **AU Sentiment: 42.1/100** (WEAK)
- **US Sentiment: 100% negative** according to user logs

**Result:** All 3 positions underwater, portfolio down -0.56% ($556 loss on $100k)

### The Dashboard Evidence (from screenshot)
```
Portfolio Value: $99,443.94 (-0.56%)
Open Positions: 3
FinBERT Sentiment: -33% negative, 0% neutral, -16% positive
Market Sentiment: 53.7 / 100 (NEUTRAL) ← INCORRECT, should be ~42

Open Positions:
- BP.L: 38 shares @ $493.00, P&L: 0.00%
- BOQ.AX: 2,179 shares @ $6.99, P&L: -2.36%
- NAB.AX: 259 shares @ $47.64, P&L: -1.22%
```

### Root Cause #1: FinBERT Sentiment Failure
**Problem:** All three stocks returned FinBERT sentiment = 0.000 (neutral)
```python
# From logs:
BP.L FinBERT: 0.000 (should be negative given market conditions)
BOQ.AX FinBERT: 0.000 (should be negative - Australian bank during crisis)
NAB.AX FinBERT: 0.000 (should be negative - Australian bank during crisis)
```

**Impact:** The system had NO stock-level sentiment data to guide decisions. It was trading blind.

**Why this happened:**
1. FinBERT model either not loaded or returning default neutral scores
2. No fallback to macro sentiment when FinBERT fails
3. No validation that sentiment scores are realistic

### Root Cause #2: No Macro Risk Gates
**Problem:** The system has MacroRiskGatekeeper code but it's NOT INTEGRATED into paper_trading_coordinator.py

**Evidence:**
```bash
$ grep -n "macro_risk_gates\|MacroRiskGatekeeper" core/paper_trading_coordinator.py
# Returns: NO RESULTS - not imported or used
```

**What should have happened:**
```python
# In should_allow_trade() method:
gatekeeper = MacroRiskGatekeeper()
allow, multiplier, reason = gatekeeper.should_allow_new_position(
    symbol=symbol,
    signal=signal,
    confidence=confidence,
    world_risk_score=100,  # From morning report
    us_market_change=-2.47,  # S&P 500 overnight
    vix=59.3
)

# Would have returned:
# BP.L: (False, 0.0, "🚫 EXTREME WORLD RISK: 100/100 >= 80 - NO NEW POSITIONS")
# BOQ.AX: (False, 0.0, "🚫 EXTREME WORLD RISK: 100/100 >= 80 - NO NEW POSITIONS")
# NAB.AX: (False, 0.0, "🚫 EXTREME WORLD RISK: 100/100 >= 80 - NO NEW POSITIONS")
```

### Root Cause #3: Ignored Macro Context
**Problem:** The `should_allow_trade` method only checks:
1. Morning report recommendation (CAUTION/HOLD - not strong enough)
2. Sentiment score threshold (42.1 > 30 = PASS - too lenient)
3. Signal confidence (~50% - too low for high risk)

**Missing checks:**
- ❌ World Event Risk score
- ❌ US overnight market performance
- ❌ VIX volatility index
- ❌ Sector-specific rules (financials = high beta)

### Root Cause #4: Insufficient LSTM Data
**Warning logs:**
```
BP.L: LSTM score 0.190, WARNING: Only 43 days of data (need 60+)
BOQ.AX: LSTM score -0.031, WARNING: Only 55 days of data (need 60+)
NAB.AX: LSTM score 0.148, WARNING: Only 52 days of data (need 60+)
```

**Impact:** LSTM predictions unreliable, but system accepted them anyway.

### Root Cause #5: Low Confidence Accepted During Extreme Risk
**Confidence scores:**
- BP.L: 54.24% confidence
- BOQ.AX: 50.33% confidence
- NAB.AX: 50.15% confidence

**Problem:** During World Risk 100/100 with VIX 59.3, the system should require ≥75% confidence. Instead, it accepted ~50% confidence.

### Root Cause #6: No Sector-Specific Rules
**Financial sector characteristics:**
- **High beta:** 0.80-0.90 (move more than market)
- **Credit risk:** Exposed during geopolitical crises
- **Sentiment-driven:** Highly correlated with market fear

**What should have happened:**
```python
if symbol in ['BP.L', 'BOQ.AX', 'NAB.AX', 'CBA.AX', 'LLOY.L', ...]:
    # Financial sector - stricter rules during risk-off
    if world_risk > 60:
        return False, 0.0, "No financials during elevated world risk"
    if us_market_change < -1.0:
        return False, 0.0, "No financials during US market weakness"
```

### Root Cause #7: Volume Weakness Ignored
**Volume indicators:**
```
BP.L: Volume score 0.333 (weak)
BOQ.AX: Volume score 0.400 (weak)
NAB.AX: Volume score 0.400 (weak)
```

**Problem:** Low volume suggests lack of conviction, but system ignored this signal.

---

## Recommended Fixes (Priority Order)

### CRITICAL: Implement Macro Risk Gates (Week 1)
**File:** `core/paper_trading_coordinator.py`

```python
# 1. Add import at top
from core.macro_risk_gates import MacroRiskGatekeeper

# 2. Initialize in __init__
self.risk_gatekeeper = MacroRiskGatekeeper(
    world_risk_threshold=80,
    us_market_threshold=-1.5,
    vix_threshold=30.0,
    financial_world_risk_threshold=60,
    financial_us_market_threshold=-1.0
)

# 3. Add macro checks in should_allow_trade() BEFORE existing checks
def should_allow_trade(self, symbol: str, signal: Dict, sentiment_score: float):
    # NEW: Macro risk gates (HIGHEST PRIORITY)
    world_risk = self._get_world_risk_from_report()
    us_change = self._get_us_overnight_performance()
    vix = self._get_vix_from_report()
    confidence = signal.get('confidence', 0) / 100.0
    
    allow, multiplier, reason = self.risk_gatekeeper.should_allow_new_position(
        symbol=symbol,
        signal=signal,
        confidence=confidence,
        world_risk_score=world_risk,
        us_market_change=us_change,
        vix=vix
    )
    
    if not allow:
        logger.warning(f"[MACRO BLOCK] {symbol}: {reason}")
        return False, 0.0, reason
    
    # Apply position multiplier from macro gates
    position_multiplier = multiplier
    
    # ... existing sentiment checks ...
    # (multiply final position_multiplier by sentiment multiplier)
```

### CRITICAL: Fix FinBERT Fallback (Week 1)
**File:** `ml_pipeline/swing_signal_generator.py`

```python
def _compute_sentiment_score(self, symbol, news_df, current_date):
    """Compute sentiment with macro fallback"""
    
    # Try FinBERT first
    sentiment = self._get_finbert_sentiment(news_df)
    
    # If FinBERT fails (returns 0.000 or None)
    if sentiment is None or abs(sentiment) < 0.01:
        logger.warning(f"{symbol}: FinBERT failed, using macro sentiment fallback")
        
        # Get macro sentiment from morning report
        macro_sentiment = self._get_macro_sentiment_from_report()
        
        # Apply sector weighting
        if self._is_financial_sector(symbol):
            # Financials are 1.3x more sensitive to macro sentiment
            sentiment = macro_sentiment * 1.3
        else:
            sentiment = macro_sentiment
        
        logger.info(f"{symbol}: Fallback sentiment = {sentiment:.3f} (from macro)")
    
    return sentiment
```

### HIGH: Add Confidence Penalties (Week 1)
**File:** `ml_pipeline/swing_signal_generator.py`

```python
def generate_signal(self, symbol, price_df, news_df=None, current_date=None):
    # ... existing component calculations ...
    
    # Calculate base confidence
    combined_score = (sentiment * w1) + (lstm * w2) + (technical * w3) + ...
    base_confidence = self._calculate_confidence(combined_score)
    
    # Apply confidence penalties for data quality issues
    penalties = []
    
    # Penalty 1: Insufficient LSTM data
    if len(price_df) < 60:
        penalties.append(('LSTM_DATA', -20))  # -20% confidence
    
    # Penalty 2: Missing sentiment
    if sentiment_score == 0.000:
        penalties.append(('NO_SENTIMENT', -15))  # -15% confidence
    
    # Penalty 3: Weak volume
    if volume_score < 0.5:
        penalties.append(('WEAK_VOLUME', -10))  # -10% confidence
    
    # Apply penalties
    adjusted_confidence = base_confidence
    for penalty_name, penalty_amount in penalties:
        adjusted_confidence += penalty_amount
        logger.warning(f"{symbol}: Applied {penalty_name} penalty: {penalty_amount}%")
    
    # Ensure confidence stays in valid range
    adjusted_confidence = max(0, min(100, adjusted_confidence))
    
    return {
        'prediction': prediction,
        'confidence': adjusted_confidence,
        'base_confidence': base_confidence,
        'penalties': penalties,
        ...
    }
```

### HIGH: Dynamic Position Sizing (Week 2)
**File:** `core/paper_trading_coordinator.py`

```python
def _calculate_position_size(self, symbol, signal, sentiment_score):
    """Calculate position size with risk adjustments"""
    
    # Base position size (25% of capital for 4 positions)
    base_size = self.capital.cash * 0.25
    
    # Get macro context
    world_risk = self._get_world_risk_from_report()
    us_change = self._get_us_overnight_performance()
    vix = self._get_vix_from_report()
    
    # Risk adjustments
    multiplier = 1.0
    
    # World risk adjustment
    if world_risk >= 80:
        multiplier *= 0.0  # No positions
    elif world_risk >= 60:
        multiplier *= 0.50  # Half size
    elif world_risk >= 50:
        multiplier *= 0.75  # 3/4 size
    
    # US market adjustment
    if us_change <= -2.0:
        multiplier *= 0.0
    elif us_change <= -1.5:
        multiplier *= 0.50
    elif us_change <= -1.0:
        multiplier *= 0.75
    
    # VIX adjustment
    if vix >= 40:
        multiplier *= 0.50
    elif vix >= 30:
        multiplier *= 0.75
    
    # Sector adjustment
    if self._is_financial_sector(symbol):
        if world_risk >= 50 or us_change <= -0.5:
            multiplier *= 0.70  # Additional 30% reduction
    
    # Apply multiplier
    adjusted_size = base_size * multiplier
    
    logger.info(f"{symbol}: Position sizing - base=${base_size:.0f}, "
                f"adjusted=${adjusted_size:.0f} (multiplier={multiplier:.2f})")
    
    return adjusted_size
```

### MEDIUM: Minimum Data Quality (Week 2)
**File:** `ml_pipeline/swing_signal_generator.py`

```python
def generate_signal(self, symbol, price_df, news_df=None, current_date=None):
    # Data quality checks at start
    
    # Minimum price data requirement
    if len(price_df) < 60:
        logger.warning(f"{symbol}: Insufficient data ({len(price_df)} days < 60), "
                       f"returning HOLD with low confidence")
        return self._generate_hold_signal(
            f"Insufficient historical data ({len(price_df)} days)",
            confidence=20.0  # Very low confidence
        )
    
    # Sentiment requirement for financials during risk-off
    if self._is_financial_sector(symbol):
        world_risk = self._get_world_risk_from_report()
        if world_risk >= 50:
            # Require valid sentiment for financials during elevated risk
            sentiment = self._compute_sentiment_score(symbol, news_df, current_date)
            if sentiment is None or abs(sentiment) < 0.01:
                logger.warning(f"{symbol}: Financial sector + high risk requires sentiment data")
                return self._generate_hold_signal(
                    "Financial sector requires sentiment during elevated risk",
                    confidence=0.0
                )
    
    # ... continue with normal signal generation ...
```

---

## Impact Analysis

### Current State (No Fixes)
```
Portfolio Value: $99,443.94
Loss: -$556 (-0.56%)
Open Positions: 3 (all losing)
Risk Exposure: HIGH (financials during crisis)
```

### With Fixes Implemented
```
March 4, 2026 Morning:
- World Risk: 100/100 detected
- US Market: -2.47% detected
- VIX: 59.3 detected

BP.L Signal Generated:
- Base confidence: 54.24%
- Penalties: -20% (LSTM data), -15% (no sentiment) = 19.24%
- Macro gates: BLOCKED (World Risk 100 >= 80)
- Result: NO TRADE

BOQ.AX Signal Generated:
- Base confidence: 50.33%
- Penalties: -20% (LSTM data), -15% (no sentiment) = 15.33%
- Macro gates: BLOCKED (World Risk 100 >= 80 AND Financial sector)
- Result: NO TRADE

NAB.AX Signal Generated:
- Base confidence: 50.15%
- Penalties: -20% (LSTM data), -15% (no sentiment) = 15.15%
- Macro gates: BLOCKED (World Risk 100 >= 80 AND Financial sector)
- Result: NO TRADE

Portfolio Value: $100,000.00
Loss: $0.00 (0.00%)
Open Positions: 0
Risk Exposure: NONE (cash is safe)
```

**Projected Benefit:** +$556 preserved (avoided -0.56% loss)

---

## Immediate Actions Required

### TODAY (March 4, 2026)
1. **Exit all 3 losing positions** (BP.L, BOQ.AX, NAB.AX)
   - Current loss: ~$556
   - Prevent further losses if market deteriorates
   
2. **Stay in CASH** until conditions improve:
   - World Risk < 60/100
   - US market stabilizes (positive close)
   - VIX < 30

3. **Suspend financial sector buys** until:
   - World Risk < 50/100
   - US market shows strength (+0.5% or better)
   - Valid FinBERT sentiment available

### THIS WEEK
1. Integrate MacroRiskGatekeeper into paper_trading_coordinator.py
2. Fix FinBERT fallback to use macro sentiment
3. Add confidence penalties for missing data
4. Test with March 4 scenario (should block all 3 trades)

### NEXT WEEK
1. Implement dynamic position sizing
2. Add minimum data quality requirements
3. Backtest with historical crisis periods:
   - Feb 24, 2022 (Ukraine invasion)
   - Mar 12, 2020 (COVID crash)
   - Aug 5, 2024 (Flash crash)

---

## Lessons Learned

### Key Takeaway
**Never buy high-beta financials during extreme risk without:**
1. Valid sentiment data (FinBERT or fallback)
2. High confidence (≥75% during crises)
3. Sufficient historical data (≥60 days LSTM)
4. Macro risk gate approval (World Risk, US performance, VIX)

### System Improvements
The trading system is only as good as its risk management. This incident revealed 7 critical gaps:
1. FinBERT failure without fallback
2. No macro risk gates integration
3. Ignored US overnight performance
4. Low confidence accepted during high risk
5. No volume weakness consideration
6. Insufficient data accepted
7. No sector-specific rules

**All 7 gaps are now documented and fixable within 1-2 weeks.**

---

## Conclusion
The March 4, 2026 financial sector buys were a **perfect storm of failures**:
- Blind sentiment (FinBERT = 0.000)
- Ignored macro context (World Risk 100, US -2.5%, VIX 59)
- Low confidence accepted (~50%)
- Insufficient data (43-55 days)
- No sector rules (financials = high beta)

**Root cause:** MacroRiskGatekeeper exists but is NOT integrated into trading logic.

**Fix:** Integrate the 4 macro gates and FinBERT fallback. Test thoroughly before resuming trading.

**Expected outcome:** Zero trades on March 4 = $556 preserved + avoided potential further losses.

---
*Analysis completed: March 4, 2026*
*Next review: After implementation of critical fixes*
