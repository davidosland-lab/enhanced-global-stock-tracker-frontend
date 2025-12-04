# Realistic Backtest Engine - User Guide

**Version:** 1.0  
**Date:** 2025-12-04  
**Status:** ✅ Production Ready

---

## 🎯 Overview

The **Realistic Backtest Engine** adds critical real-world trading features that were missing from the original backtesting system:

### What's NEW ✨

1. **Stop-Loss Orders** - Automatic risk management
2. **Take-Profit Orders** - Lock in profits at target levels
3. **Trailing Stops** - Protect profits while letting winners run
4. **Position Sizing** - Risk-based position sizing (% of capital at risk)
5. **Portfolio Heat** - Maximum total portfolio risk exposure
6. **Position Limits** - Maximum number of simultaneous positions
7. **Realistic Execution** - Slippage at stop-losses and take-profits
8. **Enhanced Metrics** - Stop-loss rate, expectancy, realized R:R ratio

---

## 📊 Comparison: Old vs. New

### Original Backtest Engine ❌

```python
# Problems with original system:
- No stop-losses → Unlimited downside risk
- No position sizing → All positions same size
- No risk management → Could blow up account
- Unrealistic → Doesn't reflect real trading
- Missing metrics → Can't assess risk

# Example trade:
BUY 100 shares @ $50 = $5,000
SELL 100 shares @ $30 = $3,000
Loss: -$2,000 (-40%)  ← OUCH! No stop-loss!
```

### Realistic Backtest Engine ✅

```python
# New system with risk management:
+ Stop-loss @ 2% → Maximum loss controlled
+ Position sizing → Risk 1% of capital per trade
+ Portfolio heat → Maximum 6% total risk
+ Take-profit @ 2:1 R:R → Target $2 for every $1 risked
+ Realistic metrics → Expectancy, stop-loss rate

# Example trade with $100,000 account:
Entry: $50/share
Stop-loss: $49 (2% below entry)
Risk per share: $1
Max risk: $1,000 (1% of $100k)
Position size: 1,000 shares (risk ÷ risk per share)
Position value: $50,000

If stopped out: -$1,000 (1% of account) ✓ CONTROLLED
If take-profit hits ($52): +$2,000 (2% of account) ✓ 2:1 R:R
```

---

## 🚀 Quick Start

### Basic Usage

```python
from models.backtesting.realistic_backtest_engine import (
    RealisticBacktestEngine, 
    StopLossType
)

# Initialize engine
engine = RealisticBacktestEngine(
    initial_capital=100000.0,
    risk_per_trade_percent=1.0,      # Risk 1% per trade
    max_portfolio_heat=6.0,          # Max 6% total risk
    stop_loss_percent=2.0,           # 2% stop-loss
    use_take_profit=True,            # Enable take-profits
    risk_reward_ratio=2.0            # Target 2:1 R:R
)

# Run backtest (example)
# ... your backtest logic here ...

# Get risk metrics
risk_metrics = engine.get_risk_metrics()

print(f"Stop-loss exits: {risk_metrics['stop_loss_exits']}")
print(f"Take-profit exits: {risk_metrics['take_profit_exits']}")
print(f"Realized R:R ratio: {risk_metrics['realized_risk_reward']:.2f}:1")
print(f"Expectancy: ${risk_metrics['expectancy']:.2f}/trade")
```

---

## ⚙️ Configuration Options

### 1. Risk Management Parameters

```python
RealisticBacktestEngine(
    initial_capital=100000.0,
    
    # How much to risk per trade
    risk_per_trade_percent=1.0,      # Risk 1% of capital per trade
    # Example: $100k account → Max $1,000 risk per trade
    
    # Maximum total portfolio risk
    max_portfolio_heat=6.0,          # Max 6% total at risk
    # Example: Can have 6 positions risking 1% each
    
    # Maximum position size
    max_position_size_percent=20.0,  # Max 20% per position
    # Example: $100k account → Max $20,000 per position
    
    # Maximum number of positions
    max_positions=10,                # Max 10 simultaneous positions
)
```

---

### 2. Stop-Loss Configuration

