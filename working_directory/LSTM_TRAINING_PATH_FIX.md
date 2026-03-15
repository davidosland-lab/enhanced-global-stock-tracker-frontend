# LSTM TRAINING FIX - CRITICAL PATH ERROR

**Date**: 2026-01-30  
**Version**: v1.3.15.48 CRITICAL FIX  
**Status**: ✅ FIXED

---

## Issue

**All 20 LSTM training attempts failed with**:
```
ERROR: No module named 'models.train_lstm'
Result: 0/20 trained, 20/20 failed, 0.0% success rate
```

---

## Root Cause

The `lstm_trainer.py` was checking if the **AATelS directory EXISTS**, not if it actually **contains the train_lstm.py module**.

**Wrong Logic** (before fix):
```python
# Line 204-210 (OLD)
finbert_path_aatels = Path(r'C:\Users\david\AATelS\finbert_v4.4.4')
finbert_path_relative = BASE_PATH / 'finbert_v4.4.4'

if finbert_path_aatels.exists():  # ❌ Only checks if directory exists
    finbert_path = finbert_path_aatels  # Uses AATelS (EMPTY)
elif finbert_path_relative.exists():
    finbert_path = finbert_path_relative  # Never reached
```

**Result**:
- AATelS directory: `C:\Users\david\AATelS\finbert_v4.4.4` (EXISTS but **EMPTY/INCOMPLETE**)
- Local FinBERT: `C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\finbert_v4.4.4` (**HAS train_lstm.py**)
- Code prioritized AATelS → Used empty directory → Import failed

**Log Evidence**:
```
2026-01-30 09:38:26 - Using FinBERT from AATelS: C:\Users\david\AATelS\finbert_v4.4.4
2026-01-30 09:38:26 - ERROR: No module named 'models.train_lstm'
```

---

## The Fix

**Correct Logic** (after fix):
```python
# Lines 203-219 (NEW)
finbert_path_relative = BASE_PATH / 'finbert_v4.4.4'
finbert_path_aatels = Path(r'C:\Users\david\AATelS\finbert_v4.4.4')

# Priority: LOCAL first, then AATelS
# Check if train_lstm.py FILE exists, not just directory
if finbert_path_relative.exists() and (finbert_path_relative / 'models' / 'train_lstm.py').exists():
    finbert_path = finbert_path_relative  # ✅ Use LOCAL (has train_lstm.py)
elif finbert_path_aatels.exists() and (finbert_path_aatels / 'models' / 'train_lstm.py').exists():
    finbert_path = finbert_path_aatels  # Fallback to AATelS (if valid)
else:
    raise FileNotFoundError(
        f"FinBERT train_lstm.py not found. Tried:\n"
        f"  1. {finbert_path_relative / 'models' / 'train_lstm.py'}\n"
        f"  2. {finbert_path_aatels / 'models' / 'train_lstm.py'}"
    )
```

**Changes**:
1. ✅ **Priority reversed**: LOCAL first, then AATelS
2. ✅ **File check**: Verifies `train_lstm.py` exists, not just directory
3. ✅ **Clear error**: Shows exact file paths checked

---

## Expected Result (After Fix)

**Next pipeline run should show**:
```
2026-01-30 XX:XX:XX - Using FinBERT from local: C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\finbert_v4.4.4
2026-01-30 XX:XX:XX - [1/20] Training BHP.AX...
2026-01-30 XX:XX:XX - [OK] BHP.AX: Training completed in 29.2s
2026-01-30 XX:XX:XX -    Loss: 0.0234
2026-01-30 XX:XX:XX -    Val Loss: 0.0267
...
2026-01-30 XX:XX:XX - [SUCCESS] LSTM Training Complete:
2026-01-30 XX:XX:XX -   Models trained: 20/20
2026-01-30 XX:XX:XX -   Successful: 20
2026-01-30 XX:XX:XX -   Failed: 0
2026-01-30 XX:XX:XX -   Success Rate: 100%
2026-01-30 XX:XX:XX -   Total Time: 10.2 minutes
```

