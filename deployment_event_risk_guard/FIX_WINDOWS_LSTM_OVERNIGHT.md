# Windows 11 Fix: TRAIN_LSTM_OVERNIGHT.bat TensorFlow Detection Issue

## Date: 2025-11-15

## Problem
When running `TRAIN_LSTM_OVERNIGHT.bat` on Windows 11, you see:

```
Checking for TensorFlow installation...
TensorFlow 2.20.0 detected
  Run: pip install -r requirements.txt
  Time: ~15 minutes (downloads ~2.5 GB)

After installing, run this script again.

Press any key to continue . . .
```

**Even though TensorFlow IS installed**, the script exits with an error.

---

## Root Cause

The batch file line 57 uses a complex Python command that doesn't reliably set the errorlevel:

```batch
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} detected')" 2>nul
```

This causes the `if errorlevel 1` check to incorrectly trigger the error message.

---

## Fix Instructions for Windows 11

### Method 1: Manual Edit (5 minutes)

#### Step 1: Open the File
1. Navigate to: `C:\Users\david\AASS\deployment_event_risk_guard`
2. Right-click on **`TRAIN_LSTM_OVERNIGHT.bat`**
3. Select **"Edit"** or **"Open with" → "Notepad"**

#### Step 2: Find Line 57
Press `Ctrl+G` (Go To) or scroll down to **line 57** which currently says:

```batch
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} detected')" 2>nul
```

#### Step 3: Replace Line 57
**DELETE the entire line 57** and replace it with:

```batch
python -c "import tensorflow" 2>nul
```

#### Step 4: Save the File
1. Press `Ctrl+S` to save
2. Close Notepad

#### Step 5: Test the Fix
Double-click **`TRAIN_LSTM_OVERNIGHT.bat`** again.

You should now see:
```
Checking for TensorFlow installation...
[OK] TensorFlow is installed

========================================================================
  STARTING LSTM TRAINING
========================================================================

Training will begin in 5 seconds...
Press Ctrl+C to cancel
```

✅ **SUCCESS!** The script will now proceed to train the models.

---

### Method 2: PowerShell Script (Automated)

If you prefer an automated fix, use PowerShell:

#### Step 1: Open PowerShell
1. Press `Win+X`
2. Select **"Windows PowerShell"** or **"Terminal"**

#### Step 2: Navigate to Directory
```powershell
cd "C:\Users\david\AASS\deployment_event_risk_guard"
```

#### Step 3: Run Fix Command
Copy and paste this **entire command** (all 3 lines):

```powershell
(Get-Content "TRAIN_LSTM_OVERNIGHT.bat") -replace 'python -c "import tensorflow; print\(f''TensorFlow \{tensorflow\.__version__\} detected''\)" 2>nul', 'python -c "import tensorflow" 2>nul' | Set-Content "TRAIN_LSTM_OVERNIGHT.bat"
```

#### Step 4: Verify the Fix
```powershell
Select-String -Path "TRAIN_LSTM_OVERNIGHT.bat" -Pattern "python -c.*tensorflow" | Select-Object -First 1
```

You should see:
```
57:python -c "import tensorflow" 2>nul
```

#### Step 5: Test
```powershell
.\TRAIN_LSTM_OVERNIGHT.bat
```

---

### Method 3: Download Fixed File

If you want to be absolutely sure, I can provide the corrected file:

#### Step 1: Backup Original
```batch
copy TRAIN_LSTM_OVERNIGHT.bat TRAIN_LSTM_OVERNIGHT.bat.backup
```

#### Step 2: Replace with Fixed Version
The fixed version is already in your deployment package. The key change is:

**BEFORE (Line 57 - BROKEN)**:
```batch
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} detected')" 2>nul
```

**AFTER (Line 57 - FIXED)**:
```batch
python -c "import tensorflow" 2>nul
```

---

## Visual Guide: Notepad Edit

### What You'll See in Notepad:

**Line 55-60 BEFORE Fix**:
```batch
55: REM Check if TensorFlow is installed
56: echo Checking for TensorFlow installation...
57: python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} detected')" 2>nul
58: if errorlevel 1 (
59:     echo.
60:     echo [WARNING] TensorFlow not detected
```

**Line 55-60 AFTER Fix**:
```batch
55: REM Check if TensorFlow is installed
56: echo Checking for TensorFlow installation...
57: python -c "import tensorflow" 2>nul
58: if errorlevel 1 (
59:     echo.
60:     echo [WARNING] TensorFlow not detected
```

**ONLY LINE 57 CHANGES!** - Everything else stays the same.

---

## Why This Fix Works

### The Problem
The old complex command tried to do two things:
1. Import tensorflow ✅
2. Print the version with an f-string ❌

Windows batch files don't handle Python f-strings reliably in command-line context, causing inconsistent exit codes.

