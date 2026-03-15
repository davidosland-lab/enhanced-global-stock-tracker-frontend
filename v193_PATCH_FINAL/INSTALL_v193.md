# v193 Installation Guide: World Event Risk Monitor + HTML Reports Fix

**Version**: v193 (World Event Risk + UK/US HTML Reports)  
**Date**: March 1, 2026  
**Prerequisites**: v188_COMPLETE_PATCHED or v190_COMPLETE

---

## What's New in v193

### 1. **World Event Risk Monitor** 🌍
- **Geopolitical crisis detection** with keyword-based analysis
- **Severity scoring**: Major war (-0.85), Military strikes (-0.70), Geopolitical tensions (-0.55), Economic sanctions (-0.45)
- **Risk indices**: Fear, Anger, Negative sentiment (0-1 scale)
- **Risk score**: 0-100 (50=neutral, 85+=critical, 35-=low)
- **Zero cost**: No API calls, keyword-based fallback only

### 2. **Trading Position Gates** 🛡️
- **Critical risk (85+)** + weak market → BLOCK new longs
- **Elevated risk (75+)** → 60% position size
- **High risk (65+)** → 75% position size  
- **Low risk (35-)** → 5% position boost

### 3. **HTML Report Fix** 📊
- **UK Pipeline**: Now generates HTML reports with FTSE/GBP/VFTSE sentiment
- **US Pipeline**: Now generates HTML reports with S&P/VIX sentiment
- **AU Pipeline**: Already working with SPI sentiment
- **World Risk Card**: Displayed prominently in all market overviews

### 4. **Market-Specific Sentiment** 📈
- **AU**: SPI200 futures (overnight ASX proxy)
- **UK**: FTSE 100 + VFTSE (UK VIX) + GBP/USD
- **US**: S&P 500 + VIX + Nasdaq

---

## Installation (Option A: In-Place Update - RECOMMENDED)

**Time**: ~30 seconds  
**Risk**: Very low (no reinstall needed)

```bash
cd C:\Users\YOUR_USERNAME\AATelS\unified_trading_system_v188_COMPLETE_PATCHED
git pull origin market-timing-critical-fix
python test_world_event_monitor.py
```

**Expected Output**:
```
================================================================================
WORLD EVENT RISK MONITOR TEST SUITE
================================================================================
✅ World Risk Score: 50.0/100
✅ Risk Level: MODERATE
✅ Fear Index: 0.00
✅ ALL TESTS PASSED
Monitor Status: OPERATIONAL
```

---

## Installation (Option B: Fresh Install)

1. **Backup current system**:
   ```bash
   cd C:\Users\YOUR_USERNAME\AATelS
   copy /Y unified_trading_system_v188_COMPLETE_PATCHED unified_trading_system_v188_COMPLETE_PATCHED_BACKUP
   ```

2. **Extract v193 package** to `C:\Users\YOUR_USERNAME\AATelS\unified_trading_system_v193_COMPLETE`

3. **Run test**:
   ```bash
   cd C:\Users\YOUR_USERNAME\AATelS\unified_trading_system_v193_COMPLETE
   python test_world_event_monitor.py
   ```

---

## Verification

### Check World Event Risk Integration

Run any overnight pipeline and check logs for:
```
================================================================================
PHASE 1.4: WORLD EVENT RISK MONITORING
================================================================================
[OK] World Event Risk Analysis Complete:
  World Risk Score: XX.X/100
  Risk Level: MODERATE/HIGH/CRITICAL
```

### Check HTML Reports

After running pipelines, verify HTML files exist:
```bash
dir reports\screening\*.html
```

You should see:
- `au_morning_report_YYYYMMDD.html`
- `uk_morning_report_YYYYMMDD.html` ← **NEW**
- `us_morning_report_YYYYMMDD.html` ← **NEW**

Open in browser and verify "World Event Risk" card appears in Market Overview section.

### Check Trading Gates

Run paper trading and look for world risk adjustments:
```
[SENTIMENT] World Risk: 75.0/100 (ELEVATED)
[TRADING] Position size reduced to 60% (world risk 75/100)
```

---

## Files Changed

### **Modified Files** (7):
1. `pipelines/models/screening/overnight_pipeline.py` (AU world risk integration)
2. `pipelines/models/screening/uk_overnight_pipeline.py` (UK world risk integration)
3. `pipelines/models/screening/us_overnight_pipeline.py` (US world risk integration)
4. `pipelines/models/screening/report_generator.py` (world risk HTML card)
5. `core/sentiment_integration.py` (world risk trading gates)
6. `scripts/run_uk_full_pipeline.py` (fix HTML generation)
7. `scripts/run_us_full_pipeline.py` (fix HTML generation)

### **New Files** (2):
1. `pipelines/models/screening/world_event_monitor.py` (13.5 KB - core module)
2. `test_world_event_monitor.py` (2 KB - validation)

**Total changes**: ~800 lines added, 9 files touched

---

## Example Impact

### Before v193:
- **Iran-US conflict** headline → Sentiment: 0.00 (NEUTRAL)
- **Position**: $50,000 full exposure
- **5% market drop** → Loss: -$2,500

### After v193:
- **Iran-US conflict** headline → World Risk: 85/100 (CRITICAL)
- **Sentiment adjusted**: 65 → 42 (BEARISH)
- **Position**: $25,000 (50% size reduction)
- **5% market drop** → Loss: -$1,250
- **💰 Savings**: $1,250 per crisis event

---

## Troubleshooting

### Issue: "WorldEventMonitor not found"
**Solution**: Module is optional. Pipeline will log:
```
[INFO] World Event Risk Monitor disabled (world_event_monitor module not found)
```
This is safe to ignore. The system will continue without world risk monitoring.

### Issue: UK/US HTML reports still missing
**Solution**: Check that pipelines are generating JSON reports first:
```bash
dir reports\screening\uk_morning_report.json
dir reports\screening\us_morning_report.json
```
If JSON exists but HTML doesn't, check logs for report generator errors.

### Issue: World risk always shows 50/100 (neutral)
**Solution**: This is expected when no crisis keywords are detected in recent news. The system defaults to neutral risk when conditions are calm.

---

## Rollback

If you encounter issues, rollback is simple:

```bash
cd C:\Users\YOUR_USERNAME\AATelS\unified_trading_system_v188_COMPLETE_PATCHED
git reset --hard HEAD~1
```

Or restore from backup:
```bash
cd C:\Users\YOUR_USERNAME\AATelS
rmdir /S unified_trading_system_v188_COMPLETE_PATCHED
ren unified_trading_system_v188_COMPLETE_PATCHED_BACKUP unified_trading_system_v188_COMPLETE_PATCHED
```

---

## Support & Documentation

- **Quick Reference**: See `QUICK_REFERENCE_v193.md` for daily operations
- **Technical Details**: See `v193_IMPLEMENTATION_PLAN.md` for architecture
- **Test Suite**: Run `python test_world_event_monitor.py` anytime

---

## Next Steps

1. ✅ Install v193 patch (this guide)
2. ✅ Run test suite to verify
3. ✅ Run tonight's AU/UK/US pipelines
4. ✅ Check HTML reports generated
5. ✅ Verify world risk appears in morning reports
6. ✅ Monitor position sizing during next geopolitical event

---

**Estimated Installation Time**: 30 seconds (git pull) to 5 minutes (fresh install)  
**Recommended**: In-place update via git pull
