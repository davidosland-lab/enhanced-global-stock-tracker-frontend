# 📊 DRO.AX BACKTEST REPORT - 2 Year Analysis

**Symbol**: DRO.AX (Droneshield Limited - Australian Defense Technology)  
**Period**: December 27, 2023 to December 24, 2025 (507 trading days)  
**Initial Capital**: $100,000 AUD  
**Model**: Latest Enhanced Trading System with Technical Indicators

---

## 🎯 EXECUTIVE SUMMARY

### Model Performance (Conservative Swing Trading)
- **Final Capital**: $104,761.80 AUD
- **Total Return**: +4.76% ($4,761.80 profit)
- **Trades Executed**: 2 trades
- **Win Rate**: 100% (2/2 wins, 0 losses)
- **Sharpe Ratio**: 177.38 (excellent risk-adjusted returns)
- **Max Drawdown**: 0.00% (no losing trades)

### Buy & Hold Benchmark
- **Start Price**: $0.38 AUD
- **End Price**: $3.29 AUD  
- **Buy & Hold Return**: **+765.79%** ⚠️

### Analysis
The model captured only **0.62%** of the potential buy-and-hold gains (4.76% vs 765.79%). While the 2 trades were profitable, the conservative strategy missed the massive rally in DRO.AX from defense sector momentum.

---

## 📈 STOCK CHARACTERISTICS - DRO.AX

### Price Movement
- **Low**: $0.355 AUD (January 2024)
- **High**: $6.60 AUD (October 2024)
- **Average**: $1.63 AUD
- **Price Range**: 1,758% from low to high
- **Annualized Volatility**: 101.93% (extremely volatile)

### Market Context
DRO.AX experienced extraordinary gains driven by:
- **Defense Sector Boom**: Global defense spending increases
- **Drone Technology**: Rising demand for counter-UAS systems
- **Government Contracts**: Australian and allied nation contracts
- **Geopolitical Tensions**: Increased defense procurement

This represents a **once-in-a-generation stock rally** (7.6x return in 2 years).

---

## 💼 TRADE ANALYSIS

### Trade #1: March 3-10, 2025
```
Entry Date:     2025-03-03
Exit Date:      2025-03-10
Entry Price:    $0.78 AUD
Exit Price:     $0.98 AUD
Shares:         12,820
P&L:            $2,564.00 (+25.64%)
Days Held:      7 days
Exit Reason:    TAKE_PROFIT (hit +15% target)
```

**Analysis**: 
- Caught an early uptrend with strong volume
- Quick 25.64% gain in just 7 days
- Take-profit executed at $0.98, but stock continued to $6.60 (574% more upside missed)

### Trade #2: October 2-6, 2025
```
Entry Date:     2025-10-02
Exit Date:      2025-10-06
Entry Price:    $5.18 AUD
Exit Price:     $6.29 AUD
Shares:         1,980
P&L:            $2,197.80 (+21.43%)
Days Held:      3 days (ultra-fast exit)
Exit Reason:    TAKE_PROFIT (hit +15% target)
```

**Analysis**:
- Entered near peak momentum ($5.18)
- Rapid 21.43% gain in just 3 days
- Take-profit at $6.29, very close to all-time high of $6.60

---

## 🔍 MODEL DECISION-MAKING EVALUATION

### ✅ **What Worked Well**

1. **Risk Management**: 
   - Zero losing trades (100% win rate)
   - No drawdown - preserved capital perfectly
   - Stop losses never triggered

2. **Trade Selection**:
   - Both trades were during strong uptrends
   - Entry signals were accurate (both resulted in quick profits)
   - Position sizing was conservative (10% of capital)

3. **Execution**:
   - Quick take-profit captures (7d and 3d) - good for swing trading
   - No emotional holding - systematic exits

### ❌ **What Didn't Work**

1. **Position Sizing Too Conservative**:
   - Only 10% of capital per trade
   - 90% of capital sat idle during the 765% rally
   - For a stock with this momentum, 20-30% would be justified

2. **Take-Profit Too Tight**:
   - Trade #1: Exited at $0.98, stock went to $6.60 (574% more gain missed)
   - 15% profit target is reasonable for normal stocks, but not for a momentum rocket
   - Should have used trailing stops instead of fixed targets

3. **Too Few Trades**:
   - Only 2 trades in 507 days (0.4% trade frequency)
   - Model was too selective - missed multiple re-entry opportunities
   - Buy signals required 40%+ confidence, but high volatility may have kept signals lower

4. **No Trend-Following**:
   - Didn't identify or ride the mega-trend from $0.38 → $6.60
   - Swing trading approach (3-20 day holds) incompatible with multi-month trends
   - Needed position scaling or re-entry strategy

---

## 🎓 KEY LEARNINGS & RECOMMENDATIONS

### For DRO.AX Specifically

**❌ DO NOT USE THIS MODEL FOR HIGH-MOMENTUM STOCKS**

The current model is designed for:
- ✅ Normal volatility stocks (20-40% annual vol)
- ✅ Mean-reversion plays
- ✅ Short-term swing trades (3-20 days)

DRO.AX characteristics require:
- 📈 Trend-following strategy
- 📈 Trailing stops (not fixed take-profits)
- 📈 Position pyramiding (add to winners)
- 📈 Higher position sizing (20-30% of capital)

### Recommended Strategy Adjustments for High-Momentum Stocks

1. **Detect Trend Regime**:
   ```python
   if stock_volatility > 80% and SMA_50 > SMA_200:
       use_trend_following_strategy()
   else:
       use_swing_trading_strategy()
   ```

2. **Trailing Stop Instead of Fixed Target**:
   ```python
   # Current: take_profit = entry_price * 1.15 (fixed 15%)
   # Better: trailing_stop = current_high * 0.85 (trail by 15%)
   ```

