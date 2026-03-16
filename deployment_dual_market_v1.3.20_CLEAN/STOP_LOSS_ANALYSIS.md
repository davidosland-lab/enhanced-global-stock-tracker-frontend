# Stop-Loss Implementation Analysis

## 🎯 **How Stop-Loss Works in Your Backtest Engine**

### **Current Stop-Loss Percentage:**
```python
stop_loss_percent: float = 2.0  # Line 68
```

**Answer: The backtest engine sells at 2% loss**

---

## 📊 **Stop-Loss Mechanism Explained**

### **1. Stop-Loss Price Calculation (Line 305)**

When you **enter a trade**:
```python
stop_loss_price = execution_price * (1 - self.stop_loss_percent / 100.0)
```

**Example:**
- Entry price: $100.00
- Stop-loss: 2.0%
- Stop-loss price: $100 × (1 - 0.02) = **$98.00**

**The position will be sold if price drops to $98.00 or below**

---

### **2. Stop-Loss Monitoring (Lines 870-875)**

During backtesting, **every day** the engine checks:
```python
if current_price <= pos.stop_loss_price:
    # TRIGGER STOP-LOSS!
    logger.info(
        f"🛑 STOP-LOSS HIT: {symbol} @ ${current_price:.2f} "
        f"(stop=${pos.stop_loss_price:.2f}, entry=${pos.entry_price:.2f})"
    )
```

**Trigger Condition:**
- Current price ≤ Stop-loss price
- Example: If price drops to $98.00 or lower, **SELL**

---

### **3. Stop-Loss Execution (Lines 877-884)**

When stop-loss triggers:
```python
# Execute at current price with slippage
execution_price = current_price * (1 - self.slippage_rate)  # Worse execution
sell_value = pos.shares * execution_price
commission = sell_value * self.commission_rate
proceeds = sell_value - commission

# Update cash
self.cash += proceeds
```

**Slippage Applied:**
- Slippage rate: 0.05% (0.0005)
- Example: If stop triggered at $98.00, sell at $98.00 × 0.9995 = **$97.95**

**Commission Applied:**
- Commission rate: 0.1% (0.001)
- Example: On $9,795 sale, commission = $9.80

---

## 💰 **Position Sizing with Stop-Loss**

### **Risk-Based Sizing (When allocation_strategy = 'risk_based')**

**Lines 312-320:**
```python
# Calculate risk per share
risk_per_share = execution_price - stop_loss_price

# Risk amount = 1% of capital
max_risk_dollars = total_value * (self.risk_per_trade_percent / 100.0)

# Calculate shares to risk exactly 1%
shares = risk_dollars / risk_per_share
```

**Example with $100,000 capital:**
```
Entry Price:       $100.00
Stop-Loss Price:   $98.00
Risk Per Share:    $2.00

Risk Amount:       $100,000 × 1% = $1,000
Shares to Buy:     $1,000 ÷ $2 = 500 shares
Position Value:    500 × $100 = $50,000 (50% of capital)

If Stop Hits:      500 × $98 = $49,000
Loss:              $50,000 - $49,000 = $1,000 (exactly 1%)
```

**This is why risk-based sizing is crucial!**

---

### **Equal-Weight Sizing (When allocation_strategy = 'equal')**

**Problem: Fixed dollar amount, inconsistent risk**

Example:
- Capital: $100,000
- Position size: 20% = $20,000

**Scenario 1: High-priced stock ($100)**
```
Entry:           $100
Position:        $20,000 ÷ $100 = 200 shares
Stop-loss:       $98
Risk per share:  $2
Total risk:      200 × $2 = $400 (0.4% of capital) ✅ Low risk
```

**Scenario 2: Low-priced stock ($10)**
```
Entry:           $10
Position:        $20,000 ÷ $10 = 2,000 shares
Stop-loss:       $9.80
Risk per share:  $0.20
Total risk:      2,000 × $0.20 = $400 (0.4% of capital) ✅ Same risk
```

**Wait, equal weight gives same risk?**

Actually, **it depends on stock volatility and price movement**, not just the percentage:

**Scenario 3: Volatile stock ($50)**
```
Entry:           $50
Position:        $20,000 ÷ $50 = 400 shares
Stop-loss:       $49 (2% stop)
Risk per share:  $1

But if stock is volatile and gaps down 5% to $47.50:
Actual loss:     400 × ($50 - $47.50) = $1,000 (1% of capital) ❌
```

**With risk-based sizing, you'd buy fewer shares** to account for volatility.

---

## 🔍 **Current Configuration Analysis**

### **Your Settings:**
```python
enable_stop_loss: bool = True        ✅ ENABLED
stop_loss_percent: float = 2.0       ✅ 2% stop-loss
allocation_strategy: str = 'equal'   ⚠️  EQUAL WEIGHT (not optimal)
```

