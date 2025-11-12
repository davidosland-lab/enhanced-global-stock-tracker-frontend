# LSTM Training Troubleshooting Guide

## 🐛 **Your Issue**

**Problem**: LSTM training crashes quickly and you can't see the error message

**Error Shown**:
```
FileNotFoundError: [Errno 2] No such file or directory: 
'C:\\Users\\david\\AOSS\\models\\config\\asx_sectors.json'
```

---

## ✅ **Solution - Use Fixed Scripts**

### **Quick Fix** (Recommended):

1. **Run Diagnostic Script**:
   ```batch
   DIAGNOSE_LSTM_ISSUE.bat
   ```
   - This will check all requirements
   - **Automatically fixes missing config file**
   - Shows clear error messages
   - Pauses so you can read output

2. **Use Fixed Scripts**:
   ```batch
   CHECK_MODEL_STATUS_FIXED.bat
   RUN_LSTM_TRAINING_FIXED.bat
   ```
   - Slower output (you can read it)
   - Auto-fixes missing config files
   - Better error messages
   - Pauses at each step

---

## 📋 **Why It's Failing**

### **Root Cause**: Missing `asx_sectors.json` file

The LSTM trainer needs this file to know which ASX stocks to train. The file should be at:
```
C:\Users\david\AOSS\models\config\asx_sectors.json
```

But it's actually located at:
```
C:\Users\david\AOSS\finbert_v4.4.4\models\config\asx_sectors.json
```

### **What the File Contains**:
- List of 240 ASX stocks across 8 sectors
- Sector weights and selection criteria
- Used by screening and training systems

---

## 🔧 **Manual Fix** (If Auto-Fix Doesn't Work)

### **Option 1**: Copy Configuration File
```batch
cd C:\Users\david\AOSS
copy finbert_v4.4.4\models\config\asx_sectors.json models\config\asx_sectors.json
```

### **Option 2**: Create models\config Directory
```batch
cd C:\Users\david\AOSS
mkdir models\config
copy finbert_v4.4.4\models\config\*.json models\config\
```

This copies **all** config files from FinBERT to the screener.

---

## 🚀 **Step-by-Step Recovery**

### **Step 1: Run Diagnostic**
```batch
DIAGNOSE_LSTM_ISSUE.bat
```

**What it does**:
- ✅ Checks Python installation
- ✅ Checks required packages (TensorFlow, pandas, yfinance)
- ✅ Checks directory structure
- ✅ **Automatically copies missing config file**
- ✅ Creates required directories
- ✅ Shows clear summary

**Expected Output**:
```
[STEP 1/7] Checking Current Directory
[STEP 2/7] Checking Python Installation
[STEP 3/7] Checking Required Python Packages
[STEP 4/7] Checking Directory Structure
[STEP 5/7] Checking Configuration Files
  [FIX] Found source file, attempting to copy...
  [SUCCESS] Configuration file copied!
[STEP 6/7] Checking FinBERT Integration
[STEP 7/7] Checking Output Directories

[SUCCESS] All diagnostics passed!
```

---

### **Step 2: Check Model Status**
```batch
CHECK_MODEL_STATUS_FIXED.bat
```

**What it does**:
- Shows how many LSTM models are trained
- Shows which models are stale (>7 days old)
- Slower output with pauses
- Auto-fixes config issues

**Expected Output**:
```
[INFO] Verifying required files...
[OK] Configuration file exists
[OK] Screening configuration exists

LSTM MODEL TRAINING STATISTICS
Total Models: 0
Fresh Models: 0 (0.0%)
Stale Models: 0 (0.0%)

Found 240 stale models:
  - CBA.AX
  - BHP.AX
  - RIO.AX
  ... and 237 more
```

---

### **Step 3: Train LSTM Models**
```batch
RUN_LSTM_TRAINING_FIXED.bat --max-stocks 5
```

**What it does**:
- Trains LSTM models for top 5 priority stocks
- Shows progress for each stock
- Pauses at each step
- Better error messages

**Expected Output**:
```
[INFO] Checking TensorFlow installation...
[OK] TensorFlow is installed

[INFO] Verifying configuration files...
[OK] asx_sectors.json exists

STARTING LSTM MODEL TRAINING

Training Stock 1/5: CBA.AX
  Fetching historical data...
  Preparing sequences...
  Training model (50 epochs)...
  Epoch 1/50 - loss: 0.0234
  ...
  Model saved: models/trained/CBA.AX_lstm.h5

[SUCCESS] LSTM training completed successfully
```

**Note**: Each stock takes 5-15 minutes to train.

---

## 🔍 **Common Issues & Solutions**

### **Issue 1: TensorFlow Not Installed**
```
[ERROR] TensorFlow not installed - REQUIRED FOR LSTM!
```

**Solution**:
```batch
pip install tensorflow>=2.13.0
```

Or run:
```batch
INSTALL_DEPENDENCIES.bat
```

---

### **Issue 2: Insufficient Data**
```
[ERROR] Not enough data to train CBA.AX (need 60 days, got 30)
```

**Why**: Stock needs at least 60 days of historical data for LSTM training

**Solution**:
- Wait for more data to accumulate
- Or skip this stock (it will use fallback predictions)

---

### **Issue 3: Memory Error**
```
[ERROR] MemoryError: Unable to allocate array
```

**Why**: LSTM training requires 2-4GB RAM per stock

**Solution**:
1. Train fewer stocks at once:
   ```batch
   RUN_LSTM_TRAINING_FIXED.bat --max-stocks 3
   ```

2. Close other programs to free RAM

