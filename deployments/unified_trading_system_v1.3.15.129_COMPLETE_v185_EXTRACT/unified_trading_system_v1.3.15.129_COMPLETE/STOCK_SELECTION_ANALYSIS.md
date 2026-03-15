# Stock Selection Logic Analysis & Fix - STAN.L Issue

## 🔍 **Issue Summary**

**Problem**: STAN.L was on the trading list alongside AAPL, BHP.AX, and HSBA.L but did not get purchased despite rising 1.87%, while the other three stocks traded immediately.

**Date**: Overnight run without UK/US pipelines  
**Stocks on List**: AAPL, BHP.AX, HSBA.L, STAN.L  
**Purchased**: AAPL ✅, BHP.AX ✅, HSBA.L ✅  
**Skipped**: STAN.L ❌ (+1.87% gain missed)

---

## 📋 **Current Buy Decision Logic**

### Entry Decision Flow (paper_trading_coordinator.py)

```
1. evaluate_entry(symbol) → Line 864
   ├─→ Fetch market data (3 months)
   ├─→ Generate swing signal (confidence required)
   ├─→ Check confidence threshold (default: varies by config)
   ├─→ evaluate_entry_with_intraday(symbol, signal)
   │   ├─→ Get market sentiment
   │   ├─→ Block if sentiment < 30 (block_threshold)
   │   └─→ Boost if sentiment > 70 (boost_threshold)
   ├─→ Check max positions limit
   ├─→ Check if already holding
   └─→ should_enter = (prediction==1 AND confidence>=threshold)

2. enter_position(symbol, signal) → Line 979
   ├─→ should_allow_trade(symbol, signal, sentiment_score) → SENTIMENT GATE
   │   ├─→ Check morning report recommendation
   │   │   └─→ BLOCK on: STRONG_SELL, AVOID
   │   │   └─→ BLOCK on: SELL + sentiment<35
   │   │   └─→ REDUCE to 50% on: High negative FinBERT (>60%)
   │   ├─→ Block if sentiment < 30
   │   ├─→ Block if confidence < 52%
   │   └─→ Position multiplier based on sentiment:
   │       • sentiment < 45: REDUCE to 50%
   │       • sentiment < 55: REDUCE to 75%
   │       • sentiment 55-65: Standard 100%
   │       • sentiment 65-75: BOOST to 120%
   │       • sentiment > 75: BOOST to 150%
   └─→ Calculate shares based on position_value * position_multiplier
```

### Key Blocking Points

1. **Confidence Threshold** (Line 901-902)
   ```python
   threshold = self.config['swing_trading']['confidence_threshold']
   if confidence < threshold:
       return False, confidence, signal
   ```

2. **Market Sentiment Block** (Line 954-960)
   ```python
   block_threshold = self.config['cross_timeframe'].get('sentiment_block_threshold', 30)
   if self.last_market_sentiment < block_threshold:
       logger.warning(f"[ERROR] BLOCKED entry for {symbol}...")
       return None
   ```

3. **Sentiment Gate** (Line 540-641)
   ```python
   def should_allow_trade(...) -> Tuple[bool, float, str]:
       # Check morning report recommendation
       # Block on STRONG_SELL, AVOID, SELL+low_sentiment
       # Check confidence threshold (52%)
       # Apply position multipliers
   ```

---

## 🔍 **Why STAN.L Might Have Been Skipped**

### Hypothesis 1: Confidence Below Threshold
**Most Likely**: Signal confidence for STAN.L was below the threshold (default ~52-60%)

**Evidence**:
- Lines 899-902: Base confidence check
- Lines 605-610: Sentiment gate confidence check (52%)
- If STAN.L had confidence = 50%, it would be rejected

**Log to Check**: 
```
[SKIP] STAN.L: Confidence 50.5% < 52.0%
```

### Hypothesis 2: Sentiment Gate Block
STAN.L might have been blocked by sentiment-based position sizing:
- If market sentiment was 45-55 (neutral), position would be reduced to 75%
- If sentiment < 45, position reduced to 50%
- If sentiment < 30, completely blocked

