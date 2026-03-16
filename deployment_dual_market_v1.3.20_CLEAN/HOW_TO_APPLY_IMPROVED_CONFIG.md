# How to Apply Improved Backtest Configuration

**Quick Answer**: The config file is already on GitHub. Here's exactly how to get it and use it.

---

## 📥 **Step 1: Get the Improved Config File**

### Option A: Download from GitHub (Easiest)

1. **Go to GitHub PR #10**:
   ```
   https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/10
   ```

2. **Click "Files changed" tab**

3. **Find `IMPROVED_BACKTEST_CONFIG.py`**

4. **Click the file name** → **Click "..." menu** → **Download**

5. **Save to your project**:
   ```
   C:\Users\david\AATelS\IMPROVED_BACKTEST_CONFIG.py
   ```

### Option B: Pull from Git

```batch
cd C:\Users\david\AATelS
git fetch origin finbert-v4.0-development
git checkout finbert-v4.0-development
git pull origin finbert-v4.0-development
```

After this, `IMPROVED_BACKTEST_CONFIG.py` will be in your root directory.

### Option C: Download Direct Link

Download from:
```
https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/raw/finbert-v4.0-development/deployment_dual_market_v1.3.20_CLEAN/IMPROVED_BACKTEST_CONFIG.py
```

---

## 🎯 **Step 2: Where to Enable Take-Profit**

There are **3 places** you can enable take-profit:

### Place 1: In the UI (Screenshot You Showed)

Looking at your screenshot, you're using a web UI with a "Backtest Configuration" form.

**To add take-profit to your UI, you need to:**

1. **Find your frontend code**:
   ```
   Look for files containing "Backtest Configuration"
   Likely in: src/components/ or pages/ folder
   ```

2. **Add these input fields** to your form:
   ```jsx
   {/* Enable Take-Profit */}
   <div className="form-group">
     <label>Enable Take-Profit</label>
     <select value={enableTakeProfit} onChange={(e) => setEnableTakeProfit(e.target.value === 'true')}>
       <option value="true">Yes</option>
       <option value="false">No</option>
     </select>
   </div>

   {/* Risk:Reward Ratio */}
   {enableTakeProfit && (
     <div className="form-group">
       <label>Risk:Reward Ratio</label>
       <input 
         type="number" 
         value={riskRewardRatio} 
         onChange={(e) => setRiskRewardRatio(parseFloat(e.target.value))}
         step="0.1"
         min="1.0"
         max="5.0"
       />
       <small>Example: 2.0 = Exit at 2x risk distance</small>
     </div>
   )}

   {/* Max Portfolio Heat */}
   <div className="form-group">
     <label>Max Portfolio Heat (%)</label>
     <input 
       type="number" 
       value={maxPortfolioHeat} 
       onChange={(e) => setMaxPortfolioHeat(parseFloat(e.target.value))}
       step="0.5"
       min="0"
       max="20"
     />
     <small>Maximum total risk across all positions</small>
   </div>

   {/* Allocation Strategy */}
   <div className="form-group">
     <label>Allocation Strategy</label>
     <select value={allocationStrategy} onChange={(e) => setAllocationStrategy(e.target.value)}>
       <option value="equal_weight">Equal Weight</option>
       <option value="risk_based">Risk-Based (Recommended)</option>
       <option value="risk_parity">Risk Parity</option>
       <option value="custom">Custom</option>
     </select>
   </div>

   {/* Risk Per Trade (for risk-based) */}
   {allocationStrategy === 'risk_based' && (
     <div className="form-group">
       <label>Risk Per Trade (%)</label>
       <input 
         type="number" 
         value={riskPerTrade} 
         onChange={(e) => setRiskPerTrade(parseFloat(e.target.value))}
         step="0.1"
         min="0.1"
         max="5.0"
       />
       <small>Risk per trade as % of capital (recommended: 1.0%)</small>
     </div>
   )}
   ```

3. **Update your API call** to include these parameters:
   ```javascript
   const backtestConfig = {
     symbol: symbol,
     startDate: startDate,
     endDate: endDate,
     initialCapital: initialCapital,
     positionSize: positionSize,
     confidenceThreshold: confidenceThreshold,
     stopLoss: stopLoss,
     modelType: modelType,
     
     // NEW: Add these parameters
     enableTakeProfit: enableTakeProfit,
     riskRewardRatio: riskRewardRatio,
     maxPortfolioHeat: maxPortfolioHeat,
     allocationStrategy: allocationStrategy,
     riskPerTrade: riskPerTrade,
     maxPositionSize: maxPositionSize,
   };

   // Send to backend
   fetch('/api/backtest', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify(backtestConfig)
   });
   ```

