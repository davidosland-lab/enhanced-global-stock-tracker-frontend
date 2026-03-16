# Local System Diagnostic Tools

## 🎯 **Purpose**

These tools run **on your local system** to verify:
- ✅ All files are **latest versions**
- ✅ Files are in **correct locations**
- ✅ Configuration is **correct**
- ✅ Phase 2 features are **present**

**No cloud dependencies** - runs completely locally!

---

## 🛠️ **Available Tools**

### 1. **CHECK_SYSTEM.bat** (Windows)
**Native Windows batch script** - double-click to run

```batch
cd C:\Users\david\AATelS
CHECK_SYSTEM.bat
```

**Features:**
- Runs without Python
- Native Windows interface
- Checks all critical files
- Provides fix recommendations

---

### 2. **CHECK_SYSTEM.py** (Cross-Platform)
**Python script** - works on Windows, Mac, Linux

```bash
cd C:\Users\david\AATelS
python CHECK_SYSTEM.py
```

**Features:**
- Colored output (green/yellow/red)
- More detailed error messages
- Exit codes for automation
- Works on any OS with Python

---

## 📋 **What Gets Checked**

### ✓ **Directory Structure**
```
finbert_v4.4.4/
└── models/
    └── backtesting/
```

### ✓ **Required Files**
- `backtest_engine.py` (should be ~42,000 bytes)
- `portfolio_backtester.py` (should be ~30,000 bytes)
- `improved_backtest_config.py` (should be ~11,000 bytes)
- `phase1_phase2_example.py` (should be ~8,000 bytes)

### ✓ **Phase 2 Features in Code**
- `enable_take_profit` parameter
- `risk_reward_ratio` parameter
- `_check_take_profits` method
- `_check_stop_losses` method

### ✓ **Configuration Defaults**
- `allocation_strategy` = 'risk_based' ✅
- `enable_take_profit` = True ✅
- `stop_loss_percent` = 2.0 ✅

### ✓ **Diagnostic Tools Available**
- FIX_BACKTEST_ENGINE_DEFAULTS.py
- DIAGNOSTIC_BACKTEST_ISSUE.py
- VERIFY_PHASE2_INSTALLATION.py

---

## 🎨 **Output Colors**

### CHECK_SYSTEM.py (Python version):
```
[OK]    - Green  - Everything correct
[WARN]  - Yellow - Optional files missing
[ERROR] - Red    - Critical issues found
[INFO]  - Blue   - Informational messages
[ISSUE] - Red    - Configuration wrong
```

### CHECK_SYSTEM.bat (Windows version):
```
[OK]    - File exists and correct
[WARN]  - Optional issue
[ERROR] - Critical problem
[INFO]  - Information only
[ISSUE] - Configuration needs fixing
```

---

## 🚀 **Quick Start**

### Windows Users (Easiest):
1. Open Windows Explorer
2. Navigate to: `C:\Users\david\AATelS`
3. Double-click: `CHECK_SYSTEM.bat`
4. Read the results

### Python Users (Any OS):
1. Open Terminal/Command Prompt
2. Run:
   ```bash
   cd C:\Users\david\AATelS
   python CHECK_SYSTEM.py
   ```
3. Read the results

---

## 📊 **Sample Output**

```
====================================================================
  FINBERT v4.4.4 - SYSTEM FILE DIAGNOSTIC
====================================================================

[CHECK 1/6] Directory Structure...
  [OK] finbert_v4.4.4\models\backtesting

[CHECK 2/6] Required Files...
  [OK] backtest_engine.py (42,156 bytes) - Phase 2 code present
  [OK] improved_backtest_config.py (11,031 bytes)
  [OK] portfolio_backtester.py (32,450 bytes)
  [OK] phase1_phase2_example.py (8,234 bytes)

[CHECK 3/6] Phase 2 Features in Code...
  [OK] enable_take_profit parameter found
  [OK] risk_reward_ratio parameter found
  [OK] _check_take_profits method found
  [OK] _check_stop_losses method found

[CHECK 4/6] Configuration Defaults...
  [ISSUE] allocation_strategy = 'equal' (should be 'risk_based')
          This is causing your poor backtest results!
  [OK] enable_take_profit = True
  [OK] stop_loss_percent = 2.0

[CHECK 5/6] Diagnostic Tools Available...
  [OK] FIX_BACKTEST_ENGINE_DEFAULTS.py
  [OK] DIAGNOSTIC_BACKTEST_ISSUE.py
  [OK] VERIFY_PHASE2_INSTALLATION.py

[CHECK 6/6] Patch Folders...
  [INFO] PHASE1_PHASE2_PATCH folder not found (already installed?)
  [INFO] IMPROVED_CONFIG_PATCH folder not found (already installed?)

====================================================================
  DIAGNOSTIC RESULTS
====================================================================

  STATUS: [ISSUES FOUND] 1 issue(s) detected

  ISSUE 1: allocation_strategy = 'equal'
  FIX:     Run: python FIX_BACKTEST_ENGINE_DEFAULTS.py
```

---

## 🔧 **Common Issues & Fixes**

