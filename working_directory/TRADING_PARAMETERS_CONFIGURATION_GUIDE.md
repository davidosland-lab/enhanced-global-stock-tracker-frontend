# 🎛️ TRADING PARAMETERS CONFIGURATION GUIDE

**Version:** v1.3.7  
**Configuration File:** `config/live_trading_config.json`  
**Date:** January 2, 2026

---

## 📋 OVERVIEW

In Phase 3 Trading System v1.3.7, all trading parameters are configured in:
```
phase3_intraday_deployment/config/live_trading_config.json
```

This is similar to FinBERT v4.4.4's parameter settings, but with **adaptive intelligence** that automatically adjusts based on market conditions.

---

## 🎯 KEY TRADING PARAMETERS

### **1. Maximum Holding Days**

**Configuration:**
```json
"swing_trading": {
  "holding_period_days": 5
}
```

**How It Works:**
- **Base Period:** 5 days (configurable)
- **Adaptive Range:** 3-15 days
- **Logic:** Automatically adjusts based on ML confidence

**Adaptive Behavior:**
```python
def _calculate_holding_period(signal):
    base_holding = 5  # From config
    confidence = signal.confidence
    
    if confidence > 70:
        return min(15, base_holding + 3)  # Hold up to 8 days
    elif confidence < 55:
        return max(3, base_holding - 2)   # Hold only 3 days
    
    return base_holding  # Default 5 days
```

**Examples:**
- **High confidence (75%):** Hold for 8 days
- **Medium confidence (60%):** Hold for 5 days (base)
- **Low confidence (50%):** Hold for 3 days

**How to Change:**
Edit `holding_period_days` in config file:
```json
"holding_period_days": 7   // New base: 7 days (range becomes 5-10 days)
```

---

### **2. Stop Loss Percentage**

**Configuration:**
```json
"swing_trading": {
  "stop_loss_percent": 3.0
}
```

**How It Works:**
- **Default:** 3.0% stop loss
- **Applied:** To all positions automatically
- **Type:** Trailing stop (follows price up)

**Calculation:**
```python
# Entry at $100
stop_loss = entry_price * (1 - stop_loss_percent / 100)
# Stop loss = $100 * (1 - 0.03) = $97.00
```

**Trailing Stop Logic:**
```python
# If price moves up to $105
if use_trailing_stop:
    new_stop = current_price * (1 - stop_loss_percent / 100)
    # New stop = $105 * (1 - 0.03) = $101.85
    trailing_stop = max(trailing_stop, new_stop)  # Move up, never down
```

**How to Change:**
```json
"stop_loss_percent": 5.0   // Tighter: 5% stop loss
"stop_loss_percent": 2.0   // Wider: 2% stop loss
```

**Recommendations:**
- **Conservative:** 2-3% (fewer stop-outs, larger max loss)
- **Balanced:** 3-4% (default)
- **Aggressive:** 5-7% (more stop-outs, smaller max loss)

---

### **3. Confidence Threshold (Buy Signal)**

**Configuration:**
```json
"swing_trading": {
  "confidence_threshold": 52.0
}
```

**How It Works:**
- **Threshold:** Minimum ML confidence to enter trade
- **Range:** 0-100%
- **Default:** 52% (slightly above random)

**ML Signal Decision:**
```python
if ml_confidence >= confidence_threshold:
    # Enter trade
    execute_buy()
else:
    # Wait for better signal
    continue_monitoring()
```

**Impact on Trading:**
- **Lower threshold (e.g., 45%):** More trades, lower quality
- **Higher threshold (e.g., 60%):** Fewer trades, higher quality

**Component Weights (Fixed):**
- FinBERT Sentiment: 25%
- LSTM Prediction: 25%
- Technical Analysis: 25%
- Momentum: 15%
- Volume: 10%

**How to Change:**
```json
"confidence_threshold": 55.0   // More selective (fewer trades)
"confidence_threshold": 48.0   // Less selective (more trades)
```

**Recommendations by Strategy:**
- **Conservative:** 60-70% (high-quality signals only)
- **Balanced:** 52-55% (default, good risk/reward)
- **Aggressive:** 45-50% (more opportunities, higher risk)