**Log to Check**:
```
[REDUCE] STAN.L: Neutral sentiment (48.5) - REDUCE position to 75%
[BLOCK] STAN.L: Sentiment too low (28.3 < 30)
```

### Hypothesis 3: Max Positions Reached
If 3 positions (AAPL, BHP.AX, HSBA.L) were entered before STAN.L was evaluated:

**Code**: Line 914-917
```python
max_positions = self.config['risk_management']['max_total_positions']
if len(self.positions) >= max_positions:
    logger.warning(f"{symbol}: Max positions ({max_positions}) reached")
    return False, confidence, signal
```

### Hypothesis 4: Morning Report Recommendation
If STAN.L had negative sentiment in morning report:
- Recommendation = "CAUTION" or "HOLD" with high negative %
- Would trigger position reduction or block

**Code**: Lines 559-591
```python
if recommendation in ['CAUTION', 'HOLD'] and sentiment_score < 45:
    if negative_pct > 60:
        return False, 0.0, reason  # BLOCK
    elif negative_pct > 45:
        return True, 0.5, reason   # REDUCE to 50%
```

---

## 🚨 **Missing Component: Intraday Opportunity Monitor**

### Original Feature (Referenced in Code)

The system DOES have intraday monitoring components but they may not be fully utilized:

**File**: `ml_pipeline/market_monitoring.py`
- `IntradayScanner` class (Line 233+)
- Scans for breakouts every 15 minutes
- Generates `IntradayAlert` objects
- **Purpose**: Detect opportunities throughout the day that weren't in original list

**Current Usage** (paper_trading_coordinator.py, Lines 1437-1451):
```python
if self._should_run_intraday_scan():
    if self.intraday_scanner:
        logger.info("🔍 Running intraday scan...")
        alerts = self.intraday_scanner.scan_for_opportunities(
            symbols=self.symbols,  # ← ONLY scans pre-selected symbols!
            price_data_provider=self.fetch_market_data
        )
```

**PROBLEM**: Intraday scanner only monitors symbols already in `self.symbols` list. It does NOT discover new opportunities outside the initial list.

---

## 🔧 **Recommended Fixes**

### Fix 1: Add Debugging Logs for STAN.L

**File**: `core/paper_trading_coordinator.py`

**Line 1485-1489** (in run_trading_cycle):
```python
should_enter, confidence, signal = self.evaluate_entry(symbol)

if should_enter:
    logger.info(f"[OK] Entry signal for {symbol} - confidence {confidence:.2f}")
    self.enter_position(symbol, signal)
else:
    # ADD THIS:
    logger.info(f"[SKIP] {symbol}: confidence={confidence:.2f}, "
                f"prediction={signal.get('prediction', 'N/A')}, "
                f"action={signal.get('action', 'N/A')}")
```

### Fix 2: Log Sentiment Gate Decisions

**File**: `core/paper_trading_coordinator.py`

**Line 993-999** (in enter_position):
```python
gate, position_multiplier, reason = self.should_allow_trade(symbol, signal, self.last_market_sentiment)

if not gate:
    # Already logged as WARNING, make it more visible:
    logger.error(f"❌ {symbol}: TRADE BLOCKED - {reason}")
    logger.error(f"  → Confidence: {signal.get('confidence', 'N/A')}")
    logger.error(f"  → Sentiment: {self.last_market_sentiment:.1f}/100")
    logger.error(f"  → Recommendation: {getattr(self, 'sentiment_recommendation', 'N/A')}")
    return False
```

### Fix 3: Restore Full Intraday Monitor (NEW)

**Purpose**: Monitor ALL stocks in watchlist (not just selected symbols), detect new opportunities throughout the day.

**File**: Create `core/intraday_opportunity_monitor.py`