---

### Place 2: In Your Backend API

If you have a Flask/FastAPI backend, update the backtest endpoint:

**File**: `app.py` or `api/backtest.py`

```python
from flask import Flask, request, jsonify
from finbert_v4.4.4.models.backtesting.backtest_engine import PortfolioBacktestEngine

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    config = request.get_json()
    
    # Create engine with improved config
    engine = PortfolioBacktestEngine(
        initial_capital=config.get('initialCapital', 100000),
        allocation_strategy=config.get('allocationStrategy', 'risk_based'),  # NEW
        risk_per_trade_percent=config.get('riskPerTrade', 1.0),            # NEW
        max_position_size_percent=config.get('maxPositionSize', 20.0),     # NEW
        
        # Phase 1: Stop-Loss
        enable_stop_loss=True,
        stop_loss_percent=config.get('stopLoss', 2.0),                     # Changed default
        
        # Phase 2: Take-Profit (NEW)
        enable_take_profit=config.get('enableTakeProfit', True),           # NEW
        risk_reward_ratio=config.get('riskRewardRatio', 2.0),             # NEW
        max_portfolio_heat=config.get('maxPortfolioHeat', 6.0),           # NEW
        
        # Transaction costs
        commission_rate=0.001,
        slippage_rate=0.0005,
    )
    
    # Run backtest
    results = engine.backtest(
        symbols=[config['symbol']],
        start_date=config['startDate'],
        end_date=config['endDate'],
        confidence_threshold=config.get('confidenceThreshold', 0.60)       # Changed default
    )
    
    return jsonify(results)
```

---

### Place 3: Directly in Python Code

If you're running backtests from Python scripts:

**File**: Your backtest script (e.g., `run_backtest.py`)

```python
from IMPROVED_BACKTEST_CONFIG import IMPROVED_CONFIG
from finbert_v4.4.4.models.backtesting.backtest_engine import PortfolioBacktestEngine

# Option 1: Use the improved config directly
engine = PortfolioBacktestEngine(**IMPROVED_CONFIG)

# Option 2: Customize the improved config
custom_config = IMPROVED_CONFIG.copy()
custom_config['risk_per_trade_percent'] = 1.5  # Adjust as needed
engine = PortfolioBacktestEngine(**custom_config)

# Option 3: Create engine with explicit parameters
engine = PortfolioBacktestEngine(
    initial_capital=100000,
    
    # Allocation
    allocation_strategy='risk_based',
    risk_per_trade_percent=1.0,
    max_position_size_percent=20.0,
    
    # Phase 1: Stop-Loss
    enable_stop_loss=True,
    stop_loss_percent=2.0,
    
    # Phase 2: Take-Profit
    enable_take_profit=True,           # ✅ Enable take-profit
    risk_reward_ratio=2.0,             # ✅ 2:1 R:R
    max_portfolio_heat=6.0,            # ✅ Max 6% total risk
    
    # Costs
    commission_rate=0.001,
    slippage_rate=0.0005,
)

# Run backtest
results = engine.backtest(
    symbols=['TCI.AX'],
    start_date='2024-01-01',
    end_date='2025-12-31',
    confidence_threshold=0.60  # ✅ Lower to 60%
)

print(f"Total Return: {results['total_return']:.2f}%")
print(f"Win Rate: {results['win_rate']*100:.1f}%")
print(f"Profit Factor: {results['profit_factor']:.2f}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

---

## 🚀 **Quick Fix Without Code Changes**

If you can't modify the UI code right now, you can **temporarily edit the backend defaults**:

**File**: `finbert_v4.4.4/models/backtesting/backtest_engine.py`

Find the `__init__` method and change the defaults:

```python
def __init__(
    self,
    initial_capital: float = 10000.0,
    allocation_strategy: str = 'risk_based',      # Changed from 'equal'
    ...
    enable_stop_loss: bool = True,
    stop_loss_percent: float = 2.0,               # Changed from 1.0
    enable_take_profit: bool = True,              # Changed from False
    risk_reward_ratio: float = 2.0,               # Added
    risk_per_trade_percent: float = 1.0,          # Added
    max_portfolio_heat: float = 6.0,              # Added
    max_position_size_percent: float = 20.0       # Added
):
```

This way, even if the UI doesn't send these parameters, the backend will use good defaults.

---

## 📝 **Step 3: Update Your UI Form**

Based on your screenshot, you need to add these fields to your form:

### Current Fields (You Have):
- ✅ Stock Symbol
- ✅ Model Type
- ✅ Start Date
- ✅ End Date
- ✅ Initial Capital
- ✅ Position Size (%)
- ✅ Confidence Threshold (%)
- ✅ Stop Loss (%)

### Missing Fields (Need to Add):

#### 1. **Enable Take-Profit** (Dropdown)
- Label: "Enable Take-Profit"
- Options: Yes / No
- Default: **Yes**
- Help Text: "Automatically exit at profit target"

#### 2. **Risk:Reward Ratio** (Number Input)
- Label: "Risk:Reward Ratio"
- Min: 1.0, Max: 5.0, Step: 0.1
- Default: **2.0**
- Help Text: "Exit at 2x risk distance (e.g., risk $1, target $2 profit)"

#### 3. **Allocation Strategy** (Dropdown)
- Label: "Allocation Strategy"
- Options: 
  - Equal Weight
  - **Risk-Based (Recommended)**
  - Risk Parity
  - Custom
- Default: **Risk-Based**
- Help Text: "How to size positions"

#### 4. **Risk Per Trade** (Number Input)
- Label: "Risk Per Trade (%)"
- Min: 0.1, Max: 5.0, Step: 0.1
- Default: **1.0**
- Help Text: "Risk per trade as % of capital"
- Show only when: Allocation Strategy = "Risk-Based"

#### 5. **Max Portfolio Heat** (Number Input)
- Label: "Max Portfolio Heat (%)"
- Min: 0, Max: 20, Step: 0.5
- Default: **6.0**
- Help Text: "Maximum total risk across all positions"

#### 6. **Max Position Size** (Number Input)
- Label: "Max Position Size (%)"
- Min: 1, Max: 100, Step: 1
- Default: **20**
- Help Text: "Maximum size of single position"

---

## 🎨 **Example: Updated UI Form (HTML)**

```html
<!-- Existing fields ... -->

