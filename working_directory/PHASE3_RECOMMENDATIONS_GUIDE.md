# Phase 3 Recommendations - Complete Guide

## Overview

The Phase 3 Enhanced Manual Trading Platform now includes **automatic buy/sell recommendations** using the **exact same methodology as the original Phase 3 backtest**.

You get:
- ✅ **Manual control** - YOU decide whether to execute
- ✅ **Phase 3 recommendations** - Same signal generation as backtest
- ✅ **Position sizing** - Calculated using Phase 3 rules (confidence + volatility)
- ✅ **Exit analysis** - Stop loss, profit targets, holding periods

---

## How It Works

### Signal Generation (Same as Original Phase 3)

The platform analyzes stocks using **4 components** with **weighted scoring**:

1. **Momentum (30% weight)**
   - RSI (14-period Relative Strength Index)
   - 10-day price momentum
   - Scoring: 40-60 RSI + positive momentum = 0.75

2. **Trend (35% weight)**
   - Moving average alignment (10/20/50-day)
   - Scoring: Price > MA10 > MA20 > MA50 = 0.80 (strong uptrend)

3. **Volume (20% weight)**
   - Volume ratio vs 20-day average
   - Scoring: 2.0x+ volume = 0.75

4. **Volatility (15% weight)**
   - ATR (Average True Range) as % of price
   - Scoring: <2% ATR = 0.70 (low volatility preferred)

**Final Confidence:**
```
Confidence = (Momentum × 0.30 + Trend × 0.35 + Volume × 0.20 + Volatility × 0.15) × 100
```

**BUY Signal:** Confidence ≥ 52% (default threshold)

---

## New Commands

### 1. `add_watchlist(symbols)` - Add Symbols to Watch

```python
>>> add_watchlist(['AAPL', 'NVDA', 'TSLA', 'MSFT', 'GOOGL'])
[SUCCESS] Watchlist updated: AAPL, NVDA, TSLA, MSFT, GOOGL
  Total symbols: 5
  Run recommend_buy() to get Phase 3 buy recommendations
```

**What it does:**
- Adds symbols to your watchlist for analysis
- These symbols will be scanned by `recommend_buy()`

---

### 2. `recommend_buy()` - Get BUY Recommendations

```python
>>> recommend_buy()

============================================================================
PHASE 3 BUY RECOMMENDATIONS - Original Backtest Methodology
============================================================================
Analyzing 5 symbols using Phase 3 signal generation...

Symbol   Confidence   Price      Shares   Value        Regime    
----------------------------------------------------------------------------
NVDA          72.3% $445.80     23       $10,253      bullish   
AAPL          65.1% $187.45     53       $9,935       bullish   
MSFT          58.9% $375.20     26       $9,755       neutral   
============================================================================

Top Recommendation: NVDA at 72.3% confidence
  Suggested command: buy('NVDA', 23)
```

**What it analyzes:**
- All symbols in your watchlist
- Uses Phase 3 signal generation (momentum, trend, volume, volatility)
- Calculates position size using Phase 3 rules
- Sorts by confidence (highest first)

**Position Sizing Logic:**
```python
Base size = 25% of capital (from config)
Confidence adjustment = 0.5 to 1.0 (scales with confidence 52-100)
Volatility adjustment = 0.6 to 1.2 (lower vol = larger position)
Final shares = (Capital × Base% × Confidence × Volatility) / Price
```

---

### 3. `recommend_sell()` - Get SELL Recommendations

```python
>>> recommend_sell()

============================================================================
PHASE 3 SELL RECOMMENDATIONS - Original Backtest Methodology
============================================================================
Evaluating 3 open positions...

[HOLD] AAPL: Hold | P&L: +$175.00 (+0.9%) | Days: 2

Symbol   Priority   P&L              Days   Reason
----------------------------------------------------------------------------
NVDA     HIGH       -$1,025.00 (-4.8%)  5      Stop loss triggered (-4.80%)
TSLA     MEDIUM     +$1,450.00 (+11.8%) 3      Quick profit target hit (11.80%)
============================================================================

Top Sell Recommendation: NVDA (HIGH priority)
  Reason: Stop loss triggered (-4.80%)
  Suggested command: sell('NVDA')
```

**What it evaluates (Phase 3 exit logic):**