```python
# Option A: Fixed Percent Stop-Loss (DEFAULT)
engine = RealisticBacktestEngine(
    stop_loss_percent=2.0,           # 2% stop-loss
    stop_loss_type=StopLossType.FIXED_PERCENT
)
# Entry: $50 → Stop-loss: $49 (2% below)

# Option B: ATR-Based Stop-Loss (Adaptive)
engine = RealisticBacktestEngine(
    stop_loss_type=StopLossType.ATR_BASED,
    atr_multiplier=2.0               # 2x ATR from entry
)
# Entry: $50, ATR=$1 → Stop-loss: $48 (2 ATR below)

# Option C: Trailing Stop (Let winners run)
engine = RealisticBacktestEngine(
    stop_loss_type=StopLossType.TRAILING_PERCENT,
    trailing_stop_percent=3.0        # Trail by 3%
)
# Entry: $50, Peak: $60 → Stop-loss: $58.20 (3% from peak)
```

---

### 3. Take-Profit Configuration

```python
# Enable take-profits with risk:reward ratio
engine = RealisticBacktestEngine(
    use_take_profit=True,
    risk_reward_ratio=2.0            # Target 2:1 reward:risk
)

# Example:
# Entry: $50
# Stop-loss: $49 (risk = $1)
# Take-profit: $52 (reward = $2)
# Actual R:R = 2:1 ✓

# Disable take-profits (exit on signal only)
engine = RealisticBacktestEngine(
    use_take_profit=False
)
```

---

### 4. Position Sizing Strategy

```python
# Risk-Based Sizing (RECOMMENDED)
engine = RealisticBacktestEngine(
    allocation_strategy='risk_based'
)
# Sizes positions based on:
# - Distance to stop-loss
# - Risk per trade percentage
# - Signal confidence

# Equal-Weight Sizing
engine = RealisticBacktestEngine(
    allocation_strategy='equal'
)
# All positions get equal $ allocation

# Custom Allocations
engine = RealisticBacktestEngine(
    allocation_strategy='custom',
    custom_allocations={
        'AAPL': 0.15,  # 15%
        'GOOGL': 0.10,  # 10%
        'MSFT': 0.15   # 15%
    }
)
```

---

## 📈 Risk Metrics Explained

### New Metrics Available

```python
risk_metrics = engine.get_risk_metrics()

# Trade Exit Analysis
stop_loss_exits = risk_metrics['stop_loss_exits']  # How many stopped out
take_profit_exits = risk_metrics['take_profit_exits']  # How many hit target
stop_loss_rate = risk_metrics['stop_loss_rate']  # % of trades stopped out

# Risk Management
avg_risk_per_trade = risk_metrics['avg_risk_per_trade']  # Avg $ risked
max_risk_taken = risk_metrics['max_risk_taken']  # Largest single risk
max_portfolio_heat_reached = risk_metrics['max_portfolio_heat_reached']  # Peak risk

# Performance
realized_risk_reward = risk_metrics['realized_risk_reward']  # Actual R:R achieved
expectancy = risk_metrics['expectancy']  # Expected $ per trade
```

### Key Metrics Definitions

**Expectancy** - Average profit per trade  
- Formula: `(Win% × Avg Win) - (Loss% × Avg Loss)`
- Example: `(60% × $200) - (40% × $100) = $80/trade`
- **Positive = profitable system**, Negative = losing system

**Realized Risk:Reward Ratio** - Actual R:R achieved  
- Formula: `Average Win ÷ Average Loss`
- Example: Avg win $400, Avg loss $200 → R:R = 2:1
- **Target: ≥2:1** for profitable trading

**Stop-Loss Rate** - % of trades closed by stop-loss  
- Example: 30 stops out of 100 trades = 30%
- **Typical: 30-50%** for trending systems
- **Too high (>70%) = stops too tight**

**Portfolio Heat** - Total capital at risk  
- Example: 5 positions, $1k risk each = $5k heat = 5%
- **Typical: 5-10%** maximum
- **Protects from simultaneous losses**

---

## 🎨 Example Strategies

### Strategy 1: Conservative (Capital Preservation)

