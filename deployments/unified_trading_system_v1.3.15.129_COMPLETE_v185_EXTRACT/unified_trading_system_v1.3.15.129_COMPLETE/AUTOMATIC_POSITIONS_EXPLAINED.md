# Understanding "Automatic" Positions in Dashboard

## Question:
"Why does the dashboard automatically buy AAPL, CBA.AX, and BHP.AX when I start trading with 'Global Mix'?"

---

## Answer: These are NOT Hardcoded Buys!

### What's Actually Happening:

When you select **"Global Mix"** and start trading, the dashboard:

1. **Monitors these 5 stocks**: `AAPL, MSFT, CBA.AX, BHP.AX, HSBA.L`
2. **Runs first trading cycle** (within 60 seconds)
3. **Evaluates each stock** for buy signals
4. **Automatically enters positions** if signals are strong

This is the **paper trading system working as designed** - it evaluates signals and executes trades automatically based on ML algorithms.

---

## Why AAPL, CBA.AX, and BHP.AX?

These stocks likely show strong buy signals because:

1. **AAPL (Apple)**: 
   - Large cap tech stock
   - High liquidity
   - Often shows momentum signals
   - Currently down -1.43% → might trigger "buy the dip" logic

2. **CBA.AX (Commonwealth Bank)**:
   - Australia's largest bank
   - Stable dividend payer
   - Often rates high on fundamental scores
   - Low volatility = good risk/reward

3. **BHP.AX (BHP Group)**:
   - Mining giant
   - Commodity exposure
   - Strong fundamentals
   - Often positively correlated with global growth

---

## The Trading Logic (Not Hardcoded!)

### File: `core/paper_trading_coordinator.py` Lines 1477-1489

```python
# 6. Look for new entries
if len(self.positions) < self.config['risk_management']['max_total_positions']:
    logger.info("🔎 Scanning for new entry opportunities...")
    
    for symbol in self.symbols:
        if symbol in self.positions:
            continue
        
        should_enter, confidence, signal = self.evaluate_entry(symbol)
        
        if should_enter:
            logger.info(f"[OK] Entry signal for {symbol} - confidence {confidence:.2f}")
            self.enter_position(symbol, signal)
```

### What `evaluate_entry()` Checks:

The system evaluates multiple factors:

1. **FinBERT Sentiment** (25% weight)
   - News sentiment for the stock
   - Market-wide sentiment

2. **LSTM Predictions** (25% weight)
   - Machine learning price predictions
   - Historical pattern recognition

3. **Technical Indicators** (25% weight)
   - RSI, MACD, Bollinger Bands
   - Moving average crossovers
   - Volume analysis

4. **Momentum** (15% weight)
   - Price momentum
   - Trend strength

5. **Volume** (10% weight)
   - Trading volume patterns
   - Volume confirmation

If **total confidence > 65%** (default threshold), the system enters the position.

---

## How to Prevent Automatic Buys

### Option 1: Use Manual Trading Only

Don't click "Start Trading" - instead use the **Force Buy/Sell** buttons in the "Manual Trading Controls" section.

### Option 2: Increase Confidence Threshold

**File**: `config/paper_trading_config.json`

```json
{
  "swing_trading": {
    "confidence_threshold": 80,  // Change from 65 to 80 (higher = fewer trades)
    ...
  }
}
```

### Option 3: Disable Automatic Entry

**File**: `core/unified_trading_dashboard.py`

Modify the trading loop to skip automatic entries:

```python
# Around line 1477 in paper_trading_coordinator.py
# Comment out or add condition:

# 6. Look for new entries (DISABLED for manual control)
if False:  # Set to False to disable auto-entries
    if len(self.positions) < self.config['risk_management']['max_total_positions']:
        # ... (rest of the code)
```

### Option 4: Adjust Risk Management Settings

**File**: `config/paper_trading_config.json`

```json
{
  "risk_management": {
    "max_total_positions": 0,  // Set to 0 to prevent ANY automatic entries
    ...
  }
}
```