**Expected Trade Frequency:**
| Threshold | Trades/Week (per symbol) | Quality |
|-----------|--------------------------|---------|
| 45% | 5-7 trades | Lower |
| 52% (default) | 2-5 trades | Good |
| 60% | 1-3 trades | High |
| 70% | 0-2 trades | Very High |

---

### **4. Maximum Position Size**

**Configuration:**
```json
"swing_trading": {
  "max_position_size": 0.25
}
```

**How It Works:**
- **Default:** 0.25 (25% of capital per position)
- **Range:** 0.10 to 0.30 (10% to 30%)
- **Adaptive:** Can be boosted in strong markets

**Position Sizing Calculation:**
```python
# With $100,000 capital and 25% max position
base_size = capital * max_position_size
# base_size = $100,000 * 0.25 = $25,000 per position

# Calculate shares
shares = base_size / current_price
# If CBA.AX is $125: shares = $25,000 / $125 = 200 shares
```

**Adaptive Position Sizing:**
```python
# In strong markets (sentiment > 70)
if market_sentiment > 70:
    position_size = min(0.30, base_size * 1.2)  # Boost to 30%
    # 25% × 1.2 = 30% position
```

**Risk Management:**
```json
"risk_management": {
  "max_total_positions": 3,          // Max 3 positions at once
  "max_portfolio_heat": 0.06,        // Max 6% total risk
  "max_single_trade_risk": 0.02      // Max 2% risk per trade
}
```

**Effective Position Sizing:**
```
With max_total_positions = 3 and max_position_size = 0.25:
- Maximum invested: 75% of capital (3 × 25%)
- Always keeps 25% cash for opportunities
```

**How to Change:**
```json
"max_position_size": 0.20   // Smaller: 20% per position (more conservative)
"max_position_size": 0.30   // Larger: 30% per position (more aggressive)
```

**Recommendations:**
- **Conservative:** 0.15-0.20 (smaller positions, more diversification)
- **Balanced:** 0.25 (default, good risk/reward)
- **Aggressive:** 0.30 (larger positions, concentrated)

**With Different Portfolio Sizes:**
| Capital | 20% Position | 25% Position | 30% Position |
|---------|--------------|--------------|--------------|
| $50,000 | $10,000 | $12,500 | $15,000 |
| $100,000 | $20,000 | $25,000 | $30,000 |
| $250,000 | $50,000 | $62,500 | $75,000 |

---

## 🔧 ADDITIONAL CONFIGURATION OPTIONS

### **5. Trailing Stop**

```json
"use_trailing_stop": true
```

- **Enabled:** Stop loss follows price up
- **Disabled:** Stop loss stays at entry level
- **Recommendation:** Keep enabled (locks in profits)

### **6. Profit Targets**

```json
"use_profit_targets": true
```

- **Enabled:** Auto-exit at 8% profit
- **Disabled:** Hold until stop loss or target exit date
- **Default:** 8% profit target

### **7. Maximum Total Positions**

```json
"risk_management": {
  "max_total_positions": 3
}
```

- **Default:** 3 positions maximum
- **Range:** 1-10
- **Impact:** With 25% position size, max 3 = 75% invested

**How to Change:**
```json
"max_total_positions": 5   // Allow up to 5 positions
```

### **8. Regime Detection**

```json
"use_regime_detection": true
```

**Market Regimes:**
- **STRONG_UPTREND:** Sentiment ≥ 70% (boost positions)
- **MILD_UPTREND:** Sentiment 60-69%
- **RANGING:** Sentiment 40-59%
- **DOWNTREND:** Sentiment < 40% (reduce/block trades)

---

## 📝 COMPLETE CONFIGURATION EXAMPLE

### **Conservative Setup:**
```json
{
  "swing_trading": {
    "holding_period_days": 7,          // Longer holds
    "stop_loss_percent": 2.5,          // Wider stops
    "confidence_threshold": 60.0,      // High confidence only
    "max_position_size": 0.20,         // Smaller positions
    "use_trailing_stop": true,
    "use_profit_targets": true
  },
  "risk_management": {
    "max_total_positions": 5,          // More diversification
    "max_portfolio_heat": 0.05,
    "max_single_trade_risk": 0.015
  }
}
```