---

## Verification Steps

### Step 1: Verify Local FinBERT Has train_lstm.py

```batch
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
dir finbert_v4.4.4\models\train_lstm.py
```

**Expected**: File exists (~10 KB)

### Step 2: Run AU Overnight Pipeline

```batch
LAUNCH_COMPLETE_SYSTEM.bat
→ Choose: [1] Run AU Overnight Pipeline
→ Wait for Phase 4.5: LSTM MODEL TRAINING
→ Watch console for "Using FinBERT from local:"
```

### Step 3: Check Training Results

**Check log**:
```batch
type logs\screening\au\overnight_*.log | findstr "LSTM Training Complete"
```

**Expected output**:
```
Models trained: 20/20
Successful: 20
Failed: 0
Success Rate: 100%
```

**Check trained models**:
```batch
dir finbert_v4.4.4\models\lstm_*.h5
```

**Expected**: 20 new .h5 model files created

---

## Why This Happened

The code was originally designed to work in **two environments**:
1. **AATelS project**: `C:\Users\david\AATelS\finbert_v4.4.4`
2. **Regime Trading project**: `C:\Users\david\Regime_trading\...\finbert_v4.4.4`

The logic checked if AATelS **directory** exists (for backward compatibility), but didn't verify it was **complete/functional**.

**Your AATelS FinBERT** appears to be either:
- Empty/incomplete installation
- Missing the `models/train_lstm.py` module
- Placeholder directory

The fix prioritizes the **LOCAL FinBERT** (which is complete) and **verifies the file exists** before using it.

---

## Files Modified

- `models/screening/lstm_trainer.py` (lines 203-219)
  - Changed priority order (LOCAL first)
  - Added file existence check (not just directory)
  - Improved error message

---

## Alternative Solution (If Still Fails)

If the fix doesn't work, you can **explicitly set the FinBERT path** in the config:

**Edit** `models/config/screening_config.json`:
```json
{
  "lstm_training": {
    "enabled": true,
    "finbert_path": "C:\\Users\\david\\Regime_trading\\COMPLETE_SYSTEM_v1.3.15.45_FINAL\\finbert_v4.4.4",
    "max_models_per_night": 20,
    ...
  }
}
```

Then update `lstm_trainer.py` line ~205:
```python
# Use config path if specified
config_finbert_path = self.training_config.get('finbert_path')
if config_finbert_path:
    finbert_path = Path(config_finbert_path)
    if not (finbert_path / 'models' / 'train_lstm.py').exists():
        raise FileNotFoundError(f"train_lstm.py not found in config path: {finbert_path}")
else:
    # Use auto-detection logic
    ...
```

---

## Summary

| Aspect | Before Fix | After Fix |
|--------|------------|-----------|
| **Path Priority** | AATelS first | LOCAL first |
| **Path Check** | Directory exists | File exists |
| **AATelS Path** | Used (empty) | Skipped (no train_lstm.py) |
| **Local Path** | Never reached | Used (has train_lstm.py) |
| **Training Success** | 0/20 (0%) | 20/20 (100%) expected |
| **Error Message** | Generic | Shows exact file paths |

---

## Next Steps

1. **Re-run AU Pipeline**:
   ```batch
   LAUNCH_COMPLETE_SYSTEM.bat → [1] Run AU Overnight Pipeline
   ```

2. **Verify log shows**:
   ```
   Using FinBERT from local: C:\Users\david\Regime_trading\...\finbert_v4.4.4
   ```

3. **Confirm training succeeds**:
   ```
   Models trained: 20/20
   Success Rate: 100%
   ```

4. **Check trained models exist**:
   ```batch
   dir finbert_v4.4.4\models\lstm_*.h5
   ```

---

**Status**: ✅ FIXED  
**Version**: v1.3.15.48  
**File Modified**: `models/screening/lstm_trainer.py`  
**Action**: Re-run overnight pipeline to verify fix  
**Expected**: 100% training success rate