3. Train one stock at a time:
   ```batch
   RUN_LSTM_TRAINING_FIXED.bat --symbols CBA.AX
   ```

---

### **Issue 4: Screen Closes Too Fast**
```
You see errors but screen closes immediately
```

**Why**: Original batch scripts don't pause on errors

**Solution**: Use the fixed scripts:
- `CHECK_MODEL_STATUS_FIXED.bat` (pauses automatically)
- `RUN_LSTM_TRAINING_FIXED.bat` (pauses at each step)
- `DIAGNOSE_LSTM_ISSUE.bat` (pauses throughout)

---

### **Issue 5: Network Timeout**
```
[ERROR] Failed to fetch data for BHP.AX (Connection timeout)
```

**Why**: yfinance needs internet to fetch historical stock data

**Solution**:
1. Check internet connection
2. Try again (yfinance sometimes has rate limits)
3. Wait a few minutes and retry

---

## 📊 **Understanding LSTM Training**

### **What LSTM Training Does**:
1. **Fetches** 3 months of historical stock data
2. **Prepares** 60-day sequences for training
3. **Trains** 3-layer neural network (128→64→32 neurons)
4. **Validates** on 20% of data
5. **Saves** trained model as `.h5` file

### **Training Time**:
- **Per Stock**: 5-15 minutes
- **10 Stocks**: 50-150 minutes (~1-2.5 hours)
- **20 Stocks**: 100-300 minutes (~2-5 hours)

### **When to Train**:
- **Daily**: Top 5-10 priority stocks
- **Weekly**: Top 20 stocks by opportunity score
- **Monthly**: All 240 stocks (overnight batch)

---

## 🎯 **Best Practices**

### **Start Small**:
```batch
REM Train just 3 stocks first
RUN_LSTM_TRAINING_FIXED.bat --max-stocks 3
```

### **Train Specific Stocks**:
```batch
REM Train your favorite stocks
RUN_LSTM_TRAINING_FIXED.bat --symbols CBA.AX BHP.AX WES.AX
```

### **Monitor Progress**:
```batch
REM Check status before and after
CHECK_MODEL_STATUS_FIXED.bat
```

### **Check Logs**:
```
Location: logs\lstm_training\lstm_training.log
```

View detailed training progress and any errors.

---

## 📁 **File Locations**

### **Configuration Files**:
```
models/config/asx_sectors.json         (stock list)
models/config/screening_config.json    (screening settings)
```

### **Trained Models**:
```
models/trained/CBA.AX_lstm.h5
models/trained/BHP.AX_lstm.h5
...
```

### **Training Logs**:
```
logs/lstm_training/lstm_training.log
logs/lstm_training/training_results.jsonl
```

### **Scripts**:
```
DIAGNOSE_LSTM_ISSUE.bat               (diagnostic tool)
CHECK_MODEL_STATUS_FIXED.bat          (status checker)
RUN_LSTM_TRAINING_FIXED.bat           (training runner)
```

---

## ✅ **Verification Steps**

### **After Fixing**:

1. **Run Diagnostic**:
   ```batch
   DIAGNOSE_LSTM_ISSUE.bat
   ```
   Should show: `[SUCCESS] All diagnostics passed!`

2. **Check Status**:
   ```batch
   CHECK_MODEL_STATUS_FIXED.bat
   ```
   Should show model statistics without errors

3. **Train Test Stock**:
   ```batch
   RUN_LSTM_TRAINING_FIXED.bat --symbols CBA.AX --max-stocks 1
   ```
   Should train CBA successfully in ~10 minutes

4. **Verify Model File**:
   ```batch
   dir models\trained\CBA.AX_lstm.h5
   ```
   File should exist with size ~1-5MB

---

## 🆘 **Still Having Issues?**

### **Check Logs**:
```batch
type logs\lstm_training\lstm_training.log
```

### **Run Full Diagnostic**:
```batch
DIAGNOSE_LSTM_ISSUE.bat
```

### **Verify Python Packages**:
```batch
pip list | findstr "tensorflow pandas numpy yfinance"
```

Should show:
- `tensorflow    2.13.0` (or higher)
- `pandas       1.5.0` (or higher)
- `numpy        1.24.0` (or higher)
- `yfinance     0.2.30` (or higher)

### **Reinstall Dependencies**:
```batch
INSTALL_DEPENDENCIES.bat
```

---

## 📚 **Additional Resources**

### **Documentation**:
- `QUICK_START_INTEGRATION.md` - Setup guide
- `FINBERT_MODEL_EXPLAINED.md` - How FinBERT works
- `INTEGRATION_COMPLETE_SUMMARY.md` - Complete overview

### **Related Scripts**:
- `INSTALL_DEPENDENCIES.bat` - Install all requirements
- `RUN_OVERNIGHT_SCREENER.bat` - Run complete screening
- `test_finbert_integration.py` - Test integration

---

## 🎉 **Success Indicators**

### **Training Working When You See**:
```
[OK] TensorFlow is installed
[OK] Configuration file exists
Training Stock 1/5: CBA.AX
  Training model (50 epochs)...
  Epoch 1/50 - loss: 0.0234
  Epoch 50/50 - loss: 0.0012
  Model saved: models/trained/CBA.AX_lstm.h5
[SUCCESS] Training completed
```

### **Then You Can**:
1. ✅ Train more stocks
2. ✅ Run overnight screener
3. ✅ Use real LSTM predictions (not fallbacks)
4. ✅ Get higher accuracy predictions

---

**Last Updated**: November 7, 2024  
**Version**: LSTM Troubleshooting v1.0  
**Status**: ✅ Ready to Use
