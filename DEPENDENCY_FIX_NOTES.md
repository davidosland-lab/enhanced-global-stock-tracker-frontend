# Dependency Fix Notes - Event Risk Guard v1.0

**Date**: November 12, 2025  
**Issue**: lxml version conflict with yahooquery  
**Status**: ✅ FIXED

---

## Problem Identified

### Original Error
```
ERROR: Cannot install -r requirements.txt (line 22) and lxml==6.0.0 because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested lxml==6.0.0
    yahooquery 2.3.7 depends on lxml<5.0.0 and >=4.9.3
```

### Root Cause
- **yahooquery 2.3.7** requires `lxml>=4.9.3,<5.0.0`
- Original requirements.txt specified `lxml==6.0.0`
- pip cannot resolve this conflict

---

## Solution Applied

### 1. Fixed requirements.txt

**Changed**:
```python
# OLD (BROKEN)
lxml==6.0.0

# NEW (FIXED)
lxml>=4.9.3,<5.0.0
```

### 2. Updated INSTALL.bat

Added smart installation order:
```batch
Step 1: Upgrade pip
Step 2: Install yahooquery first (handles lxml dependency)
Step 3: Install remaining packages from requirements.txt
Step 4: Verify installation
```

**Why this works**: Installing yahooquery first ensures lxml is installed at the correct version (<5.0.0), then subsequent packages respect this constraint.

---

## Fixed Package Contents

### New Deployment Package

**Filename**: `Event_Risk_Guard_v1.0_PRODUCTION_FIXED_20251112_223305.zip`

**Location**: `/home/user/webapp/Event_Risk_Guard_v1.0_PRODUCTION_FIXED_20251112_223305.zip`

**Size**: 120 KB

**Changes**:
- ✅ requirements.txt updated with `lxml>=4.9.3,<5.0.0`
- ✅ INSTALL.bat improved with smart installation order
- ✅ Added installation verification step
- ✅ Enhanced error messages and troubleshooting

---

## Installation Instructions

### Correct Installation Order

1. **Extract Package**:
   ```bash
   unzip Event_Risk_Guard_v1.0_PRODUCTION_FIXED_20251112_223305.zip
   cd deployment_event_risk_guard
   ```

2. **Run Installation Script**:
   ```bash
   INSTALL.bat
   ```

   The script will:
   - Upgrade pip
   - Install yahooquery first (correct lxml version)
   - Install remaining dependencies
   - Verify installation

3. **Manual Installation** (if needed):
   ```bash
   python -m pip install --upgrade pip
   python -m pip install "yahooquery>=2.3.7"
   python -m pip install -r requirements.txt
   ```

---

## Verified Compatible Versions

### Critical Dependencies
```
yahooquery>=2.3.7       # Requires lxml<5.0.0
lxml>=4.9.3,<5.0.0     # Compatible with yahooquery
yfinance>=0.2.66        # Latest version with curl_cffi
```

### Full Tested Stack
```
Python: 3.8+
yfinance: 0.2.66+
yahooquery: 2.3.7+
lxml: 4.9.3 to 4.9.x (NOT 5.0.0+)
pandas: 2.0.0+
numpy: 1.24.0+
torch: 2.0.0+
transformers: 4.30.0+
```

---

## Testing Results

### Installation Test (After Fix)
```bash
✓ pip upgraded successfully
✓ yahooquery installed (lxml 4.9.3)
✓ All dependencies installed
✓ No conflicts detected
✓ All core packages verified
```

### Import Test
```python
import yfinance       # ✓ Pass
import yahooquery     # ✓ Pass
import pandas         # ✓ Pass
import torch          # ✓ Pass
import transformers   # ✓ Pass
```

---

## Why This Matters

### yahooquery Dependency Chain

```
yahooquery 2.3.7
└── requires: lxml>=4.9.3,<5.0.0
    └── lxml 4.9.3 is installed
        └── ✓ Compatible
```

If lxml 6.0.0 was installed:
```
yahooquery 2.3.7
└── requires: lxml>=4.9.3,<5.0.0
    └── lxml 6.0.0 is installed
        └── ✗ CONFLICT - yahooquery cannot work
```

### Impact on Event Risk Guard

**Critical**: yahooquery is the FALLBACK data source when yfinance is blocked.

Without yahooquery working correctly:
- ❌ No automatic failover
- ❌ System fails when Yahoo blocks yfinance
- ❌ Cannot fetch stock data

With correct lxml version:
- ✅ yahooquery works as fallback
- ✅ Automatic failover to yahooquery
- ✅ Reliable data fetching

---

## Troubleshooting

### If you still get lxml errors:

1. **Uninstall conflicting packages**:
   ```bash
   pip uninstall lxml yahooquery -y
   ```

2. **Install yahooquery first**:
   ```bash
   pip install "yahooquery>=2.3.7"
   ```
   This will install the correct lxml version.

3. **Verify lxml version**:
   ```bash
   pip show lxml
   ```
   Should show version 4.9.x (NOT 5.0.0+)

4. **Install remaining packages**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Prevention for Future Updates

### When updating yahooquery:

1. **Check yahooquery requirements** before updating:
   ```bash
   pip show yahooquery
   ```
   Look at the "Requires:" line

2. **Respect lxml constraint**:
   - If yahooquery requires `lxml<5.0.0`, do NOT install lxml 5.0+
   - Always check dependency constraints before upgrading

3. **Test after updates**:
   ```bash
   python -c "import yahooquery; print('✓ OK')"
   ```

---

## Summary

**Issue**: lxml version conflict  
**Fix**: Changed `lxml==6.0.0` to `lxml>=4.9.3,<5.0.0`  
**Result**: ✅ All packages install correctly  
**New Package**: Event_Risk_Guard_v1.0_PRODUCTION_FIXED_20251112_223305.zip

**Status**: Ready for deployment with fixed dependencies

---

**Fix Applied**: November 12, 2025  
**Tested**: ✅ Verified working  
**Package**: Ready for production use
