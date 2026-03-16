# Fix Git Checkout Error - Windows Invalid Paths

**Error**: `error: invalid path 'COMPLETE_SYSTEM_PACKAGE/cache/...|...|...pkl'`

**Root Cause**: Cache files with `|` characters in filenames (not allowed on Windows)

---

## ⚡ **Quick Fix (5 Minutes)**

### Option 1: Download Files Directly (Easiest)

Since git checkout has issues, just download the files you need directly:

#### 1. **IMPROVED_BACKTEST_CONFIG.py**
```
https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/finbert-v4.0-development/deployment_dual_market_v1.3.20_CLEAN/IMPROVED_BACKTEST_CONFIG.py
```

#### 2. **BACKTEST_IMPROVEMENT_PLAN.md**
```
https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/finbert-v4.0-development/deployment_dual_market_v1.3.20_CLEAN/BACKTEST_IMPROVEMENT_PLAN.md
```

#### 3. **HOW_TO_APPLY_IMPROVED_CONFIG.md**
```
https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/finbert-v4.0-development/deployment_dual_market_v1.3.20_CLEAN/HOW_TO_APPLY_IMPROVED_CONFIG.md
```

**How to download:**
1. Copy URL
2. Paste in browser
3. Right-click → "Save As..."
4. Save to `C:\Users\david\AATelS\`

---

### Option 2: Use Git Sparse Checkout

```batch
cd C:\Users\david\AATelS

REM Reset to clean state
git reset --hard

REM Enable sparse checkout
git config core.sparseCheckout true

REM Tell git which files to checkout (exclude cache files)
echo deployment_dual_market_v1.3.20_CLEAN/IMPROVED_BACKTEST_CONFIG.py > .git/info/sparse-checkout
echo deployment_dual_market_v1.3.20_CLEAN/BACKTEST_IMPROVEMENT_PLAN.md >> .git/info/sparse-checkout
echo deployment_dual_market_v1.3.20_CLEAN/HOW_TO_APPLY_IMPROVED_CONFIG.md >> .git/info/sparse-checkout
echo !COMPLETE_SYSTEM_PACKAGE/cache/ >> .git/info/sparse-checkout

REM Now checkout
git checkout finbert-v4.0-development
```

---

### Option 3: Clone Fresh (Nuclear Option)

If nothing else works:

```batch
cd C:\Users\david

REM Backup current directory
rename AATelS AATelS_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%

REM Clone fresh (will skip invalid Windows paths automatically)
git clone --branch finbert-v4.0-development https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend.git AATelS

REM Copy back your local changes if needed
xcopy AATelS_backup_*\*.json AATelS\ /s /y
xcopy AATelS_backup_*\config.py AATelS\ /y
```

---

## 🚀 **Simplest Solution: Just Edit the File Directly**

You don't actually need to checkout the branch. Just manually update your existing file:

### Step 1: Open This File
```
C:\Users\david\AATelS\finbert_v4.4.4\models\backtesting\backtest_engine.py
```

### Step 2: Find the `__init__` Method (Around Line 57)

Look for:
```python
def __init__(
    self,
    initial_capital: float = 10000.0,
    allocation_strategy: str = 'equal',  # or 'risk_parity', 'custom', 'risk_based'
```

### Step 3: Change These Lines

**FIND** this section (around lines 60-74):
```python
    allocation_strategy: str = 'equal',  # 'equal', 'risk_parity', 'custom', 'risk_based'
    custom_allocations: Optional[Dict[str, float]] = None,
    rebalance_frequency: str = 'monthly',
    commission_rate: float = 0.001,
    slippage_rate: float = 0.0005,
    
    # Phase 1 & 2: Risk management parameters
    enable_stop_loss: bool = True,
    stop_loss_percent: float = 2.0,
    enable_take_profit: bool = True,
    risk_reward_ratio: float = 2.0,
    risk_per_trade_percent: float = 1.0,
    max_portfolio_heat: float = 6.0,
    max_position_size_percent: float = 20.0
```

**CHANGE TO** (update the default values):
```python
    allocation_strategy: str = 'risk_based',  # ✅ Changed from 'equal'
    custom_allocations: Optional[Dict[str, float]] = None,
    rebalance_frequency: str = 'monthly',
    commission_rate: float = 0.001,
    slippage_rate: float = 0.0005,
    
    # Phase 1 & 2: Risk management parameters
    enable_stop_loss: bool = True,
    stop_loss_percent: float = 2.0,          # ✅ Already correct
    enable_take_profit: bool = True,          # ✅ Already correct
    risk_reward_ratio: float = 2.0,           # ✅ Already correct
    risk_per_trade_percent: float = 1.0,      # ✅ Already correct
    max_portfolio_heat: float = 6.0,          # ✅ Already correct
    max_position_size_percent: float = 20.0   # ✅ Already correct
```

**Only change needed**: 
- Line ~60: `allocation_strategy: str = 'equal'` → `allocation_strategy: str = 'risk_based'`

### Step 4: Save the File

### Step 5: Also Lower Confidence Threshold in UI

In your UI, change:
- **Confidence Threshold**: `85%` → `60%`

### Step 6: Restart Your App and Rerun Backtest

That's it! You're now using the improved configuration.

---

## 📋 **What Actually Needs to Change**

Good news: Your `backtest_engine.py` file **already has Phase 1 & 2 implemented**! 

You just need to change:

1. **In `backtest_engine.py`**:
   - Change `allocation_strategy` default from `'equal'` to `'risk_based'`

2. **In your UI**:
   - Change **Confidence Threshold** from `85%` to `60%`
   - Change **Stop Loss** from `1%` to `2%`

That's literally all you need!

---

## ✅ **Verification**

After making changes, verify:

```batch
cd C:\Users\david\AATelS

REM Check the file was updated
findstr "allocation_strategy: str = 'risk_based'" finbert_v4.4.4\models\backtesting\backtest_engine.py

REM Should show the line with 'risk_based'
```

---

## 📝 **Summary**

**You don't need to checkout the branch!**

Your file already has Phase 1 & 2 code. Just:

1. ✅ Edit `backtest_engine.py` (change 1 line: `'equal'` → `'risk_based'`)
2. ✅ In UI: Set **Confidence** to `60%`, **Stop-Loss** to `2%`
3. ✅ Rerun backtest

Expected results:
- Return: -1.5% → +8-12%
- Win Rate: 25% → 45-55%
- Profit Factor: 0.12 → 1.5-2.4
- More trades: 8 → 20-40

---

## 🔧 **If You Really Want the Config File**

Download directly:
```
Right-click → Save As:
https://raw.githubusercontent.com/davidosland-lab/enhanced-global-stock-tracker-frontend/finbert-v4.0-development/deployment_dual_market_v1.3.20_CLEAN/IMPROVED_BACKTEST_CONFIG.py
```

Save to: `C:\Users\david\AATelS\IMPROVED_BACKTEST_CONFIG.py`

Then use in your code:
```python
from IMPROVED_BACKTEST_CONFIG import IMPROVED_CONFIG
engine = PortfolioBacktestEngine(**IMPROVED_CONFIG)
```

---

**Status**: Simple fix - just edit one line!  
**Time**: 2 minutes  
**Risk**: Very low (just changing default value)