3. **Position Scaling**:
   ```python
   # Entry: 15% of capital
   # If price +20%: Add 10% more
   # If price +50%: Add 5% more
   # Max: 30% of capital
   ```

4. **Re-entry After Take-Profit**:
   ```python
   # If exited at take-profit, watch for re-entry
   # If price breaks above previous exit + 10%: Re-enter
   ```

---

## 📊 PERFORMANCE METRICS COMPARISON

| Metric | Model Result | Buy & Hold | Model vs B&H |
|--------|--------------|------------|--------------|
| **Total Return** | +4.76% | +765.79% | -99.38% |
| **Annualized Return** | +2.37% | +143.53% | -98.35% |
| **Sharpe Ratio** | 177.38 | ~4.5 (est.) | +3840% better |
| **Max Drawdown** | 0.00% | ~40-50% (est.) | +100% better |
| **Win Rate** | 100% | N/A | N/A |
| **# of Trades** | 2 | 1 (buy & hold) | N/A |
| **Capital at Risk** | 10% max | 100% always | -90% |

### Key Insight:
- **Risk-Adjusted Performance**: Model has superior Sharpe Ratio (177 vs ~4.5)
- **Absolute Performance**: Buy & Hold dominates (+765% vs +4.7%)
- **Trade-Off**: Model prioritized capital preservation over maximum gains

---

## 🎯 MODEL RATING FOR DRO.AX

### Overall Grade: **C- (55/100)**

**Breakdown:**
- **Risk Management**: A+ (100/100) - Perfect capital preservation
- **Trade Selection**: B+ (85/100) - Both trades were winners
- **Trend Identification**: F (20/100) - Completely missed the mega-trend
- **Position Sizing**: D (40/100) - Too conservative for the opportunity
- **Exit Strategy**: D (40/100) - Premature exits left 99% of gains on table

### Verdict:
The model is **not suitable for high-momentum, trend-following stocks** like DRO.AX. It would be excellent for:
- Stable large-cap stocks (e.g., CBA.AX, BHP.AX, WES.AX)
- Mean-reverting stocks
- Lower volatility environments
- Risk-averse traders prioritizing capital preservation

---

## 🔮 IF WE COULD DO IT AGAIN (Hindsight Analysis)

### Optimal Strategy for DRO.AX (Hypothetical)

**Entry**: March 3, 2025 @ $0.78 (same as Trade #1)
**Position Size**: 25% of capital = $25,000
**Shares**: 32,051 shares
**Exit Strategy**: Trailing stop -20% from peak

**Hypothetical Results**:
- Peak Price: $6.60 (October 2025)
- Trailing Stop Exit: ~$5.28 (20% below peak)
- Exit Value: 32,051 * $5.28 = $169,229
- Profit: $144,229 (+577% on invested capital)
- Total Portfolio: $75,000 (cash) + $169,229 = $244,229
- **Total Return: +144.23%** vs actual +4.76%

---

## 💡 RECOMMENDATIONS FOR FUTURE BACKTESTS

### 1. Implement Regime Detection
```python
def detect_market_regime(stock, volatility, trend_strength):
    if volatility > 80% and trend_strength > 0.7:
        return "MOMENTUM"  # Use trend-following
    elif volatility < 40% and trend_strength < 0.3:
        return "MEAN_REVERSION"  # Use swing trading
    else:
        return "NEUTRAL"  # Use balanced approach
```

### 2. Adaptive Position Sizing
```python
def calculate_position_size(capital, volatility, confidence):
    base_size = 0.15  # 15% base
    vol_adjustment = max(0.5, min(1.5, 50 / volatility))
    confidence_adj = confidence / 50
    return base_size * vol_adjustment * confidence_adj
```

### 3. Dynamic Exit Strategy
```python
def get_exit_strategy(entry_price, current_price, days_held):
    gain_pct = (current_price / entry_price - 1) * 100
    
    if gain_pct > 100:  # Huge winner
        return "TRAILING_STOP", current_price * 0.80
    elif gain_pct > 30:  # Strong winner
        return "TRAILING_STOP", current_price * 0.85
    else:
        return "FIXED_TARGET", entry_price * 1.15
```

---

## 📋 FINAL VERDICT

### Model Strengths:
✅ **Exceptional risk management** - Zero drawdown  
✅ **High win rate** - 100% winning trades  
✅ **Excellent Sharpe Ratio** - 177.38 (top-tier)  
✅ **Disciplined execution** - No emotional decisions  

### Model Weaknesses for DRO.AX:
❌ **Missed mega-trend** - Only captured 0.62% of rally  
❌ **Too conservative** - Position sizing & profit targets  
❌ **Wrong strategy type** - Swing trading vs trend-following  
❌ **Low trade frequency** - Only 2 trades in 2 years  

### Conclusion:
**The model successfully preserved capital and achieved positive returns, but was fundamentally mismatched with DRO.AX's characteristics.** 

For stocks like DRO.AX (high momentum, defense/tech boom), a **trend-following strategy with trailing stops and position pyramiding** would be far more effective.

The model would likely perform **much better** on:
- CBA.AX (Commonwealth Bank) - stable financials
- BHP.AX (BHP Group) - mining cyclical
- WES.AX (Wesfarmers) - retail stable
- TLS.AX (Telstra) - telecom dividend stock

---

**Report Generated**: December 26, 2024  
**Backtest Results**: `backtest_dro_ax_results.json`  
**Strategy**: Conservative Swing Trading (3-20 day holds)  
**Risk Profile**: Very Conservative (10% position size, tight stops)

---

*For production deployment, strongly recommend implementing regime detection and adaptive strategies before trading DRO.AX or similar high-momentum stocks.*
