# LSTM Training Fix - Windows 11 Instructions

## Quick Start (Choose One Method)

### ⚡ Method 1: Automatic Fix (FASTEST - 30 seconds)

1. Double-click: **`APPLY_LSTM_FIX.bat`**
2. Wait for completion message
3. Run **`TRAIN_LSTM_OVERNIGHT.bat`** to test

✅ **Done!** The script automatically backs up and fixes the file.

---

### 📝 Method 2: Manual Fix (EASIEST - 2 minutes)

1. **Right-click** on **`TRAIN_LSTM_OVERNIGHT.bat`**
2. Select **"Edit"** (opens Notepad)
3. Press **`Ctrl+H`** (Find and Replace)
4. **Find**: `tensorflow.__version__`
5. You'll see line 57 with a long Python command
6. **Replace the entire line** with:
   ```batch
   python -c "import tensorflow" 2>nul
   ```
7. Press **`Ctrl+S`** to save
8. Close Notepad
9. Run **`TRAIN_LSTM_OVERNIGHT.bat`** to test

✅ **Done!**

---

## What's the Problem?

When you run `TRAIN_LSTM_OVERNIGHT.bat`, you see:

```
Checking for TensorFlow installation...
TensorFlow 2.20.0 detected
  Run: pip install -r requirements.txt
  Time: ~15 minutes (downloads ~2.5 GB)
```

**But TensorFlow IS already installed!** The script incorrectly thinks it failed.

---

## What's the Fix?

**Change line 57** from this complex command:

```batch
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} detected')" 2>nul
```

**To this simple command**:

```batch
python -c "import tensorflow" 2>nul
```

---

## Why Does This Fix It?

**Old Code**: Tries to import AND print version (complex)
- Windows batch files don't handle Python f-strings reliably
- Exit code gets confused
- Script thinks import failed even when it succeeded

**New Code**: Just tries to import (simple)
- If import works → exit code 0 → Continue ✅
- If import fails → exit code 1 → Show error ✅

---

## How to Verify the Fix Worked

After applying the fix, run:

```batch
TRAIN_LSTM_OVERNIGHT.bat
```

**You should see**:

```
[OK] Python detected

Checking for TensorFlow installation...
[OK] TensorFlow is installed

========================================================================
  STARTING LSTM TRAINING
========================================================================

Training will begin in 5 seconds...
Press Ctrl+C to cancel
```

✅ **SUCCESS!** The TensorFlow check passed and training is starting.

---

## Files in This Fix Package

| File | Purpose |
|------|---------|
| **`APPLY_LSTM_FIX.bat`** | ⚡ Automatic fix script (just double-click) |
| **`QUICK_FIX_GUIDE.txt`** | 📋 Simple text guide (print-friendly) |
| **`FIX_WINDOWS_LSTM_OVERNIGHT.md`** | 📚 Detailed technical documentation |
| **`README_LSTM_FIX.md`** | 📖 This file (quick reference) |

---

## Troubleshooting

### Issue: "Still showing error after fix"

**Verify TensorFlow is actually installed**:
```batch
python -c "import tensorflow; print(tensorflow.__version__)"
```

Should show: `2.20.0`

If you get an error, install TensorFlow:
```batch
pip install tensorflow>=2.13.0
```

---

### Issue: "Can't save the file"

**Solution**:
1. Close any programs that might have the file open
2. Try running Notepad as Administrator
3. Or save as a new name: `TRAIN_LSTM_OVERNIGHT_FIXED.bat`

---

### Issue: "Fix didn't apply correctly"

**Restore backup and try again**:
```batch
copy TRAIN_LSTM_OVERNIGHT.bat.backup TRAIN_LSTM_OVERNIGHT.bat
```

Then try Method 2 (Manual Fix) with Notepad.

---

## Other LSTM Training Scripts

This fix is specifically for **`TRAIN_LSTM_OVERNIGHT.bat`**.

Other scripts already work correctly:
- ✅ `TRAIN_LSTM_SINGLE.bat` - Already fixed
- ✅ `TRAIN_LSTM_CUSTOM.bat` - No issues
- ✅ `train_lstm_batch.py` - No changes needed

---

## Training Information

After the fix is applied, you can train LSTM models:

### Full Overnight Training
```batch
TRAIN_LSTM_OVERNIGHT.bat
```

**Trains**: 10 ASX stocks (CBA, ANZ, NAB, WBC, MQG, BHP, RIO, CSL, WES, BOQ)  
**Time**: 1.5-2 hours (10-15 min per stock)  
**Output**: `.keras` model files in `models/` directory

### Single Stock Training (Quick Test)
```batch
TRAIN_LSTM_SINGLE.bat CBA.AX
```

**Trains**: Just CBA.AX (Commonwealth Bank)  
**Time**: 10-15 minutes  
**Output**: `models/lstm_CBA.AX_model.keras`

---

## What Happens During Training

```
1. Downloads 2 years of historical stock data (Yahoo Finance)
2. Preprocesses data (normalization, sequence creation)
3. Trains LSTM neural network (50 epochs)
4. Validates model performance
5. Saves trained model (.keras file)
6. Saves metadata (training stats, validation accuracy)
```

**Per Stock**: 10-15 minutes  
**CPU Usage**: High (TensorFlow training)  
**Memory**: ~2-4 GB per stock

---

## After Training Completes

Trained models are used automatically in predictions:

**Prediction Weights**:
- LSTM: 45% (when model exists)
- Trend Analysis: 25%
- Technical Indicators: 15%
- FinBERT Sentiment: 15%

**Without LSTM models**: System uses baseline predictions with adjusted weights.

---

## Next Steps After Fix

1. ✅ Apply the fix (Method 1 or 2)
2. ✅ Test: Run `TRAIN_LSTM_OVERNIGHT.bat`
3. ✅ Verify: Check you see "[OK] TensorFlow is installed"
4. ⏱️ Let training run (1.5-2 hours)
5. 📊 View results: Check `models/` directory for `.keras` files
6. 🚀 Run pipeline: `RUN_OVERNIGHT_PIPELINE.bat` (uses trained models)

---

## Questions?

**Q: Do I need to train models?**  
A: No, optional. The system works without them (uses baseline predictions).

**Q: How often should I retrain?**  
A: Monthly or quarterly to keep models updated with recent data.

**Q: Can I train custom stocks?**  
A: Yes! Use `TRAIN_LSTM_CUSTOM.bat` or `TRAIN_LSTM_SINGLE.bat <SYMBOL>`

**Q: What if training fails?**  
A: Check error message. Common issues:
- Insufficient memory (close other programs)
- Network issues (check internet)
- Invalid stock symbol (verify on Yahoo Finance)

---

## Summary

**Problem**: TensorFlow detection fails in `TRAIN_LSTM_OVERNIGHT.bat`  
**Fix**: Change line 57 to simpler import check  
**Time**: 30 seconds (automatic) or 2 minutes (manual)  
**Risk**: None (backup created automatically)  
**Result**: Training works correctly ✅

---

**Choose your fix method and get training!** 🚀