### Issue 1: allocation_strategy = 'equal'
**Fix:**
```bash
python FIX_BACKTEST_ENGINE_DEFAULTS.py
```

### Issue 2: Phase 2 code missing
**Fix:**
1. Download `PHASE1_PHASE2_PATCH.zip` from GitHub
2. Extract and run `INSTALL.bat`
3. Run `CHECK_SYSTEM.bat` again to verify

### Issue 3: File too small (outdated)
**Fix:**
1. Re-download the patch files
2. Reinstall patches
3. Verify installation

### Issue 4: enable_take_profit = False
**Fix:**
```bash
python FIX_BACKTEST_ENGINE_DEFAULTS.py
```

---

## 📁 **Expected File Locations**

```
C:\Users\david\AATelS\
├── CHECK_SYSTEM.bat                          ← Diagnostic tool (Windows)
├── CHECK_SYSTEM.py                           ← Diagnostic tool (Python)
├── FIX_BACKTEST_ENGINE_DEFAULTS.py           ← Automatic fixer
├── DIAGNOSTIC_BACKTEST_ISSUE.py              ← Full diagnostic
├── VERIFY_PHASE2_INSTALLATION.py             ← Phase 2 verifier
└── finbert_v4.4.4/
    └── models/
        └── backtesting/
            ├── backtest_engine.py            ← Main engine
            ├── portfolio_backtester.py       ← Portfolio engine
            ├── improved_backtest_config.py   ← Config file
            └── phase1_phase2_example.py      ← Example script
```

---

## 🎯 **When to Use Each Tool**

### Use CHECK_SYSTEM.bat/py When:
- ✅ After installing patches
- ✅ Before running backtests
- ✅ After downloading files from GitHub
- ✅ When results are unexpected
- ✅ To verify system is ready

### Use FIX_BACKTEST_ENGINE_DEFAULTS.py When:
- CHECK_SYSTEM finds configuration issues
- allocation_strategy = 'equal'
- enable_take_profit = False

### Use DIAGNOSTIC_BACKTEST_ISSUE.py When:
- Need detailed system analysis
- Results still poor after fixes
- Want comprehensive report

### Use VERIFY_PHASE2_INSTALLATION.py When:
- Need to verify Phase 2 patch installed
- Quick yes/no check needed
- Before running full diagnostic

---

## ⏱️ **How Long Does It Take?**

| Tool | Time |
|------|------|
| CHECK_SYSTEM.bat | 10 seconds |
| CHECK_SYSTEM.py | 10 seconds |
| FIX_BACKTEST_ENGINE_DEFAULTS.py | 15 seconds |
| VERIFY_PHASE2_INSTALLATION.py | 5 seconds |
| DIAGNOSTIC_BACKTEST_ISSUE.py | 30 seconds |

---

## 🆘 **Troubleshooting**

### "Wrong Directory" Error
**Problem:** Script can't find `finbert_v4.4.4` folder

**Solution:**
```bash
# Windows
cd C:\Users\david\AATelS
CHECK_SYSTEM.bat

# Or
C:
cd \Users\david\AATelS
python CHECK_SYSTEM.py
```

### "Python not found" Error
**Problem:** Python not installed or not in PATH

**Solution:**
- Use `CHECK_SYSTEM.bat` instead (no Python required)
- Or install Python from python.org

### "File not found" Error
**Problem:** Diagnostic tools not downloaded

**Solution:**
1. Go to GitHub PR #10
2. Download the diagnostic tools
3. Place in `C:\Users\david\AATelS`

---

## 📦 **Download Locations**

### GitHub:
```
https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/tree/finbert-v4.0-development/deployment_dual_market_v1.3.20_CLEAN
```

### PR #10:
```
https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/10
```

### Direct Links:
- CHECK_SYSTEM.bat
- CHECK_SYSTEM.py
- FIX_BACKTEST_ENGINE_DEFAULTS.py
- DIAGNOSTIC_BACKTEST_ISSUE.py
- VERIFY_PHASE2_INSTALLATION.py

All available in the latest commit on `finbert-v4.0-development` branch.

---

## ✅ **Success Criteria**

After running CHECK_SYSTEM, you should see:

```
STATUS: [OK] No critical issues found

Your system appears to be configured correctly.
```

If you see this, your system is ready to run backtests with optimal settings!

---

## 🎉 **Summary**

| Tool | Purpose | Platform | Time |
|------|---------|----------|------|
| CHECK_SYSTEM.bat | System check | Windows only | 10s |
| CHECK_SYSTEM.py | System check | All platforms | 10s |
| Both check | Files, versions, config | Local system | Fast |
| Output | Green/Yellow/Red status | Terminal/Console | Clear |
| Fix | Automatic fix available | FIX_BACKTEST_ENGINE_DEFAULTS.py | 15s |

**No cloud dependencies - runs 100% locally!**

---

**Created:** 2025-12-05  
**Commit:** 31a5ab3  
**Status:** ✅ Ready to use  
**Platform:** Windows, Mac, Linux  
**Requirements:** Windows batch OR Python 3.6+
