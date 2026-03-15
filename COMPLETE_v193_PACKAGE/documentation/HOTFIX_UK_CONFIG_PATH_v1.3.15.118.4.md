# HOTFIX v1.3.15.118.4 - UK Sectors Config Path Fix

## Date: 2026-02-11

### 🔧 Issue Fixed: UK Pipeline Can't Find Sectors Config

**Problem**:
```
Error loading config: [Errno 2] No such file or directory: 
'C:\...\config\uk_sectors.json'

[X] Error scanning selection_criteria: 'stocks'
[X] UK PIPELINE FAILED: No valid UK stocks found during scanning
```

**Root Cause**:
UK pipeline was looking for config in wrong location:

```python
# WRONG PATH:
uk_config_path = BASE_PATH / 'config' / 'uk_sectors.json'
# Looks in: C:\...\unified_trading_dashboard\config\uk_sectors.json (DOESN'T EXIST)

# ACTUAL LOCATION:
# File is at: C:\...\unified_trading_dashboard\pipelines\config\uk_sectors.json
```

**Why This Happened**:
- UK sectors config stored in `pipelines/config/uk_sectors.json`
- UK pipeline tried to load from `config/uk_sectors.json` (missing `pipelines/` prefix)
- File not found → Scanner failed to load → No stocks to scan

---

## Fix Applied

### File Changed:
**pipelines/models/screening/uk_overnight_pipeline.py**

```python
# Line 104 (BEFORE):
uk_config_path = BASE_PATH / 'config' / 'uk_sectors.json'  # ❌ Wrong path

# Line 105 (AFTER):
# FIX v1.3.15.118.4: Config file is in pipelines/config/
uk_config_path = BASE_PATH / 'pipelines' / 'config' / 'uk_sectors.json'  # ✅ Correct path
```

---

## Impact

### Before (WRONG):
```
BASE_PATH = C:\...\unified_trading_dashboard\
Config Path = BASE_PATH / 'config' / 'uk_sectors.json'
            = C:\...\unified_trading_dashboard\config\uk_sectors.json  ← DOESN'T EXIST
            
Result: FileNotFoundError → No stocks loaded → Pipeline fails
```

### After (CORRECT):
```
BASE_PATH = C:\...\unified_trading_dashboard\
Config Path = BASE_PATH / 'pipelines' / 'config' / 'uk_sectors.json'
            = C:\...\unified_trading_dashboard\pipelines\config\uk_sectors.json  ← EXISTS!

Result: Config loads successfully → 240 UK stocks loaded → Pipeline runs
```

---

## Verification Steps

### Step 1: Verify Config File Exists
```batch
dir "pipelines\config\uk_sectors.json"
```
**Expected**: File found (should show ~240 stocks in 8 sectors)

### Step 2: Run UK Pipeline
```batch
START.bat → Option 7 (UK Pipeline)
```

### Step 3: Check Logs
**Expected**:
```
[OK] UK Stock Scanning Complete:
  Total Valid Stocks: 240
  
[1/8] Scanning Financials... (30 stocks)
[2/8] Scanning Energy... (30 stocks)
...
```

**NOT Expected** (old error):
```
❌ Error loading config: [Errno 2] No such file or directory
❌ No valid UK stocks found during scanning
```

### Step 4: Check Output
**Expected**:
- HTML report: `reports/morning_reports/2026-02-11_market_report.html`
- JSON report: `reports/screening/uk_morning_report.json`
- Both should contain ~240 UK stocks analyzed

---

## Technical Details

### UK Sectors Config Structure:
```json
{
  "metadata": {
    "total_stocks": 240,
    "sectors_count": 8,
    "stocks_per_sector": 30
  },
  "sectors": {
    "Financials": {
      "stocks": ["HSBA.L", "LLOY.L", "BARC.L", ...]
    },
    "Energy": {
      "stocks": ["SHEL.L", "BP.L", "SSE.L", ...]
    },
    ...
  }
}
```

### Config Path Resolution:
```python
# BASE_PATH (from v1.3.15.118.2 fix):
BASE_PATH = Path(__file__).parent.parent.parent.parent  # 4 levels up
# __file__ = pipelines/models/screening/uk_overnight_pipeline.py
# BASE_PATH = project_root/

# Config path:
uk_config_path = BASE_PATH / 'pipelines' / 'config' / 'uk_sectors.json'
# = project_root/pipelines/config/uk_sectors.json ✅
```

---

## Status

**Version**: v1.3.15.118.4  
**Status**: ✅ **FIXED**  
**Files Modified**: 1 (uk_overnight_pipeline.py line 105)  
**Impact**: Critical (UK pipeline couldn't run)  
**Breaking Changes**: None  

---

## Related Fixes

This fix builds on previous path fixes:
- **v1.3.15.118.2**: Fixed `BASE_PATH` (3 levels → 4 levels)
- **v1.3.15.118.4**: Fixed UK config path (config/ → pipelines/config/)

**Together**: Both fixes ensure correct path resolution throughout the system.

---

## For Other Pipelines

**AU Pipeline**: ✅ Uses `pipelines/config/asx_sectors.json` (correct)  
**US Pipeline**: ✅ Uses `USStockScanner` (no config file needed)  
**UK Pipeline**: ✅ Now uses `pipelines/config/uk_sectors.json` (fixed)  

---

**Status**: ✅ **RESOLVED** - v1.3.15.118.4

UK pipeline can now load sectors config and scan 240 UK stocks!