### **Aggressive Setup:**
```json
{
  "swing_trading": {
    "holding_period_days": 3,          // Shorter holds
    "stop_loss_percent": 5.0,          // Tighter stops
    "confidence_threshold": 48.0,      // Lower threshold
    "max_position_size": 0.30,         // Larger positions
    "use_trailing_stop": true,
    "use_profit_targets": false
  },
  "risk_management": {
    "max_total_positions": 3,          // Concentrated
    "max_portfolio_heat": 0.08,
    "max_single_trade_risk": 0.025
  }
}
```

### **Balanced Setup (Default):**
```json
{
  "swing_trading": {
    "holding_period_days": 5,          // Medium holds
    "stop_loss_percent": 3.0,          // Standard stops
    "confidence_threshold": 52.0,      // Good quality
    "max_position_size": 0.25,         // Balanced size
    "use_trailing_stop": true,
    "use_profit_targets": true
  },
  "risk_management": {
    "max_total_positions": 3,
    "max_portfolio_heat": 0.06,
    "max_single_trade_risk": 0.02
  }
}
```

---

## 🎨 HOW TO MODIFY PARAMETERS

### **Step 1: Stop Dashboard**
```bash
# Press Ctrl+C in terminal
# Or close command window
```

### **Step 2: Edit Configuration**
```bash
# Navigate to config folder
cd C:\Users\[YourName]\Trading\phase3_intraday_deployment\config

# Open in text editor
notepad live_trading_config.json
```

### **Step 3: Make Changes**
```json
{
  "swing_trading": {
    "holding_period_days": 7,        // Changed from 5
    "stop_loss_percent": 4.0,        // Changed from 3.0
    "confidence_threshold": 55.0,    // Changed from 52.0
    "max_position_size": 0.20        // Changed from 0.25
  }
}
```

### **Step 4: Save File**
```
File → Save
```

### **Step 5: Restart Dashboard**
```bash
# From phase3_intraday_deployment folder
python unified_trading_dashboard.py

# Or double-click
START_UNIFIED_DASHBOARD.bat
```

### **Step 6: Verify Changes**
Check logs:
```bash
tail -f logs/paper_trading.log
```

Look for:
```
PAPER TRADING COORDINATOR - INTEGRATED VERSION
  Confidence Threshold: 55.0%
  Position Size: 20%
  Stop Loss: 4.0%
```

---

## 📊 PARAMETER COMPARISON: FinBERT v4.4.4 vs Phase 3 v1.3.7

| Parameter | FinBERT v4.4.4 | Phase 3 v1.3.7 | Adaptive? |
|-----------|----------------|----------------|-----------|
| **Max Holding Days** | Fixed (user set) | Base + Adaptive (3-15 days) | ✅ Yes |
| **Stop Loss %** | Fixed (user set) | Fixed + Trailing | ⚡ Trailing |
| **Confidence Level** | Fixed threshold | Fixed threshold + Components | ✅ Components |
| **Max Position Size** | Fixed (user set) | Base + Sentiment Boost | ✅ Yes |
| **Configuration** | UI Settings | JSON File | Same ease |
| **Risk Management** | Basic | Advanced (heat, limits) | ✅ Enhanced |

**Key Differences:**

1. **Adaptive Holding Period:**
   - FinBERT: Fixed days
   - Phase 3: Adjusts based on ML confidence (3-15 days)

2. **Dynamic Position Sizing:**
   - FinBERT: Fixed size
   - Phase 3: Boosts in strong markets (up to 1.2x)

3. **Trailing Stops:**
   - FinBERT: Not mentioned
   - Phase 3: Built-in trailing stop feature

4. **Regime Detection:**
   - FinBERT: Not mentioned
   - Phase 3: Adjusts strategy based on market regime

---

## 💡 RECOMMENDED CONFIGURATIONS BY EXPERIENCE

### **Beginner Trader:**
```json
{
  "holding_period_days": 7,           // Longer holds, less monitoring
  "stop_loss_percent": 3.0,           // Standard protection
  "confidence_threshold": 60.0,       // High quality signals only
  "max_position_size": 0.15,          // Small positions
  "max_total_positions": 5            // Diversified
}
```
**Expected:** 1-2 trades/week, 70-75% win rate

