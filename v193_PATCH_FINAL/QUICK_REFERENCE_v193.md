# v193 Quick Reference Guide

**World Event Risk Monitor + UK/US HTML Reports**

---

## Installation (30 seconds)

```bash
cd C:\Users\YOUR_USERNAME\AATelS\unified_trading_system_v188_COMPLETE_PATCHED
INSTALL_v193.bat
```

OR manual:

```bash
git pull origin market-timing-critical-fix
python test_world_event_monitor.py
```

---

## What's New

✅ **World Event Risk Monitor** - Detects geopolitical crises (war, strikes, sanctions)  
✅ **UK HTML Reports** - Morning reports with FTSE/VFTSE/GBP sentiment  
✅ **US HTML Reports** - Morning reports with S&P/VIX sentiment  
✅ **Trading Gates** - Auto position size reduction during crises

---

## Daily Operations

### 1. Run Overnight Pipelines
```bash
# AU Market
python scripts/run_au_pipeline_v1.3.13.py

# UK Market
python scripts/run_uk_full_pipeline.py --full-scan

# US Market
python scripts/run_us_full_pipeline.py --full-scan
```

### 2. Check Logs for World Risk
```
================================================================================
PHASE 1.4: WORLD EVENT RISK MONITORING
================================================================================
[OK] World Risk Score: 85.0/100
[OK] Risk Level: CRITICAL
  [🚨] CRITICAL WORLD RISK - DEFENSIVE STANCE REQUIRED
```

### 3. View HTML Reports
```bash
start reports\screening\au_morning_report_20260301.html
start reports\screening\uk_morning_report_20260301.html
start reports\screening\us_morning_report_20260301.html
```

---

## World Risk Levels

| Score | Level | Action | Position Size |
|-------|-------|--------|---------------|
| **85+** | CRITICAL | Block new longs (weak market) | 0% or 50% |
| **75-84** | ELEVATED | Reduce positions | 60% |
| **65-74** | HIGH | Apply caution | 75% |
| **35-64** | MODERATE | Normal operations | 100% |
| **0-34** | LOW | Slight boost (good market) | 105% |

---

## Crisis Detection Keywords

### Major War (-0.85)
`war declared`, `invasion`, `military offensive`, `armed conflict`

### Military Strikes (-0.70)
`airstrike`, `missile attack`, `bombing campaign`, `drone strike`

### Geopolitical Tensions (-0.55)
`escalating tensions`, `diplomatic crisis`, `trade war`, `standoff`

### Economic Sanctions (-0.45)
`sanctions imposed`, `economic penalties`, `embargo`, `asset freeze`

---

## Verification Checklist

- [ ] Test suite passes: `python test_world_event_monitor.py`
- [ ] World risk appears in logs: Search for "PHASE 1.4"
- [ ] HTML reports generated: `dir reports\screening\*.html`
- [ ] World Risk card visible in HTML (Market Overview section)
- [ ] Position sizing adjusts during crises (check paper trading logs)

---

## Troubleshooting

### Issue: World risk always 50/100
**Reason**: No crisis keywords detected (calm market conditions)  
**Action**: Normal behavior when geopolitical environment is stable

### Issue: UK/US HTML reports missing
**Check**: Do JSON reports exist?
```bash
dir reports\screening\uk_morning_report.json
dir reports\screening\us_morning_report.json
```
If JSON exists but HTML doesn't, check pipeline logs for errors.

### Issue: Module import error
**Fix**: Verify world_event_monitor.py exists:
```bash
python -c "from pipelines.models.screening.world_event_monitor import WorldEventMonitor; print('OK')"
```

---

## Rollback (if needed)

### Option 1: Git reset
```bash
cd C:\Users\YOUR_USERNAME\AATelS\unified_trading_system_v188_COMPLETE_PATCHED
git reset --hard HEAD~6
```

### Option 2: Restore from backup
```bash
cd backup_pre_v193
copy /Y *.bak ..\pipelines\models\screening\
copy /Y run_*.bak ..\scripts\
copy /Y sentiment_integration.py.bak ..\core\
```

---

## Quick Test

```bash
python test_world_event_monitor.py
```

**Expected**:
```
✅ ALL TESTS PASSED
Monitor Status: OPERATIONAL
Keyword Detection: 20 crisis patterns
```

---

## File Locations

| File | Path |
|------|------|
| World Event Monitor | `pipelines/models/screening/world_event_monitor.py` |
| Test Suite | `test_world_event_monitor.py` |
| AU Pipeline | `pipelines/models/screening/overnight_pipeline.py` |
| UK Pipeline | `pipelines/models/screening/uk_overnight_pipeline.py` |
| US Pipeline | `pipelines/models/screening/us_overnight_pipeline.py` |
| HTML Generator | `pipelines/models/screening/report_generator.py` |
| Trading Gates | `core/sentiment_integration.py` |
| Backups | `backup_pre_v193/` |

---

## Example Scenarios

### Scenario 1: Iran-US Conflict
```
Input: "US launches airstrikes on Iran military bases"
World Risk: 85/100 (CRITICAL)
Market Sentiment: 58/100
Decision: BLOCK new longs
Position Size: 0% (defensive)
```

### Scenario 2: Trade War Escalation
```
Input: "Trump announces 60% tariffs on Chinese imports"
World Risk: 70/100 (HIGH)
Market Sentiment: 62/100
Decision: REDUCE
Position Size: 60%
```

### Scenario 3: Calm Markets
```
Input: "GDP grows 2.5%, unemployment steady"
World Risk: 40/100 (MODERATE)
Market Sentiment: 68/100
Decision: ALLOW
Position Size: 100%
```

---

## Support

**Documentation**:
- `INSTALL_v193.md` - Full installation guide
- `v193_COMPLETE_SUMMARY.md` - Technical architecture
- `QUICK_REFERENCE_v193.md` - This guide

**Commands**:
```bash
# Test world event monitor
python test_world_event_monitor.py

# Check module import
python -c "from pipelines.models.screening.world_event_monitor import WorldEventMonitor; print('OK')"

# View installation report
type v193_installation_report.txt
```

---

**Version**: v193 (March 1, 2026)  
**Status**: Production Ready ✅