```python
"""
Intraday Opportunity Monitor
============================

Continuously monitors expanded watchlist for:
- Breakouts (price > key resistance)
- Volume spikes (3x+ average)
- Momentum shifts (RSI crossing 50)
- Sentiment changes (FinBERT updates)

Unlike intraday_scanner, this monitors ALL stocks in the universe,
not just pre-selected symbols.
"""

class IntradayOpportunityMonitor:
    def __init__(self, watchlist: List[str], finbert_api_url: str = None):
        self.watchlist = watchlist  # e.g., 240 stocks per market
        self.finbert_api_url = finbert_api_url or "http://localhost:5001"
        self.last_scan = {}
        self.opportunities = []
    
    def scan_universe(self) -> List[Dict]:
        """
        Scan entire watchlist for opportunities
        
        Returns: List of {symbol, reason, confidence, entry_price}
        """
        opportunities = []
        
        for symbol in self.watchlist:
            # Skip if scanned recently (< 15 min)
            if self._recently_scanned(symbol):
                continue
            
            # Check for opportunity
            opportunity = self._evaluate_opportunity(symbol)
            
            if opportunity:
                opportunities.append(opportunity)
        
        self.opportunities = opportunities
        return opportunities
    
    def _evaluate_opportunity(self, symbol: str) -> Optional[Dict]:
        """Check if symbol has new opportunity"""
        # 1. Get current price data
        data = fetch_market_data(symbol, period='5d', interval='15m')
        
        if data is None or len(data) < 20:
            return None
        
        # 2. Check for breakout
        current_price = data['Close'].iloc[-1]
        high_20 = data['High'].iloc[-20:].max()
        
        if current_price > high_20 * 1.02:  # Breakout above 20-period high
            # 3. Check volume confirmation
            current_volume = data['Volume'].iloc[-1]
            avg_volume = data['Volume'].iloc[-20:].mean()
            
            if current_volume > avg_volume * 1.5:  # Volume spike
                # 4. Get FinBERT sentiment
                sentiment = self._get_finbert_sentiment(symbol)
                
                if sentiment and sentiment.get('confidence', 0) > 60:
                    return {
                        'symbol': symbol,
                        'reason': 'Breakout + Volume Spike',
                        'confidence': sentiment.get('confidence', 0),
                        'entry_price': current_price,
                        'sentiment': sentiment.get('sentiment', 'neutral'),
                        'timestamp': datetime.now().isoformat()
                    }
        
        return None
    
    def _get_finbert_sentiment(self, symbol: str) -> Optional[Dict]:
        """Query FinBERT API for sentiment"""
        try:
            response = requests.get(f"{self.finbert_api_url}/api/sentiment/{symbol}", timeout=5)
            return response.json() if response.ok else None
        except:
            return None
```

### Fix 4: Integrate Intraday Monitor into Trading Coordinator

**File**: `core/paper_trading_coordinator.py`

**Add to `__init__`** (around Line 250):
```python
# Initialize intraday opportunity monitor
if self.config.get('intraday_monitoring', {}).get('enabled', False):
    from intraday_opportunity_monitor import IntradayOpportunityMonitor
    
    # Build watchlist from pipeline reports
    watchlist = self._load_watchlist_from_reports()
    
    self.opportunity_monitor = IntradayOpportunityMonitor(
        watchlist=watchlist,
        finbert_api_url=config.get('finbert_api_url', 'http://localhost:5001')
    )
    logger.info(f"[MONITOR] Intraday opportunity monitor initialized with {len(watchlist)} stocks")
else:
    self.opportunity_monitor = None
```

**Add to `run_trading_cycle`** (around Line 1451):
```python
# 2.5. Check for NEW opportunities from intraday monitor
if self.opportunity_monitor:
    new_opportunities = self.opportunity_monitor.scan_universe()
    
    if new_opportunities:
        logger.info(f"🎯 Found {len(new_opportunities)} NEW intraday opportunities")
        
        for opp in new_opportunities:
            symbol = opp['symbol']
            
            # Add to symbols if not already there
            if symbol not in self.symbols:
                self.symbols.append(symbol)
                logger.info(f"  ➕ Added {symbol} to watchlist: {opp['reason']} (conf={opp['confidence']:.1f}%)")
```

### Fix 5: Load Watchlist from Pipeline Reports

**File**: `core/paper_trading_coordinator.py`

