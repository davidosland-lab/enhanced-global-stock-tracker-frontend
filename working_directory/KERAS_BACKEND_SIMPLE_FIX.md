# 🔧 SIMPLE FIX: Set Keras Backend to PyTorch

## 🎯 THE PROBLEM

You have:
- ✅ PyTorch installed
- ✅ Keras 3.0 installed
- ❌ Keras doesn't know to use PyTorch (tries TensorFlow instead)

**Simple Fix**: Tell Keras to use PyTorch by setting an environment variable.

---

## ✅ SOLUTION: 3 Easy Options

### Option 1: Run Simple Script (Easiest)

**Download**: `SET_KERAS_BACKEND_SIMPLE.bat`

**Run it from anywhere**:
```batch
# Double-click SET_KERAS_BACKEND_SIMPLE.bat
# Or run from any directory:
SET_KERAS_BACKEND_SIMPLE.bat
```

**Then**:
1. Close terminal
2. Open NEW terminal
3. Start dashboard
4. ✅ No more warning!

---

### Option 2: Set Manually in Windows (Recommended if script fails)

**Steps**:
1. Press `Windows Key` + type "Environment Variables"
2. Click "Edit system environment variables"
3. Click "Environment Variables" button at bottom
4. Under "User variables for [YourName]", click "New"
5. Enter:
   - Variable name: `KERAS_BACKEND`
   - Variable value: `torch`
6. Click "OK" on all windows
7. **Close ALL terminals**
8. Open NEW terminal
9. Start dashboard
10. ✅ No more warning!

**Screenshot guide**:
```
┌─────────────────────────────────────┐
│ Environment Variables               │
├─────────────────────────────────────┤
│ User variables for David:           │
│ ┌─────────────┬──────────────────┐  │
│ │ Variable    │ Value            │  │
│ ├─────────────┼──────────────────┤  │
│ │ KERAS_BACKEND│ torch           │  │ ← Add this
│ └─────────────┴──────────────────┘  │
│                                     │
│        [New] [Edit] [Delete]        │
└─────────────────────────────────────┘
```

---

### Option 3: Set in Command Prompt (Temporary - Quick Test)

**For quick testing**:
```batch
# Set for current session only
set KERAS_BACKEND=torch

# Start dashboard in SAME terminal
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
python unified_trading_dashboard.py
```

**Note**: This only lasts for current terminal session. Use Option 1 or 2 for permanent fix.

---

## 🔍 VERIFY IT WORKED

### Test 1: Check Environment Variable
Open NEW terminal:
```batch
echo %KERAS_BACKEND%
```

**Expected**: `torch`  
**If blank**: Variable not set, try Option 2 (manual)

### Test 2: Check Keras Backend
```batch
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
venv\Scripts\activate
set KERAS_BACKEND=torch
python -c "import keras; print(keras.backend.backend())"
```

**Expected**: `torch`  
**If error**: Restart terminal first

### Test 3: Start Dashboard
Start dashboard and check console:

**Success** ✅:
```
[LSTM] Training model for BHP.AX
[LSTM] Prediction: 0.67
(No Keras warning)
```

**Still broken** ❌:
```
WARNING - Keras/PyTorch not available
```

If still broken, restart terminal again or try Option 2 (manual).

---

## ❓ WHY RESTART TERMINAL?

**Environment variables** are loaded when a terminal/program starts.

- ❌ Setting variable in running terminal: Doesn't affect running Python programs
- ✅ Setting variable then starting NEW terminal: New Python programs see it

**You MUST**:
1. Set the variable (using any option above)
2. Close ALL terminals
3. Open a NEW terminal
4. Start dashboard in NEW terminal

---

## 🛠️ TROUBLESHOOTING

### Problem: Variable won't set
**Solution**: Run Command Prompt as Administrator
1. Search "cmd" in Start Menu
2. Right-click "Command Prompt"
3. Select "Run as administrator"
4. Run: `setx KERAS_BACKEND torch`

### Problem: Still getting warning after restart
**Solution**: Check if variable is actually set
```batch
echo %KERAS_BACKEND%
```
If blank, variable isn't set. Use Option 2 (manual GUI method).

### Problem: "setx" command not found
**Solution**: You're on Windows 7 or earlier. Use Option 2 (manual GUI method).

---

## 📊 WHAT THIS DOES

### Before:
```python
import keras
# Keras looks for TensorFlow (not installed)
# Error: ModuleNotFoundError: No module named 'tensorflow'
```

### After (with KERAS_BACKEND=torch):
```python
import keras
# Keras uses PyTorch (installed!)
# Works! No error!
```

---

## 🎯 SUMMARY

**Problem**: Keras trying to use TensorFlow (not installed)  
**Solution**: Set `KERAS_BACKEND=torch` to use PyTorch (is installed)

**3 Ways to Fix**:
1. 🚀 **Easiest**: Run `SET_KERAS_BACKEND_SIMPLE.bat`
2. 🔧 **Most Reliable**: Set manually in Windows Environment Variables GUI
3. ⚡ **Quick Test**: `set KERAS_BACKEND=torch` in terminal

**After ANY method**: Restart terminal!

**Expected Result**: No more Keras warning, LSTM neural networks enabled

---

## 📝 STEP-BY-STEP (MANUAL METHOD)

If scripts don't work, do this manually:

```
1. Press Windows Key
2. Type "environment"
3. Click "Edit system environment variables"
4. Click "Environment Variables" button
5. Under "User variables", click "New"
6. Variable name: KERAS_BACKEND
7. Variable value: torch
8. Click OK (3 times to close all windows)
9. Close ALL terminals
10. Open NEW terminal
11. cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
12. Start dashboard
13. ✅ No more warning!
```

---

**Files Available**:
- `SET_KERAS_BACKEND_SIMPLE.bat` (can run from anywhere)
- `KERAS_BACKEND_FIX.md` (this guide)

**Both methods work - choose whichever is easier for you!**