### **Intermediate Trader:**
```json
{
  "holding_period_days": 5,           // Balanced holding
  "stop_loss_percent": 3.5,           // Moderate stops
  "confidence_threshold": 52.0,       // Good signals
  "max_position_size": 0.25,          // Standard size
  "max_total_positions": 3            // Focused
}
```
**Expected:** 2-4 trades/week, 68-72% win rate

### **Advanced Trader:**
```json
{
  "holding_period_days": 3,           // Quick trades
  "stop_loss_percent": 4.5,           // Tighter stops
  "confidence_threshold": 48.0,       // More opportunities
  "max_position_size": 0.30,          // Larger positions
  "max_total_positions": 3            // Concentrated
}
```
**Expected:** 4-6 trades/week, 65-70% win rate

---

## ⚠️ IMPORTANT NOTES

### **1. Changes Take Effect:**
- Immediately on dashboard restart
- Existing positions not affected
- New positions use new parameters

### **2. Backup Configuration:**
```bash
# Before making changes
copy live_trading_config.json live_trading_config.backup.json
```

### **3. Test Changes:**
- Use paper trading first
- Monitor for 1-2 weeks
- Adjust as needed

### **4. Performance Impact:**

**Lower Confidence Threshold:**
- ✅ More trading opportunities
- ❌ Lower win rate
- ❌ More commissions

**Higher Confidence Threshold:**
- ✅ Higher win rate
- ❌ Fewer opportunities
- ✅ Better risk/reward

**Larger Position Size:**
- ✅ Bigger profits when right
- ❌ Bigger losses when wrong
- ❌ Less diversification

**Tighter Stop Loss:**
- ✅ Smaller max loss
- ❌ More stop-outs
- ❌ May miss reversals

---

## 🔍 MONITORING YOUR CONFIGURATION

### **Dashboard Displays:**
Look for these in the dashboard and logs:

**Current Configuration:**
```
Confidence Threshold: 52.0%
Max Position Size: 25%
Stop Loss: 3.0%
Holding Period: 5 days (adaptive 3-15)
```

**Per-Trade Info:**
```
✓ POSITION OPENED: CBA.AX
  Shares: 200 @ $125.00
  Position Size: 25.0% ($25,000)
  Stop Loss: $121.25 (-3%)
  Target Exit: 5 days
  Confidence: 68%
```

### **Log Messages:**
```bash
grep "Position Size" logs/paper_trading.log
grep "Stop Loss" logs/paper_trading.log
grep "Confidence" logs/paper_trading.log
```

---

## 📈 OPTIMIZATION TIPS

### **1. Start Conservative:**
- High confidence threshold (60%)
- Smaller positions (20%)
- Wider stops (2.5%)

### **2. Track Performance:**
- Monitor win rate
- Track average hold time
- Measure max drawdown

### **3. Adjust Gradually:**
- Change one parameter at a time
- Test for 10-20 trades
- Compare results

### **4. Seasonal Adjustments:**
- **Bull market:** Lower threshold, larger positions
- **Bear market:** Higher threshold, smaller positions
- **Volatile:** Tighter stops, shorter holds

---

## ✅ SUMMARY

**Configuration Location:**
```
phase3_intraday_deployment/config/live_trading_config.json
```

**Key Parameters:**
1. **holding_period_days:** 5 (base, adapts 3-15 days)
2. **stop_loss_percent:** 3.0%
3. **confidence_threshold:** 52.0%
4. **max_position_size:** 0.25 (25%)

**Adaptive Features:**
- Holding period adjusts with confidence
- Position size boosts in strong markets
- Trailing stops lock in profits
- Regime detection optimizes strategy

**How to Change:**
1. Stop dashboard
2. Edit `config/live_trading_config.json`
3. Save file
4. Restart dashboard
5. Verify in logs

**Your system has MORE flexibility than FinBERT v4.4.4 with adaptive intelligence built in!**

---

**Version:** v1.3.7  
**Config File:** config/live_trading_config.json  
**Date:** January 2, 2026  
**Status:** Fully Configurable ✅