1. **Stop Loss** - Confidence threshold: 3% loss (volatility-adjusted)
2. **Quick Profit** - 12% gain after 1+ days
3. **Profit Target** - 8% gain after 2+ days
4. **Holding Period** - 5 days complete with profit
5. **Extended Hold** - 7.5 days with 2%+ loss (cut losses)
6. **Signal Deterioration** - New confidence <45 and in loss

**Priority Levels:**
- **HIGH** - Stop loss hit or significant loss
- **MEDIUM** - Profit target hit or holding period complete

---

### 4. `auto_trade_recommendation()` - Auto-Execute Top Signal

```python
>>> auto_trade_recommendation()

[AUTO-TRADE] Analyzing watchlist for best Phase 3 opportunity...

[EXECUTING] Top Phase 3 recommendation:
  Symbol: NVDA
  Confidence: 72.3%
  Price: $445.80
  Shares: 23

[SUCCESS] Bought 23 shares of NVDA @ $445.80
  Market Regime: BULLISH
  Entry Sentiment: 72.3/100
```

**What it does:**
- Scans watchlist for BUY signals
- Automatically executes the highest confidence recommendation
- ⚠️ **WARNING**: This executes a trade automatically!

---

## Complete Workflow Example

### Step 1: Setup Watchlist

```python
>>> add_watchlist(['AAPL', 'NVDA', 'TSLA', 'MSFT', 'GOOGL', 'AMZN'])
[SUCCESS] Watchlist updated
  Total symbols: 6
```

### Step 2: Get Buy Recommendations

```python
>>> recommend_buy()

============================================================================
PHASE 3 BUY RECOMMENDATIONS
============================================================================

Symbol   Confidence   Price      Shares   Value        Regime    
----------------------------------------------------------------------------
NVDA          72.3% $445.80     23       $10,253      bullish   
AAPL          65.1% $187.45     53       $9,935       bullish   
MSFT          58.9% $375.20     26       $9,755       neutral   
TSLA          55.2% $245.60     40       $9,824       bullish   

Top Recommendation: NVDA at 72.3% confidence
  Suggested command: buy('NVDA', 23)
```

**Analysis:**
- NVDA shows **strongest Phase 3 signal** (72.3%)
- Position sized at 23 shares ($10,253)
- Bullish regime detected

### Step 3: Review Signal Details

```python
>>> market_sentiment()
MARKET CONDITIONS - PHASE 3
Current Regime:     BULLISH
Market Sentiment:   68.5/100
  ↗️  BULLISH - Positive momentum
```

### Step 4: Execute (Manual or Auto)

**Option A: Manual Execution**
```python
>>> buy('NVDA', 23)
[SUCCESS] Bought 23 shares of NVDA @ $445.80
  Stop Loss: $432.43 (-3.0%)
  Take Profit: $481.46 (+8.0%)
  Market Regime: BULLISH
  Entry Sentiment: 72.3/100
```

**Option B: Auto Execution**
```python
>>> auto_trade_recommendation()
[EXECUTING] Top Phase 3 recommendation: NVDA
[SUCCESS] Bought 23 shares @ $445.80
```

### Step 5: Monitor Positions

```python
>>> positions()
Symbol   Shares   Entry      Current    P&L              Regime     Sentiment
NVDA     23       $445.80    $458.20    +$285.20 (+2.8%) bullish   72.3/100
```

### Step 6: Check Sell Recommendations

```python
>>> recommend_sell()

============================================================================
PHASE 3 SELL RECOMMENDATIONS
============================================================================

[HOLD] NVDA: Hold | P&L: +$285.20 (+2.8%) | Days: 1

[INFO] No SELL signals detected. All positions should be held.
```

### Step 7: Later - Exit Signal Triggered

```python
>>> recommend_sell()

Symbol   Priority   P&L              Days   Reason
----------------------------------------------------------------------------
NVDA     MEDIUM     +$1,025.00 (+11.5%) 3      Quick profit target hit (11.50%)

Top Sell Recommendation: NVDA (MEDIUM priority)
  Suggested command: sell('NVDA')

>>> sell('NVDA')
[SUCCESS] Sold 23 shares @ $497.14
  P&L: +$1,180.82 (+11.5%)
  Hold Duration: 3.2 days
```

---

## Configuration

The recommendations use the same Phase 3 config:

```json
{
  "swing_trading": {
    "confidence_threshold": 52.0,
    "max_position_size": 0.25,
    "stop_loss_percent": 3.0,
    "profit_target_pct": 8.0,
    "quick_profit_target_pct": 12.0,
    "holding_period_days": 5,
    "use_volatility_sizing": true
  }
}
```

**Key Parameters:**
- `confidence_threshold`: Minimum confidence for BUY (52%)
- `max_position_size`: Max % of capital per position (25%)
- `stop_loss_percent`: Stop loss % (3%)
- `profit_target_pct`: Standard profit target (8%)
- `quick_profit_target_pct`: Early exit target (12%)

---

## Comparison: Manual vs Recommendations

| Feature | Manual Commands | Recommendation Commands |
|---------|----------------|------------------------|
| **Buy Decision** | YOU choose stocks | Phase 3 generates signals |
| **Position Size** | YOU choose quantity | Phase 3 calculates (confidence + volatility) |
| **Sell Decision** | YOU decide when | Phase 3 evaluates (stops, targets, holding) |
| **Analysis** | Manual sentiment check | Automatic multi-factor analysis |
| **Control** | Full control | Suggestions (you still execute) |

**Best Practice:** Use recommendations for ideas, manual commands for execution control!

---

## Advanced Usage

### Custom Confidence Threshold

Want more/fewer signals? Adjust threshold:

```python
# More conservative (fewer signals)
platform.signal_generator.confidence_threshold = 60.0
recommend_buy()

# More aggressive (more signals)
platform.signal_generator.confidence_threshold = 50.0
recommend_buy()
```

### Scan Specific Symbols

```python
# Scan only tech stocks
recommend_buy(['AAPL', 'NVDA', 'MSFT'])

# Scan all watchlist (default)
recommend_buy()
```

### Check Individual Signal

```python
# Manually check a specific stock's Phase 3 signal
import yfinance as yf
ticker = yf.Ticker('AAPL')
hist = ticker.history(period="3mo")
signal = platform.signal_generator.generate_swing_signal('AAPL', hist)
print(f"Confidence: {signal['confidence']:.1f}%")
print(f"Recommendation: {signal['recommendation']}")
print(f"Regime: {signal['regime']}")
```

---

## FAQ

### Q: Do recommendations use real Phase 3 logic?
**A:** Yes! Exact same methodology:
- 4-component scoring (momentum, trend, volume, volatility)
- Weighted combination (30/35/20/15)
- Position sizing with confidence + volatility adjustment
- Exit logic with stops, targets, holding periods

### Q: Are recommendations automatic?
**A:** No! They are **suggestions**. YOU execute with `buy()` or `sell()`.
Exception: `auto_trade_recommendation()` executes automatically (use with caution).

### Q: How often should I check recommendations?
**A:** Daily or when you want to add positions. Phase 3 is designed for 5-day swing trades.

### Q: Can I adjust the methodology?
**A:** Yes! Edit `phase3_signal_generator.py` or adjust config thresholds.

### Q: What if no symbols qualify?
**A:** `[INFO] No BUY signals detected at current threshold`
Options:
- Wait for better setups
- Add more symbols to watchlist
- Lower confidence threshold (more aggressive)

---

## Quick Reference

```python
# SETUP
add_watchlist(['AAPL', 'NVDA', 'TSLA'])
show_watchlist()

# RECOMMENDATIONS
recommend_buy()           # Get Phase 3 buy signals
recommend_sell()          # Get Phase 3 sell signals

# EXECUTE (Manual)
buy('NVDA', 23)          # Execute recommended trade
sell('NVDA')             # Execute recommended exit

# EXECUTE (Auto)
auto_trade_recommendation()  # Auto-execute top signal

# MONITOR
positions()              # View with regime/sentiment
status()                 # Portfolio summary
```

---

## Summary

✅ **Phase 3 methodology** - Same as original backtest  
✅ **Buy recommendations** - Multi-factor signal generation  
✅ **Sell recommendations** - Exit logic (stops, targets, holding)  
✅ **Position sizing** - Confidence + volatility based  
✅ **Manual control** - YOU decide whether to execute  
✅ **Auto-trade option** - Execute top signal automatically  
✅ **Watchlist** - Track multiple symbols  
✅ **Full transparency** - See confidence, components, metrics  

**Now you get Phase 3 backtest-quality recommendations with full manual control!** 🎯📈