```python
engine = RealisticBacktestEngine(
    initial_capital=50000.0,
    risk_per_trade_percent=0.5,      # Risk only 0.5% per trade
    max_portfolio_heat=3.0,          # Max 3% total risk
    max_position_size_percent=10.0,  # Max 10% per position
    max_positions=6,                 # Max 6 positions
    stop_loss_percent=1.5,           # Tight 1.5% stops
    use_take_profit=True,
    risk_reward_ratio=3.0            # Target 3:1 R:R
)

# Characteristics:
# - Very low risk per trade
# - Tight stops
# - High R:R targets
# - Suitable for: Risk-averse traders, retirement accounts
```

### Strategy 2: Balanced (Moderate Growth)

```python
engine = RealisticBacktestEngine(
    initial_capital=100000.0,
    risk_per_trade_percent=1.0,      # Risk 1% per trade
    max_portfolio_heat=6.0,          # Max 6% total risk
    max_position_size_percent=15.0,  # Max 15% per position
    max_positions=10,                # Max 10 positions
    stop_loss_percent=2.0,           # Standard 2% stops
    use_take_profit=True,
    risk_reward_ratio=2.0            # Target 2:1 R:R
)

# Characteristics:
# - Moderate risk
# - Standard stops
# - Realistic R:R
# - Suitable for: Most traders, growth accounts
```

### Strategy 3: Aggressive (Maximum Growth)

```python
engine = RealisticBacktestEngine(
    initial_capital=200000.0,
    risk_per_trade_percent=2.0,      # Risk 2% per trade
    max_portfolio_heat=12.0,         # Max 12% total risk
    max_position_size_percent=25.0,  # Max 25% per position
    max_positions=15,                # Max 15 positions
    stop_loss_percent=3.0,           # Wider 3% stops
    stop_loss_type=StopLossType.TRAILING_PERCENT,
    trailing_stop_percent=4.0,       # Trail by 4%
    use_take_profit=False            # Let winners run
)

# Characteristics:
# - Higher risk per trade
# - Wider stops
# - No take-profits (exit on signal)
# - Suitable for: Experienced traders, high-risk tolerance
```

---

## 🔍 Comparing Results

### Scenario: $100,000 account, 100 trades

**Original Engine (No Risk Management)** ❌
```
Total trades: 100
Win rate: 55%
Avg win: $1,200
Avg loss: -$1,800
Total return: -$5,000 (-5%)
Max drawdown: -25%

Problem: Large losses wiped out small wins!
```

**Realistic Engine (With Risk Management)** ✅
```
Total trades: 100
Win rate: 55%
Avg win: $2,000
Avg loss: -$1,000 (stop-losses controlled)
Stop-loss rate: 35%
Take-profit rate: 20%
Realized R:R: 2:1
Expectancy: $200/trade
Total return: +$20,000 (+20%)
Max drawdown: -8%

Result: Small controlled losses, big winners!
```

---

## 📋 Checklist: Before Running Backtest

- [ ] **Set risk per trade** - Typically 0.5-2% of capital
- [ ] **Set portfolio heat limit** - Typically 5-10% maximum
- [ ] **Choose stop-loss type** - Fixed %, ATR, or Trailing
- [ ] **Set stop-loss distance** - Typically 1.5-3%
- [ ] **Enable take-profits?** - Yes for mechanical exits, No to let winners run
- [ ] **Set R:R ratio** - Typically 2:1 or 3:1
- [ ] **Set max positions** - Depends on strategy (5-15)
- [ ] **Set commission rate** - Match your broker (0.1% typical)
- [ ] **Set slippage rate** - Account for execution delays (0.05% typical)

---

## ⚠️ Common Mistakes to Avoid

### Mistake 1: Risk Too Much Per Trade
```python
# BAD
risk_per_trade_percent=5.0  # 5% per trade → Too risky!

# GOOD
risk_per_trade_percent=1.0  # 1% per trade → Sustainable
```

**Why:** Risking 5% means 10 consecutive losses = -50% drawdown

---

### Mistake 2: Stops Too Tight
```python
# BAD
stop_loss_percent=0.5  # 0.5% stop → Gets hit by noise

# GOOD
stop_loss_percent=2.0  # 2% stop → Room for normal volatility
```