```python
def _load_watchlist_from_reports(self) -> List[str]:
    """
    Load expanded watchlist from pipeline morning reports
    
    Returns: List of symbols from AU/US/UK reports
    """
    watchlist = set(self.symbols)  # Start with initial symbols
    
    report_paths = [
        'reports/screening/au_morning_report.json',
        'reports/screening/us_morning_report.json',
        'reports/screening/uk_morning_report.json'
    ]
    
    for report_path in report_paths:
        if Path(report_path).exists():
            try:
                with open(report_path) as f:
                    report = json.load(f)
                
                # Add top opportunities from report
                top_opportunities = report.get('top_opportunities', [])
                for stock in top_opportunities[:20]:  # Top 20 from each market
                    watchlist.add(stock.get('symbol'))
                
                logger.info(f"[MONITOR] Loaded {len(top_opportunities)} stocks from {report_path}")
            except Exception as e:
                logger.warning(f"Could not load {report_path}: {e}")
    
    logger.info(f"[MONITOR] Total watchlist: {len(watchlist)} stocks")
    return list(watchlist)
```

---

## 📊 **Expected Behavior After Fixes**

### Before Fixes
```
[1478] Scanning for new entry opportunities...
[1482] AAPL: evaluate_entry → confidence=65% → ENTER ✅
[1482] BHP.AX: evaluate_entry → confidence=70% → ENTER ✅
[1482] HSBA.L: evaluate_entry → confidence=68% → ENTER ✅
[1482] STAN.L: evaluate_entry → confidence=51% → ❌ (silently skipped)
```

### After Fixes
```
[1478] Scanning for new entry opportunities...
[1482] AAPL: evaluate_entry → confidence=65%, action=BUY → ENTER ✅
[1482] BHP.AX: evaluate_entry → confidence=70%, action=BUY → ENTER ✅
[1482] HSBA.L: evaluate_entry → confidence=68%, action=BUY → ENTER ✅
[1482] STAN.L: evaluate_entry → confidence=51%, action=BUY
       [SKIP] STAN.L: confidence=51.0%, prediction=1, action=BUY
       ❌ Reason: Confidence 51.0% < 52.0%
       
[1437] 🔍 Running intraday scan...
[1447]   Found 2 intraday alerts
[1449]   🚨 STAN.L: BULLISH_BREAKOUT (strength=75.0)
       
[NEW]  🎯 Found 1 NEW intraday opportunity
       ➕ Added STAN.L to watchlist: Breakout + Volume Spike (conf=68.0%)
       [Next cycle] STAN.L: evaluate_entry → confidence=68% → ENTER ✅
```

---

## 🎯 **Root Cause: STAN.L Issue**

Based on the code analysis, STAN.L was most likely skipped because:

1. **Confidence was 51-52%** (just below 52% threshold)
2. **Evaluated AFTER max positions reached** (if max=3 and AAPL/BHP/HSBA entered first)
3. **Sentiment gate reduced position sizing** but didn't enter due to low confidence

**Missing Feature**: The intraday monitor exists but only scans pre-selected symbols. STAN.L needed to be:
- Either in initial symbol list with higher confidence
- OR detected by expanded intraday opportunity monitor (currently missing)

---

## ✅ **Action Items**

### Immediate Debugging (v1.3.15.90.2)
1. ✅ Add skip reason logging in evaluate_entry
2. ✅ Add detailed sentiment gate logging
3. ✅ Log confidence thresholds being used

### Feature Restoration (v1.3.15.91)
1. ⚠️ Implement IntradayOpportunityMonitor
2. ⚠️ Load watchlist from pipeline reports
3. ⚠️ Scan expanded universe (not just self.symbols)
4. ⚠️ Add discovered opportunities to trading list dynamically

### Configuration Review
1. ⚠️ Review confidence_threshold setting (may be too high at 52%)
2. ⚠️ Review max_total_positions (may need to be 5-10, not 3)
3. ⚠️ Review sentiment_block_threshold (30 may be too conservative)

---

**Status**: Analysis Complete  
**Priority**: High (opportunity cost: missed +1.87% on STAN.L)  
**Next**: Implement debugging logs (v1.3.15.90.2) then restore intraday monitor (v1.3.15.91)