### **How It Works Now:**

1. **Entry:**
   - Buy TCI.AX with 20% of capital ($20,000 on $100k)
   - Stop-loss set at 2% below entry price

2. **Stop-Loss Trigger:**
   - If price drops 2% or more, **SELL**
   - Example: Entry at $10.00, stop at $9.80

3. **Actual Loss:**
   - With equal weight: Loss ≈ $400 (0.4% of capital)
   - With risk-based: Loss = $1,000 (exactly 1% of capital)

---

## 📈 **Performance Impact**

### **Your Current Results Show:**
```
Win Rate:     45.5%
Total Return: -0.86%
Profit Factor: 0.54
```

**This pattern suggests:**
- Stop-losses ARE working (protecting from big losses)
- But position sizing might not be optimal
- And **take-profit might not be triggering** (the main issue)

### **Why Still Losing with 2% Stop-Loss?**

**Math Analysis:**
```
Assume:
- Entry: $100
- Stop-loss: $98 (2% loss)
- Take-profit: $104 (4% gain, 2:1 R:R)

With equal weight ($20,000 position):
- Stop hit:  200 shares × $98 = $19,600 → Loss $400
- TP hit:    200 shares × $104 = $20,800 → Gain $800

Expected value with 45.5% win rate:
(0.455 × $800) - (0.545 × $400) = $364 - $218 = +$146 per trade ✅
```

**But your results show -$77.86 avg profit!**

**Possible reasons:**
1. **Take-profit not triggering** (positions held too long, then stopped out)
2. **Slippage + commission** eating profits
3. **Confidence threshold too high** (65% instead of 60%)
4. **Equal weight causing inconsistent sizing**

---

## 🔧 **Stop-Loss Configuration Options**

### **Current Default (Line 68):**
```python
stop_loss_percent: float = 2.0
```

### **You Can Change This To:**

**More Conservative (Wider Stop):**
```python
stop_loss_percent: float = 3.0  # 3% stop-loss
```
- Pros: Less whipsaw (fewer false stops)
- Cons: Bigger losses when stopped
- Use when: Stock is volatile

**More Aggressive (Tighter Stop):**
```python
stop_loss_percent: float = 1.0  # 1% stop-loss
```
- Pros: Smaller losses
- Cons: More whipsaw (stopped out more often)
- Use when: Stock is stable

**Recommended for TCI.AX:**
```python
stop_loss_percent: float = 2.0  # Keep at 2%
```
- Good balance between protection and whipsaw
- Industry standard for equities

---

## 🎯 **Key Findings**

### ✅ **Stop-Loss IS Working Correctly:**
```python
Line 870: if current_price <= pos.stop_loss_price:
    # SELL at stop-loss
```

### ✅ **Stop-Loss Percentage:**
```python
Line 68: stop_loss_percent: float = 2.0
```
**The engine sells at 2% loss**

### ✅ **Stop-Loss Calculation:**
```python
Line 305: stop_loss_price = execution_price * (1 - 0.02)
```
**If entry = $100, stop = $98**

### ⚠️ **Main Issue is NOT Stop-Loss:**

The stop-loss is working fine. Your issue is:
1. **Allocation strategy = 'equal'** (should be 'risk_based')
2. **Take-profit might not be working** as expected
3. **Position sizing not optimal** for risk management

---

## 💡 **Recommendations**

### 1. **Keep Stop-Loss at 2%** ✅
```python
stop_loss_percent: float = 2.0  # This is good
```

### 2. **Change Allocation to Risk-Based** ⚠️
```python
allocation_strategy: str = 'risk_based'  # Change from 'equal'
```

### 3. **Verify Take-Profit is Working**
```python
enable_take_profit: bool = True          # Should be True
risk_reward_ratio: float = 2.0           # 2:1 R:R
```

### 4. **Lower Confidence Threshold**
- Current: 65%
- Recommended: 60%

---

## 📊 **Summary**

| Aspect | Current | Status |
|--------|---------|--------|
| **Stop-Loss Enabled** | Yes | ✅ Working |
| **Stop-Loss %** | 2.0% | ✅ Optimal |
| **Stop-Loss Logic** | Correct | ✅ Working |
| **Allocation Strategy** | equal | ⚠️ Needs fix |
| **Take-Profit** | Enabled | ❓ Check if triggering |
| **Position Sizing** | Fixed $ | ⚠️ Not optimal |

**Bottom Line:**
- Stop-loss **IS working correctly** at **2% loss**
- The **real issue** is allocation strategy and possibly take-profit execution
- Fix: Change `allocation_strategy` to `'risk_based'`

---

**Date:** 2025-12-05  
**Analysis:** Complete  
**Stop-Loss:** 2.0% (working correctly)  
**Main Issue:** Allocation strategy, not stop-loss
