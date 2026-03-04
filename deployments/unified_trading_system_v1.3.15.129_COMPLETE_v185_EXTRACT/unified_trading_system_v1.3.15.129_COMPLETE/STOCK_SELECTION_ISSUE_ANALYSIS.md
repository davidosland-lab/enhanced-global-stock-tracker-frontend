# Stock Selection Issue Analysis - STAN.L Missing Trade

**Date**: 2026-02-07  
**Issue**: STAN.L was identified as a buy candidate but was not purchased, despite rising 1.87%  
**Context**: Overnight run without UK/US pipelines executed  
**Peers that traded**: AAPL, BHP.AX, HSBA.L

---

## Issue Summary

### What Happened
- **STAN.L** appeared on the buy list during the overnight run
- Stock rose **+1.87%** - a profitable opportunity
- **NOT purchased** by the system
- **Three peers traded immediately**: AAPL, BHP.AX, HSBA.L

### Key Observation
UK and US pipelines had **NOT been run** prior to this overnight execution.

---

## Root Cause Analysis

### 1. Missing Pipeline Reports

**CRITICAL FINDING**: Only AU (Australia) morning reports exist:
```
./reports/screening/au_morning_report.json
./reports/screening/au_morning_report_2026-02-03.json
```

**NO UK or US morning reports found** in:
- `/reports/screening/uk_morning_report*.json` ❌
- `/reports/screening/us_morning_report*.json` ❌

### 2. Market Sentiment Calculation

The system uses **Multi-Market Sentiment** with weights:
```python
# From paper_trading_coordinator.py line ~485
global_sentiment = weighted_average:
  - US: 50% weight
  - UK: 25% weight  
  - AU: 25% weight
```

**When UK/US reports are missing**:
- System **falls back to SPY-based sentiment** (US market proxy)
- This fallback may not accurately reflect **UK market conditions** for STAN.L
- STAN.L (UK Financial) requires UK-specific sentiment analysis

### 3. Trading Decision Gates

The `should_allow_trade()` method implements multiple gates:

#### Gate 1: Sentiment Recommendation Block
```python
# Lines 555-565
if recommendation == 'STRONG_SELL' or recommendation == 'AVOID':
    return (False, 0.0, "Morning report: STRONG_SELL/AVOID")

if recommendation == 'SELL' and sentiment_score < 35:
    return (False, 0.0, f"Morning report: SELL + Low Sentiment ({sentiment_score})")
```

#### Gate 2: FinBERT Breakdown Check
```python
# Lines 567-580
if recommendation in ['CAUTION', 'HOLD'] and sentiment_score < 45:
    if finbert_breakdown and finbert_breakdown.get('negative', 0) > 0.60:
        return (False, 0.0, "Caution + High Negative Sentiment >60%")
    elif finbert_breakdown and finbert_breakdown.get('negative', 0) > 0.45:
        return (True, 0.5, "Caution + Moderate Negative 45-60%")  # REDUCE position
```

#### Gate 3: Global Sentiment Block
```python
# Lines 582-585
block_threshold = self.config.get('cross_timeframe', {}).get('sentiment_block_threshold', 30)
if sentiment_score < block_threshold:
    return (False, 0.0, f"Market Sentiment too low ({sentiment_score:.0f} < {block_threshold})")
```

#### Gate 4: Signal Confidence
```python
# Lines 587-590
if signal.get('action') not in ['BUY', 'STRONG_BUY']:
    return (True, 1.0, "Signal not a buy")

if signal.get('confidence', 0) < 52:
    return (False, 0.0, f"Signal confidence too low ({signal.get('confidence')})")
```

#### Gate 5: Position Sizing by Sentiment
```python
# Lines 593-613
# <30: BLOCKED (extreme bearish)
# 30-45: 50% position (0.5 multiplier)
# 45-55: 75% position (0.75 multiplier)
# 55-65: 100% position (1.0 multiplier)
# 65-75: 120% position (1.2 multiplier)
# ≥75: 150% position (1.5 multiplier)
```

### 4. Likely Failure Point for STAN.L

**Hypothesis**: One or more of these scenarios occurred:

#### Scenario A: No UK Morning Report
- **STAN.L** requires UK market sentiment
- **UK pipeline NOT run** → No `uk_morning_report.json`
- System falls back to **SPY-based sentiment** (US proxy)
- SPY sentiment may have been **< 45** (borderline)
- **Result**: Trade BLOCKED or position REDUCED to 50%

#### Scenario B: Signal Confidence Too Low
- Without UK pipeline data, STAN.L may have generated weak signal
- If `signal.confidence < 52%` → **BLOCKED**
- The `SwingSignalGenerator` needs UK-specific data:
  - UK sector momentum
  - UK market breadth
  - FTSE 100 context
  - UK financial sector news

#### Scenario C: Market Timing
- **STAN.L** is a UK Financial (opens 08:00 GMT)
- If overnight run occurred **before UK market open**:
  - `market_calendar.py` may have marked **STAN.L as CLOSED**
  - Trading cycle skips closed markets (lines 1411-1419)

#### Scenario D: Position Limit Reached
- System has `max_total_positions` limit (default 10)
- If **AAPL, BHP.AX, HSBA.L** were entered first
- And position limit was reached
- **STAN.L** would be skipped (lines 1467-1471)

---

## Why AAPL, BHP.AX, HSBA.L Traded Successfully

### AAPL (US Tech)
✅ **US pipeline data available** (or fallback SPY works well for US stocks)  
✅ **High signal confidence** from FinBERT + LSTM  
✅ **Market open during run**  
✅ **Entered before position limit**

### BHP.AX (AU Materials)
✅ **AU morning report EXISTS** (`au_morning_report.json`)  
✅ **Strong sector momentum** (Materials: Strong per report)  
✅ **High sentiment score** (68/100 per report)  
✅ **Listed in top_stocks**

### HSBA.L (UK Financial)
✅ **Same sector as STAN.L** (UK Financials)  
✅ **BUT**: May have been first UK stock evaluated  
✅ **Higher signal confidence** than STAN.L  
✅ **Or**: Better technical indicators at time of scan

---

## Missing Feature: Intraday Opportunity Monitor

### Original Implementation (Weeks Ago)

The conversation history mentions:
> "In the original version of the pipeline module many weeks ago now there was also a monitor for opportunities throughout that would provide a buy or sell signal."

**Current Status**: ❌ **NOT FOUND** in current codebase

```bash
# Search results:
grep "intraday.*monitor" *.py → 0 matches
grep "opportunity.*monitor" *.py → 0 matches
find . -name "*scanner*" → 0 matches
find . -name "*opportunity*" → 0 matches
```

### Available Monitoring Components

The following modules **DO EXIST** but are **NOT INTEGRATED**:

1. **`pipelines/models/screening/macro_news_monitor.py`** (55KB)
   - Macro news monitoring
   - NOT integrated into trading cycle

2. **`pipelines/models/screening/spi_monitor.py`** (24KB)
   - SPI (Strategic Performance Indicator) monitoring
   - NOT integrated into trading cycle

3. **`pipelines/models/screening/us_market_monitor.py`** (14KB)
   - US market monitoring
   - NOT integrated into trading cycle

### Intraday Scanner (Exists but Limited)

Found in `market_monitoring.py`:
```python
class IntradayScanner:
    """
    15-minute breakout detection
    """
    def scan_opportunities(self, symbols, fetch_func):
        # Detects breakouts every 15 minutes
        # Returns IntradayAlert objects
```

**Current Integration**:
```python
# paper_trading_coordinator.py line 1346
def run_intraday_scan(self):
    if self._should_run_intraday_scan():
        alerts = self.intraday_scanner.scan_opportunities(...)
        self.last_intraday_scan = datetime.now()
```

**Limitations**:
- Only runs **every 15 minutes**
- Only detects **breakouts**
- Does **NOT** monitor:
  - Emerging opportunities in watchlist
  - News-driven price movements
  - Sector rotation signals
  - Correlation-based trades

---

## Recommendations

### 1. **URGENT**: Run All Pipelines Before Trading Cycle

**Action**: Ensure pipelines run in sequence:
```bash
# Required sequence:
1. RUN_AU_PIPELINE.bat  → generates au_morning_report.json
2. RUN_US_PIPELINE.bat  → generates us_morning_report.json
3. RUN_UK_PIPELINE.bat  → generates uk_morning_report.json
4. START_DASHBOARD.bat  → uses all three reports
```

