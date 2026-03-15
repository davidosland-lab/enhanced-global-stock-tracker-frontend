# QUICK START - v1.3.15.116

## ✅ What's New in This Version

**TWO CRITICAL FIXES:**
1. 🔴 **24hr Market Chart** - Now updates continuously (was frozen on yesterday's data)
2. 📂 **HTML Reports** - Now save to correct location (was hidden in pipelines folder)

---

## 🚀 Fresh Installation (New Users)

### Step 1: Extract
Extract ZIP to your desired location:
```
Example: C:\Users\david\Regime Trading V2\
```

### Step 2: Install
```batch
Right-click: INSTALL_COMPLETE.bat
Select: "Run as Administrator"
Wait: ~20-25 minutes
```

### Step 3: Start
```batch
Double-click: START.bat
Select: Option 1 (Complete System) or Option 5 (AU Pipeline Only)
```

### Step 4: Verify
- ✅ 24hr chart shows 4 market indices updating live
- ✅ HTML reports appear in `reports\morning_reports\`
- ✅ Dashboard loads without errors

**Done!** Both fixes are already included.

---

## 🔄 Update Existing Installation

### Option 1: Quick File Update (Recommended)

**For 24hr Chart Fix:**
1. Stop dashboard (Ctrl+C in START.bat)
2. Backup: `copy core\unified_trading_dashboard.py core\unified_trading_dashboard.py.backup`
3. Extract new `core\unified_trading_dashboard.py` from ZIP
4. Restart: Run START.bat

**For HTML Report Fix:**
1. Extract new `pipelines\models\screening\report_generator.py` from ZIP
2. No restart needed (applies to next pipeline run)

**Time**: 2 minutes + restart time

---

### Option 2: Full Reinstall (Safest)

1. Stop dashboard (Ctrl+C in START.bat)
2. Backup entire folder (copy to safe location)
3. Extract new ZIP over existing installation
4. Run START.bat

**Time**: 5 minutes + restart time

---

## ✅ Verification Steps

### Check 1: Market Chart Working
```
1. Open dashboard in browser
2. Look at "24hr Global Market Performance" chart
3. Should see 4 colored lines (ASX, S&P 500, NASDAQ, FTSE)
4. Check logs for: "24h window data: 96" (not 26)
```

**Expected Log**:
```
[MARKET CHART] ^GSPC: 24h window data: 96, Market hours data: 78
Date range: 2026-02-10 to 2026-02-11  ← Shows 24-hour range
```

**Before Fix (wrong)**:
```
[MARKET CHART] ^GSPC: Market hours data: 26
Date filter: 2026-02-10  ← Single date (yesterday)
```

---

### Check 2: Reports in Correct Location
```
1. Run: pipelines\RUN_AU_PIPELINE.bat
2. Check: reports\morning_reports\2026-02-11_market_report.html
3. Should NOT be in: pipelines\reports\morning_reports\
```

**Correct Location**:
```
reports\
└── morning_reports\
    └── 2026-02-11_market_report.html  ✅
```

---

### Check 3: Live Updates (5 min test)
```
1. Note current data points in chart
2. Wait 5 minutes (chart auto-refreshes)
3. Chart should show new data
4. Data point count should increase
```

---

## 🔍 Quick Troubleshooting

### Issue: Chart still shows old date
**Solution**: 
- Restart dashboard completely (Ctrl+C, then START.bat)
- Check you replaced the correct file: `core\unified_trading_dashboard.py`
- Look for "24h window data" in logs (not "Total data points")

### Issue: Reports still in wrong location
**Solution**:
- Check you replaced: `pipelines\models\screening\report_generator.py`
- Run pipeline again (takes effect on next run)
- Look for "base_path" with 4 `.parent` calls in file

### Issue: Dashboard won't start
**Solution**:
- Restore from backup
- Run INSTALL_COMPLETE.bat to reinstall
- Check logs at: `logs\screening\`

---

## 📊 What You Should See

### Market Chart (After Fix)
```
Chart Title: "24hr Global Market Performance"
4 Lines visible:
  - Cyan: ASX All Ords (~78 points)
  - Blue: S&P 500 (~78 points)
  - Green: NASDAQ (~78 points)
  - Orange: FTSE 100 (~84 points)

X-axis: Last 24 hours (e.g., Feb 10 10:00 - Feb 11 10:00)
Y-axis: % Change from Previous Close
Updates: Every 5 minutes
```

### Log Output (After Fix)
```
INFO - [MARKET CHART] ^AORD (ASX All Ords): 
  Total data points: 102
  24h window data: 96         ← Should be ~96
  Market hours data: 78       ← Should be ~78
  Date range: 2026-02-10 to 2026-02-11  ← 24h range
  Spans midnight: True
```

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Fresh install | 20-25 minutes |
| Quick update (1 file) | 2 minutes |
| Full reinstall | 5 minutes |
| Verification | 2 minutes |
| **Total (fresh)** | **~30 minutes** |
| **Total (update)** | **~5 minutes** |

---

## 📋 Checklist

**Before Update:**
- [ ] Dashboard running and accessible
- [ ] Note current chart behavior (frozen?)
- [ ] Check where reports currently save

**During Update:**
- [ ] Backed up current installation
- [ ] Extracted new files
- [ ] Restarted dashboard

**After Update:**
- [ ] Chart shows 4 market lines
- [ ] Chart updates every 5 minutes
- [ ] Reports in `reports\morning_reports\`
- [ ] Logs show "24h window data: 96"
- [ ] Logs show "Date range: X to Y"

---

## 🎯 Bottom Line

**Two Critical Fixes in One Package:**
1. Market chart now shows live 24-hour data (was frozen)
2. Reports now save to correct location (was hidden)

**For Fresh Install**: Just run INSTALL_COMPLETE.bat - fixes included!

**For Updates**: Replace 2 files, restart dashboard, done!

**Time to Fix**: 2-5 minutes  
**Status**: Production Ready  
**Risk**: Low (2 files changed)

---

## 📞 Need Help?

**Documentation:**
- Full details: `HOTFIX_DUAL_FIX_v1.3.15.116.md`
- Version history: `VERSION.md`

**Common Issues:**
- Chart not updating? → Restart dashboard
- Reports wrong location? → Run pipeline again
- Still issues? → Check logs at `logs\screening\`

---

✅ **Ready to install!**

*v1.3.15.116 | 2026-02-11 | Production Ready*
