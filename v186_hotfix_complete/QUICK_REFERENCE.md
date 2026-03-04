# v186 HOTFIX - QUICK REFERENCE CARD

## 🔴 PROBLEM
Trades blocked: confidence threshold too high (65% vs. should be 48%)

## ✅ SOLUTION
Apply v186 hotfix to lower threshold

---

## ⚡ QUICK INSTALL (30 seconds)

```powershell
# 1. Go to your trading system directory
cd "C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15"

# 2. Copy patch script from extracted hotfix
Copy-Item "PATH_TO_HOTFIX\APPLY_V186_HOTFIX.py" -Destination "."

# 3. Run patch
python APPLY_V186_HOTFIX.py

# 4. Launch dashboard
python unified_trading_dashboard.py
```

---

## 📋 WHAT GETS CHANGED

| File | Line | Old Value | New Value |
|------|------|-----------|-----------|
| `config/live_trading_config.json` | 4 | `52.0` | `45.0` |
| `ml_pipeline/swing_signal_generator.py` | 81 | `0.52` | `0.48` |
| `ml_pipeline/swing_signal_generator.py` | 95 | `52%` | `48%` |
| `ml_pipeline/swing_signal_generator.py` | 600 | `> 0.52` | `> 0.48` |

---

## ✅ VERIFICATION (5 seconds)

```powershell
# Check config
Get-Content "config\live_trading_config.json" | Select-String "confidence_threshold"
# Should show: "confidence_threshold": 45.0,

# Check code
Get-Content "ml_pipeline\swing_signal_generator.py" | Select-String "confidence_threshold: float"
# Should show: confidence_threshold: float = 0.48,
```

---

## 📊 EXPECTED RESULTS

### BEFORE (Blocked)
```
❌ TRADE BLOCKED: RIO.AX signal confidence 54.4% below threshold (65.0%)
```

### AFTER (Passed)
```
✅ Entry signal detected for RIO.AX: BUY with confidence 0.54
✅ Signal PASSED threshold check (54.4% >= 48.0%)
```

---

## 🔄 ROLLBACK

```powershell
Copy-Item "config\live_trading_config.json.v186_backup" -Destination "config\live_trading_config.json" -Force
Copy-Item "ml_pipeline\swing_signal_generator.py.v186_backup" -Destination "ml_pipeline\swing_signal_generator.py" -Force
```

---

## 📁 PACKAGE CONTENTS

- `README.md` - Full documentation
- `MANUAL_PATCH_GUIDE.md` - Step-by-step manual patching
- `APPLY_V186_HOTFIX.py` - Automated patch script
- `QUICK_REFERENCE.md` - This file
- `config/live_trading_config.json` - Reference config

---

## 🐛 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| "Cannot detect trading system" | Run from trading system root directory |
| Changes don't work | Restart dashboard completely |
| Script not found | Copy APPLY_V186_HOTFIX.py to trading system root |

---

## 📞 NEED HELP?

1. Read README.md for full documentation
2. Try MANUAL_PATCH_GUIDE.md for manual patching
3. Check backups were created (.v186_backup files)

---

**Version:** v186  
**Date:** 2026-02-25  
**Install Time:** ~30 seconds  
**Difficulty:** Easy