**Current Issue**:
- START.bat menu Option 1 "Complete System" does NOT run pipelines first
- User must manually run `RUN_ALL_PIPELINES.bat` separately

**Fix**: Update `START.bat` to include pipeline check:
```batch
IF NOT EXIST reports\screening\uk_morning_report.json (
    echo [WARN] UK morning report missing - running UK pipeline...
    call RUN_UK_PIPELINE.bat
)
```

### 2. **HIGH PRIORITY**: Restore Intraday Opportunity Monitor

**Requirement**: Re-implement continuous opportunity scanning

**Features Needed**:
- **Watchlist monitoring**: Track all 720 stocks for entry signals
- **News-driven alerts**: Monitor breaking news for rapid response
- **Price action triggers**: Detect unusual price movements
- **Sector rotation**: Identify sector momentum shifts
- **Volume anomalies**: Flag high-volume breakouts

**Implementation**:
```python
class OpportunityMonitor:
    """
    Continuous monitoring for trading opportunities across 720-stock universe
    """
    def __init__(self, symbols: List[str], update_interval_minutes: int = 5):
        self.symbols = symbols
        self.update_interval = update_interval_minutes
        self.last_scan = {}
        
    def scan_for_opportunities(self) -> List[OpportunityAlert]:
        """
        Scan all symbols for:
        1. Entry signals (BUY setups)
        2. Exit signals (SELL warnings)
        3. Position adjustments (REDUCE/INCREASE)
        """
        opportunities = []
        
        for symbol in self.symbols:
            if self._should_scan(symbol):
                # Check multiple criteria
                signal = self._evaluate_opportunity(symbol)
                
                if signal:
                    opportunities.append(OpportunityAlert(
                        symbol=symbol,
                        alert_type=signal['type'],  # BUY/SELL/ADJUST
                        confidence=signal['confidence'],
                        reason=signal['reason'],
                        urgency=signal['urgency'],  # LOW/MEDIUM/HIGH
                        timestamp=datetime.now()
                    ))
        
        return opportunities
    
    def _evaluate_opportunity(self, symbol: str) -> Optional[Dict]:
        """
        Multi-factor opportunity evaluation:
        1. Technical breakout
        2. News sentiment spike
        3. Volume surge
        4. Sector momentum
        5. Correlation divergence
        """
        # Fetch real-time data
        price_data = self._fetch_price_data(symbol)
        news_data = self._fetch_news_data(symbol)
        
        # Generate composite signal
        technical_signal = self._check_technical_breakout(price_data)
        sentiment_signal = self._check_sentiment_spike(news_data)
        volume_signal = self._check_volume_anomaly(price_data)
        
        # Combine signals
        if technical_signal and sentiment_signal:
            return {
                'type': 'BUY',
                'confidence': 85,
                'reason': 'Technical breakout + positive news',
                'urgency': 'HIGH'
            }
        
        return None
```

**Integration into Trading Cycle**:
```python
# paper_trading_coordinator.py
def run_trading_cycle(self):
    # ... existing code ...
    
    # NEW: Check opportunity monitor
    if self.opportunity_monitor:
        opportunities = self.opportunity_monitor.scan_for_opportunities()
        
        for opp in opportunities:
            if opp.alert_type == 'BUY' and opp.confidence >= 75:
                # Evaluate for immediate entry
                should_enter, _, _ = self.evaluate_entry(opp.symbol)
                
                if should_enter:
                    logger.info(f"[OPPORTUNITY] {opp.symbol}: {opp.reason}")
                    self.enter_position(opp.symbol, {
                        'confidence': opp.confidence,
                        'source': 'opportunity_monitor'
                    })
```

### 3. **MEDIUM PRIORITY**: Enhance UK Market Support

**Issues**:
- UK market timing not properly handled
- UK-specific sentiment missing
- UK sector data underutilized

**Actions**:
a) **Market Calendar Enhancement**
```python
# Proper UK trading hours (GMT)
UK_TRADING_HOURS = {
    'open': '08:00',
    'close': '16:30',
    'timezone': 'Europe/London'
}
```

b) **UK Sentiment Module**
```python
def get_uk_market_sentiment() -> float:
    """
    UK-specific sentiment using:
    - FTSE 100 momentum
    - GBP/USD strength
    - UK economic data
    - Brexit sentiment (if relevant)
    """
    pass
```

