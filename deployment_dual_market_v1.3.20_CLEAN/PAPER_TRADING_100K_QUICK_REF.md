# 📊 PAPER TRADING $100K PATCH - Quick Reference Card

## 🎯 One-Line Summary
**Increases paper trading from $10,000 to $100,000 in 5 minutes with automated installer**

---

## 📦 Files to Copy to Windows

**Main File**: `PAPER_TRADING_100K_PATCH.zip` (62 KB)  
**From**: `/home/user/webapp/deployment_dual_market_v1.3.20_CLEAN/`  
**To**: `C:\Users\david\AATelS\`

---

## ⚡ Super Quick Install

```batch
# 1. Extract ZIP to C:\Users\david\AATelS\

# 2. Run installer
cd C:\Users\david\AATelS
PAPER_TRADING_100K_PATCH\INSTALL_PATCH.bat

# 3. Reset account
cd finbert_v4.4.4
python -c "from models.trading.paper_trading_engine import PaperTradingEngine; engine = PaperTradingEngine(); engine.reset_account(100000); print('✅ $100K')"

# 4. Verify
python -c "from models.trading.paper_trading_engine import PaperTradingEngine; account = PaperTradingEngine().get_account_summary()['account']; print(f'Cash: ${account[\"cash_balance\"]:,.2f}')"
```

**Expected**: `Cash: $100,000.00`

---

## 📝 What Changes

| File | Changes |
|------|---------|
| `trade_database.py` | 11 defaults: 10000→100000 |
| `paper_trading_engine.py` | 1 default: 10000→100000 |
| `portfolio_manager.py` | 1 default: 10000→100000 |
| `app_finbert_v4_dev.py` | 6 API defaults: 10000→100000 |
| `finbert_v4_enhanced_ui.html` | 3 UI values: $10K→$100K |

**Total**: 22 changes across 5 files

---

## ✅ Quick Checks

### Database Default
```batch
findstr /C:"DEFAULT 100000" finbert_v4.4.4\models\trading\trade_database.py
```

### Engine Default
```batch
findstr /C:"initial_capital: float = 100000" finbert_v4.4.4\models\trading\paper_trading_engine.py
```

### Web UI
```batch
findstr /C:"$100,000" finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html
```

All should return matches.

---

## 🔄 Quick Rollback

```batch
cd C:\Users\david\AATelS
dir finbert_v4.4.4\BACKUP_PAPER_TRADING_*
# Copy files from backup folder back to finbert_v4.4.4\
```

---

## 📚 Full Documentation

1. **Installation Guide**: `PAPER_TRADING_100K_INSTALLATION_GUIDE.md`
2. **Deployment Status**: `PAPER_TRADING_100K_DEPLOYMENT_COMPLETE.md`
3. **Summary**: `PAPER_TRADING_100K_SUMMARY.md`
4. **In-Patch Docs**: `PAPER_TRADING_100K_PATCH/README.txt`

---

## 🆘 Troubleshooting One-Liners

### Problem: Still shows $10,000 after reset
```batch
del finbert_v4.4.4\trading.db
# Restart app - will recreate with $100K
```

### Problem: Import errors
```batch
cd finbert_v4.4.4
for /d /r models\trading %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
```

### Problem: Web UI shows wrong amount
```batch
# Close Python, clear browser cache (Ctrl+Shift+Delete)
# Re-run INSTALL_PATCH.bat
```

---

## 🎯 Success Criteria

✅ `INSTALL_PATCH.bat` shows "ALL CHECKS PASSED"  
✅ Python command shows `Cash: $100,000.00`  
✅ Web UI Paper Trading shows `$100,000.00`  
✅ Reset button says "Reset to $100,000"

---

**Status**: PRODUCTION READY ✅  
**Version**: 1.0  
**Date**: 2025-12-04