<!-- NEW: Enable Take-Profit -->
<div class="form-group">
  <label for="enableTakeProfit">Enable Take-Profit</label>
  <select id="enableTakeProfit" name="enableTakeProfit" class="form-control">
    <option value="true" selected>Yes</option>
    <option value="false">No</option>
  </select>
  <small class="form-text text-muted">Automatically exit at profit target</small>
</div>

<!-- NEW: Risk:Reward Ratio -->
<div class="form-group" id="riskRewardGroup">
  <label for="riskRewardRatio">Risk:Reward Ratio</label>
  <input 
    type="number" 
    id="riskRewardRatio" 
    name="riskRewardRatio" 
    class="form-control" 
    value="2.0" 
    min="1.0" 
    max="5.0" 
    step="0.1"
  />
  <small class="form-text text-muted">2.0 = Exit at 2x risk distance</small>
</div>

<!-- NEW: Allocation Strategy -->
<div class="form-group">
  <label for="allocationStrategy">Allocation Strategy</label>
  <select id="allocationStrategy" name="allocationStrategy" class="form-control">
    <option value="equal_weight">Equal Weight</option>
    <option value="risk_based" selected>Risk-Based (Recommended)</option>
    <option value="risk_parity">Risk Parity</option>
    <option value="custom">Custom</option>
  </select>
  <small class="form-text text-muted">How to size positions</small>
</div>

<!-- NEW: Risk Per Trade (shown when risk_based selected) -->
<div class="form-group" id="riskPerTradeGroup">
  <label for="riskPerTrade">Risk Per Trade (%)</label>
  <input 
    type="number" 
    id="riskPerTrade" 
    name="riskPerTrade" 
    class="form-control" 
    value="1.0" 
    min="0.1" 
    max="5.0" 
    step="0.1"
  />
  <small class="form-text text-muted">Risk per trade as % of capital (recommended: 1.0%)</small>
</div>

<!-- NEW: Max Portfolio Heat -->
<div class="form-group">
  <label for="maxPortfolioHeat">Max Portfolio Heat (%)</label>
  <input 
    type="number" 
    id="maxPortfolioHeat" 
    name="maxPortfolioHeat" 
    class="form-control" 
    value="6.0" 
    min="0" 
    max="20" 
    step="0.5"
  />
  <small class="form-text text-muted">Maximum total risk across all positions</small>