**Why:** Tight stops lead to excessive stop-outs (>70%)

---

### Mistake 3: Unrealistic R:R Targets
```python
# BAD
risk_reward_ratio=10.0  # 10:1 R:R → Never hits

# GOOD
risk_reward_ratio=2.0  # 2:1 R:R → Realistic and achievable
```

**Why:** High R:R targets rarely get hit, reducing win rate

---

### Mistake 4: Ignoring Portfolio Heat
```python
# BAD
max_portfolio_heat=50.0  # 50% heat → Can lose half the account!

# GOOD
max_portfolio_heat=6.0  # 6% heat → Limited simultaneous risk
```

**Why:** Multiple losing positions at once can be catastrophic

---

## 🆚 Metric Targets

| Metric | Poor | Good | Excellent |
|--------|------|------|-----------|
| **Win Rate** | <45% | 50-60% | >65% |
| **R:R Ratio** | <1:1 | 1.5-2:1 | >2.5:1 |
| **Expectancy** | <$0 | $50-100 | >$150/trade |
| **Stop-Loss Rate** | >70% | 30-50% | <25% |
| **Max Drawdown** | >25% | 10-20% | <10% |
| **Sharpe Ratio** | <1.0 | 1.5-2.0 | >2.5 |

---

## 📊 Interpreting Results

### Good Backtest Results ✅
```
Win Rate: 58%
Stop-Loss Rate: 38%
Take-Profit Rate: 22%
Realized R:R: 2.1:1
Expectancy: $125/trade
Max Drawdown: -12%
```
**Interpretation:** Profitable system with controlled risk

### Warning Signs ⚠️
```
Win Rate: 42%
Stop-Loss Rate: 68%  ← TOO HIGH
Take-Profit Rate: 8%
Realized R:R: 0.8:1  ← TOO LOW
Expectancy: -$35/trade  ← NEGATIVE
Max Drawdown: -28%  ← TOO LARGE
```
**Interpretation:** System needs improvement (stops too tight, R:R too low)

---

## 🔧 Tuning Your Strategy

### If stop-loss rate is too high (>60%)...

1. **Widen stops:** Increase `stop_loss_percent` from 2% to 3%
2. **Use ATR stops:** Switch to `StopLossType.ATR_BASED`
3. **Filter signals:** Only take high-confidence signals (>70%)

### If take-profit rate is too low (<15%)...

1. **Lower R:R target:** Change from 3:1 to 2:1
2. **Use trailing stops:** Let winners run instead
3. **Check market conditions:** May not be trending enough

### If max drawdown is too large (>20%)...

1. **Reduce risk per trade:** From 2% to 1%
2. **Lower portfolio heat:** From 10% to 6%
3. **Tighten stops:** From 3% to 2%
4. **Add position limits:** Reduce `max_positions`

---

## 📚 Further Reading

- **Van Tharp's "Trade Your Way to Financial Freedom"** - Position sizing
- **Mark Douglas's "Trading in the Zone"** - Psychology of stops
- **Alexander Elder's "Trading for a Living"** - Stop-loss strategies
- **David Ryan's "Stock Market Wizards"** - Risk management

---

## ✅ Summary

### Key Improvements

✅ **Stop-Losses** - Automatic risk control on every trade  
✅ **Take-Profits** - Lock in gains at target levels  
✅ **Position Sizing** - Risk-based sizing (not dollar-based)  
✅ **Portfolio Heat** - Limit total portfolio risk exposure  
✅ **Trailing Stops** - Protect profits while letting winners run  
✅ **Realistic Metrics** - Expectancy, R:R ratio, stop-loss rate  

### Before vs. After

**Before:** Unrealistic backtest with unlimited downside  
**After:** Realistic backtest reflecting actual trading conditions  

### Next Steps

1. Review your current backtests with old engine
2. Re-run with realistic engine
3. Compare results (likely much different!)
4. Adjust parameters to meet your risk tolerance
5. Use realistic metrics for strategy optimization

---

**Happy (Realistic) Backtesting! 📊🎯**
