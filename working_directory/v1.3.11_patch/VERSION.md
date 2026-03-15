# Version Information

**Patch Name:** v1.3.11 Calibration Fix  
**Patch Version:** 1.3.11  
**Release Date:** January 2, 2026  
**Patch Type:** Critical Fix  

---

## Compatibility

**Compatible with:**
- v1.3.10 ✅ (recommended)
- v1.3.9 ✅
- v1.3.8 ✅

**Not compatible with:**
- v1.3.7 and earlier ❌

---

## What's Fixed

### Issue:
Market performance charts calculated percentage change from market open instead of previous day's close.

### Solution:
Changed reference price to previous trading day's last close.

### Result:
Charts now show accurate daily percentage changes matching official market figures from Bloomberg, Yahoo Finance, and exchange websites.

---

## Files Modified

### Updated Files (1):
```
phase3_intraday_deployment/unified_trading_dashboard.py
- Lines changed: 374-413 (40 lines)
- Changes: Percentage calculation logic
- Added: Previous day close reference
- Updated: Hover tooltip text
```

### Documentation Added (3):
```
README.md
PATCH_INSTALLATION_GUIDE.md
V1.3.11_CALIBRATION_FIX.md
```

### Install Scripts (2):
```
INSTALL_PATCH.bat (Windows)
install_patch.sh (Linux/Mac)
```

---

## Technical Details

### Code Change Summary:
```python
# Before (v1.3.10)
first_price = market_hours_data['Close'].iloc[0]  # Market open
pct_change = ((close - first_price) / first_price) * 100

# After (v1.3.11)
previous_day_data = hist[hist.index.date < latest_date]
previous_close = previous_day_data['Close'].iloc[-1]  # Previous close
pct_change = ((close - previous_close) / previous_close) * 100
```

### Hover Tooltip Update:
```
Before: "Change: X.XX%"
After:  "Change from Prev Close: X.XX%"
```

---

## Package Contents

```
v1.3.11_calibration_patch.zip (35 KB)
└── v1.3.11_patch/
    ├── README.md
    ├── VERSION.md (this file)
    ├── PATCH_INSTALLATION_GUIDE.md
    ├── V1.3.11_CALIBRATION_FIX.md
    ├── INSTALL_PATCH.bat
    ├── install_patch.sh
    └── phase3_intraday_deployment/
        └── unified_trading_dashboard.py
```

---

## Installation

### Quick Install (Windows):
```batch
1. Run INSTALL_PATCH.bat
2. Follow prompts
3. Restart dashboard
```

### Quick Install (Linux/Mac):
```bash
chmod +x install_patch.sh
./install_patch.sh
```

### Manual Install:
See **PATCH_INSTALLATION_GUIDE.md**

---

## Verification

### After installation, verify:
1. ✅ Dashboard starts without errors
2. ✅ Hover tooltip shows "Change from Prev Close"
3. ✅ Daily % matches official figures
4. ✅ Chart updates every 5 seconds

### Compare with official sources:
- Yahoo Finance: https://finance.yahoo.com
- Bloomberg: https://www.bloomberg.com/markets
- Exchange websites

---

## Support

### Documentation:
- PATCH_INSTALLATION_GUIDE.md (detailed instructions)
- V1.3.11_CALIBRATION_FIX.md (technical details)

### Rollback:
If needed, backup files are automatically created as:
```
unified_trading_dashboard.py.v1.3.10.backup
```

---

## Checksums

### File Integrity:
```
unified_trading_dashboard.py
- Size: ~37 KB
- Modified: January 2, 2026
- Lines: ~1,400
```

---

## Release Notes

### v1.3.11 (January 2, 2026)
**Type:** Critical Calibration Fix  
**Priority:** High  

**Fixed:**
- ✅ Market performance percentage calculations
- ✅ Reference changed from market open to previous close
- ✅ Charts now match official market figures

**Verified:**
- ✅ NASDAQ daily % accurate
- ✅ S&P 500 daily % accurate
- ✅ FTSE 100 daily % accurate
- ✅ ASX All Ords daily % accurate

**User Feedback:**
> "Apart from this calibration issue the module worked well overnight."

**Status:** PRODUCTION READY ✅

---

**Build Date:** January 2, 2026  
**Build Number:** v1.3.11-patch-001  
**Git Commit:** 7bda922  
**Patch Size:** 35 KB compressed