</div>

<!-- Update Stop Loss default -->
<div class="form-group">
  <label for="stopLoss">Stop Loss (%)</label>
  <input 
    type="number" 
    id="stopLoss" 
    name="stopLoss" 
    class="form-control" 
    value="2" 
    min="0" 
    max="10" 
    step="0.1"
  />
  <small class="form-text text-muted">Changed from 1% to 2% (less whipsaw)</small>
</div>

<!-- Update Confidence Threshold default -->
<div class="form-group">
  <label for="confidenceThreshold">Confidence Threshold (%)</label>
  <input 
    type="number" 
    id="confidenceThreshold" 
    name="confidenceThreshold" 
    class="form-control" 
    value="60" 
    min="0" 
    max="100" 
    step="1"
  />
  <small class="form-text text-muted">Changed from 85% to 60% (more trades)</small>
</div>

<!-- Add JavaScript to show/hide risk per trade field -->
<script>
document.getElementById('allocationStrategy').addEventListener('change', function() {
  const riskPerTradeGroup = document.getElementById('riskPerTradeGroup');
  if (this.value === 'risk_based') {
    riskPerTradeGroup.style.display = 'block';
  } else {
    riskPerTradeGroup.style.display = 'none';
  }
});

document.getElementById('enableTakeProfit').addEventListener('change', function() {
  const riskRewardGroup = document.getElementById('riskRewardGroup');
  if (this.value === 'true') {
    riskRewardGroup.style.display = 'block';
  } else {
    riskRewardGroup.style.display = 'none';
  }
});
</script>
```

---

## 🔍 **Finding Your UI Code**

Your backtest form is likely in one of these files:

```batch
cd C:\Users\david\AATelS

REM Search for "Backtest Configuration"
findstr /s /i "Backtest Configuration" *.html *.jsx *.tsx *.js *.ts

REM Search for "Stop Loss"
findstr /s /i "Stop Loss" *.html *.jsx *.tsx *.js *.ts

REM Search for "Confidence Threshold"
findstr /s /i "Confidence Threshold" *.html *.jsx *.tsx *.js *.ts
```

Common locations:
- `src/components/Backtest.tsx`
- `src/pages/Backtest.tsx`
- `frontend/src/components/BacktestForm.jsx`
- `public/index.html`
- `templates/backtest.html` (if Flask)

---

## 💡 **Quick Temporary Fix (No Code Changes)**

If you can't update the UI right now, you can manually set better defaults in the backend:

1. **Open**: `finbert_v4.4.4/models/backtesting/backtest_engine.py`

2. **Find the `__init__` method** (around line 57)

3. **Change the default values**:
   ```python
   def __init__(
       self,
       initial_capital: float = 10000.0,
       allocation_strategy: str = 'risk_based',         # Change from 'equal'
       ...
       stop_loss_percent: float = 2.0,                  # Change from 1.0
       enable_take_profit: bool = True,                 # Change from False
       risk_reward_ratio: float = 2.0,                  # Add if missing
       risk_per_trade_percent: float = 1.0,             # Add if missing
       max_portfolio_heat: float = 6.0,                 # Add if missing
       max_position_size_percent: float = 20.0          # Add if missing
   ):
   ```

4. **Save the file**

5. **Restart your app**

Now even without UI changes, the backend will use better defaults!

---

## ✅ **Summary**

### To Get the Config File:
1. **Download from GitHub** (link in Step 1 above)
2. OR **Pull from git**: `git pull origin finbert-v4.0-development`
3. File location: `C:\Users\david\AATelS\IMPROVED_BACKTEST_CONFIG.py`

### To Enable Take-Profit:
1. **Option 1**: Add UI fields (see example HTML above)
2. **Option 2**: Update backend API (see Python example above)
3. **Option 3**: Change backend defaults temporarily (see Quick Fix above)

### Easiest Path:
1. **Change backend defaults** in `backtest_engine.py` (5 minutes)
2. **Rerun your backtest** with same UI
3. See improved results immediately!

---

**Need help finding your UI code?** 

Run this command and share the output:
```batch
cd C:\Users\david\AATelS
findstr /s /i "Backtest Configuration" *
```

I can then tell you exactly which file to edit!

---

**Created**: 2025-12-05  
**Files**: IMPROVED_BACKTEST_CONFIG.py, backtest_engine.py  
**Status**: Ready to apply ✅