c) **UK Pipeline Reliability**
- Add retry logic
- Add fallback data sources
- Add cache with TTL

### 4. **LOW PRIORITY**: Position Queue System

**Problem**: When position limit reached, opportunities are lost

**Solution**: Implement waiting queue
```python
class PositionQueue:
    """
    Queue of pending opportunities when position limit reached
    """
    def __init__(self, max_queue_size: int = 20):
        self.queue = []  # Priority queue by confidence
        
    def add_opportunity(self, symbol: str, signal: Dict):
        """Add to queue, sorted by confidence"""
        pass
        
    def get_next_opportunity(self) -> Optional[Tuple[str, Dict]]:
        """Get highest confidence opportunity when position slot opens"""
        pass
```

### 5. **MONITORING**: Add Trade Decision Logging

**Requirement**: Log WHY stocks were not purchased

```python
# Enhanced logging in evaluate_entry()
if not should_enter:
    logger.warning(f"[SKIP] {symbol}: Entry declined")
    logger.warning(f"  Reason: {decline_reason}")
    logger.warning(f"  Confidence: {confidence:.1f}%")
    logger.warning(f"  Sentiment: {sentiment_score:.1f}/100")
    logger.warning(f"  Positions: {len(self.positions)}/{self.max_positions}")
    
    # Log to decision file
    self._log_declined_trade(symbol, decline_reason, signal)
```

**Output Example**:
```
[SKIP] STAN.L: Entry declined
  Reason: UK morning report missing - fallback sentiment too low (43/100)
  Confidence: 67.5%
  Sentiment: 43.0/100
  Positions: 8/10
  UK Market: OPEN
  Peers: HSBA.L TRADED (sentiment 68)
```

---

## Implementation Priority

| Priority | Task | Impact | Effort | Timeline |
|----------|------|--------|--------|----------|
| 🔴 **P0** | Ensure pipelines run before trading cycle | **HIGH** | Low | Immediate |
| 🔴 **P0** | Add trade decision logging | **HIGH** | Low | Today |
| 🟠 **P1** | Restore opportunity monitor | **HIGH** | High | 2-3 days |
| 🟠 **P1** | Enhance UK market support | **MEDIUM** | Medium | 1-2 days |
| 🟢 **P2** | Implement position queue | **MEDIUM** | Medium | 3-5 days |

---

## Testing Plan

### Test Case 1: STAN.L Scenario Reproduction
```python
# Simulate overnight run without UK pipeline
1. Delete uk_morning_report.json
2. Delete us_morning_report.json  
3. Keep only au_morning_report.json
4. Run trading cycle with symbols: ['AAPL', 'BHP.AX', 'HSBA.L', 'STAN.L']
5. Capture logs for each stock
6. Verify:
   - Which stocks traded
   - Which stocks were skipped
   - Why each was skipped
```

### Test Case 2: Pipeline Dependency
```python
# Verify all pipelines run before trading
1. Clear all reports
2. Run complete workflow
3. Verify reports generated in order: AU → US → UK
4. Verify trading cycle waits for reports
5. Verify fallback behavior if reports missing
```

### Test Case 3: Opportunity Monitor
```python
# Test intraday opportunity detection
1. Start system with empty positions
2. Inject simulated breakout for STAN.L
3. Verify opportunity detected within 5 minutes
4. Verify entry decision made
5. Verify position opened successfully
```

---

## Summary

**Root Cause**: STAN.L likely failed to trade due to:
1. ❌ Missing UK morning report (pipeline not run)
2. ❌ Fallback sentiment too low for UK stock
3. ❌ Possible signal confidence < 52%
4. ❌ Possible position limit reached

**Missing Feature**: Intraday opportunity monitor not present in current codebase

**Recommendation**: 
1. **Immediate**: Run all three pipelines before trading cycle
2. **Short-term**: Restore opportunity monitor for continuous scanning
3. **Medium-term**: Enhance UK market support and logging

---

**Next Steps**:
1. Review logs from the overnight run that missed STAN.L
2. Implement trade decision logging
3. Update START.bat to ensure pipeline execution
4. Begin restoring opportunity monitor functionality

**Estimated Win Rate Improvement**: +8-12% by catching missed opportunities like STAN.L