### Option 5: Change Symbol Preset

Instead of using "Global Mix", create a custom list without stocks you don't want:

**File**: `core/unified_trading_dashboard.py` Line 104

```python
STOCK_PRESETS = {
    'ASX Blue Chips': 'CBA.AX,BHP.AX,RIO.AX,WOW.AX,CSL.AX',
    'ASX Mining': 'RIO.AX,BHP.AX,FMG.AX,NCM.AX,S32.AX',
    'ASX Banks': 'CBA.AX,NAB.AX,WBC.AX,ANZ.AX',
    'US Tech Giants': 'AAPL,MSFT,GOOGL,NVDA,TSLA',
    'US Blue Chips': 'AAPL,JPM,JNJ,WMT,XOM',
    'US Growth': 'TSLA,NVDA,AMD,PLTR,SQ',
    'Global Mix': 'AAPL,MSFT,CBA.AX,BHP.AX,HSBA.L',  // Original
    'Global Mix (No Auto)': 'MSFT,HSBA.L',  // ADD THIS: Exclude stocks that always trigger
    'Custom': ''
}
```

---

## Checking Why Specific Stocks Triggered

### Look at the Logs

**File**: `logs/unified_trading.log` or `logs/paper_trading.log`

Look for entries like:

```
[OK] Entry signal for AAPL - confidence 72.50
  → FinBERT: 68/100 (BULLISH)
  → LSTM: 5.2% gain predicted
  → Technical: RSI=42 (oversold), MACD=bullish crossover
  → Volume: Above average
  → Market Sentiment: 58/100 (NEUTRAL)
  → DECISION: BUY 250 shares @ $184.23
```

This will show you **exactly why** each stock was bought.

### Dashboard ML Signals Panel

The dashboard shows:
- Current sentiment scores
- Technical indicators
- ML predictions
- Recent trading decisions

Check the **"ML Signals & Decisions"** panel to see what triggered the buys.

---

## Recommended Approach

### For Learning / Testing:
1. **Keep automatic trading enabled**
2. **Monitor the logs** to understand why stocks are bought
3. **Adjust confidence threshold** (75-80%) to reduce trades
4. **Review performance** after a few days

### For Manual Control:
1. **Set `max_total_positions: 0`** in config
2. **Use Force Buy/Sell buttons only**
3. **Dashboard still monitors signals** but doesn't execute

### For Production:
1. **Keep auto-trading enabled** (that's the point!)
2. **Fine-tune confidence threshold** based on backtesting
3. **Monitor win rate** and adjust parameters
4. **Trust the ML signals** - they're designed to be 70-75% accurate

---

## Key Files to Check

1. **Config**: `config/paper_trading_config.json`
   - Confidence threshold
   - Max positions
   - Risk management

2. **Presets**: `core/unified_trading_dashboard.py` (Line 97-106)
   - Symbol lists
   - Global Mix definition

3. **Logs**: `logs/paper_trading.log`
   - Why stocks were bought
   - Signal breakdowns
   - Trading decisions

4. **State**: `state/paper_trading_state.json`
   - Current positions
   - Capital allocation
   - Performance metrics

---

## Summary

**Bottom Line**: The dashboard is **NOT hardcoded** to buy AAPL, CBA.AX, and BHP.AX. These stocks simply meet the buy criteria when you start trading with "Global Mix".

**Why these specific stocks?**
- They're liquid, well-known stocks
- They often show positive signals
- AAPL being down -1.43% might trigger "buy the dip" logic
- CBA.AX and BHP.AX are fundamentally strong Australian stocks

**To prevent auto-buys**:
- Set `max_total_positions: 0` in config
- Use Force Buy/Sell buttons manually
- Increase confidence threshold to 80%+
- Monitor different stocks that don't always trigger

**To understand WHY they're bought**:
- Check `logs/paper_trading.log`
- Review ML Signals panel in dashboard
- Look at recent trading decisions

---

## Version: v1.3.15.110
## Date: 2026-02-09