### The Solution
The new simple command does one thing:
1. Import tensorflow ✅

If import succeeds → errorlevel 0 → Script continues  
If import fails → errorlevel 1 → Show error message

Simple, clean, reliable. ✅

---

## Verification Steps

After applying the fix, verify it works:

### Test 1: Check TensorFlow Detection
```batch
TRAIN_LSTM_OVERNIGHT.bat
```

**Expected Output**:
```
[OK] Python detected

Checking for TensorFlow installation...
[OK] TensorFlow is installed

========================================================================
  STARTING LSTM TRAINING
========================================================================
```

### Test 2: Cancel Training (Optional)
Press `Ctrl+C` when you see "Training will begin in 5 seconds..."

This confirms the TensorFlow check passed and you can proceed when ready.

---

## If Fix Doesn't Work

If you still see the error after applying the fix:

### Troubleshooting

#### 1. Verify TensorFlow is Actually Installed
Open **PowerShell** or **Command Prompt**:
```batch
python -c "import tensorflow; print(tensorflow.__version__)"
```

**Expected Output**:
```
2.20.0
```

If you get an error, TensorFlow is NOT installed. Install it:
```batch
pip install tensorflow>=2.13.0
```

#### 2. Check Python Version
```batch
python --version
```

**Expected**: `Python 3.12.9` (or any 3.8+)

#### 3. Verify File Was Saved
Open `TRAIN_LSTM_OVERNIGHT.bat` again and check line 57.

If it still shows the old version, the save didn't work. Try:
- Close any programs that might have the file open
- Save with a different name: `TRAIN_LSTM_OVERNIGHT_FIXED.bat`
- Run the new file instead

#### 4. Try Different Editor
If Notepad doesn't save properly:
- Use **Notepad++** (free download)
- Use **VSCode** (free download)
- Use **WordPad** (built-in Windows app)

**Important**: Save as **"All Files (*.*)"** and keep the `.bat` extension!

---

## Quick Copy-Paste Fix (Easiest Method)

### Option A: One-Line Notepad Fix

1. Open `TRAIN_LSTM_OVERNIGHT.bat` in Notepad
2. Press `Ctrl+H` (Find and Replace)
3. In **"Find what"** box, paste:
   ```
   python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} detected')" 2>nul
   ```
4. In **"Replace with"** box, paste:
   ```
   python -c "import tensorflow" 2>nul
   ```
5. Click **"Replace All"**
6. Press `Ctrl+S` to save
7. Close Notepad

### Option B: PowerShell One-Liner (Advanced)

Open PowerShell in the `deployment_event_risk_guard` folder and run:

```powershell
(Get-Content .\TRAIN_LSTM_OVERNIGHT.bat) | ForEach-Object { $_ -replace 'python -c "import tensorflow; print\(f.*detected.*2>nul', 'python -c "import tensorflow" 2>nul' } | Set-Content .\TRAIN_LSTM_OVERNIGHT.bat
```

---

## After Fix is Applied

Once the fix is working, you can proceed with training:

### Full Training Run
```batch
TRAIN_LSTM_OVERNIGHT.bat
```

This will train LSTM models for 10 ASX stocks:
- CBA.AX, ANZ.AX, NAB.AX, WBC.AX, MQG.AX
- BHP.AX, RIO.AX, CSL.AX, WES.AX, BOQ.AX

**Expected Time**: 1.5-2 hours (10-15 minutes per stock)

### Quick Test Run (Single Stock)
If you want to test with just one stock first:
```batch
TRAIN_LSTM_SINGLE.bat CBA.AX
```

**Expected Time**: 10-15 minutes

---

## Summary

**What to Change**: Line 57 in `TRAIN_LSTM_OVERNIGHT.bat`

**From**:
```batch
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} detected')" 2>nul
```

**To**:
```batch
python -c "import tensorflow" 2>nul
```

**How**: Open in Notepad, edit line 57, save, test.

**Result**: TensorFlow detection now works correctly! ✅

---

## Need Help?

If you encounter issues:

1. **Check the backup**: `TRAIN_LSTM_OVERNIGHT.bat.backup`
2. **Verify Python works**: `python --version`
3. **Verify TensorFlow works**: `python -c "import tensorflow"`
4. **Check file encoding**: Save as UTF-8 in Notepad

---

## Files Modified

- `TRAIN_LSTM_OVERNIGHT.bat` - Line 57 only

## Files NOT Modified

- `train_lstm_batch.py` - No changes needed
- `TRAIN_LSTM_SINGLE.bat` - Already fixed (different issue)
- `TRAIN_LSTM_CUSTOM.bat` - No changes needed
- All other files - No changes needed

---

**That's it!** One line change, and your LSTM training will work perfectly. 🎉
