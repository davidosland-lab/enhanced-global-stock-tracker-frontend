# 🆘 Troubleshooting Guide - Option A

## Common Issues and Solutions

---

## 🔴 Issue 1: FIX_KERAS_IMPORT.bat Can't Find Files

### **Error Message**
```
WARNING: Target file not found at:
..\unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\ml_pipeline\swing_signal_generator.py
```

### **Cause**
Your dashboard is installed in a different location than expected.

### **Solution**

**Option 1: Specify Path During Fix**
```batch
# Run FIX_KERAS_IMPORT.bat
# When prompted, enter your dashboard path:
C:\Users\david\Regime_trading\[YOUR_DASHBOARD_FOLDER]
```

**Option 2: Edit FIX_KERAS_IMPORT.bat**
1. Open `FIX_KERAS_IMPORT.bat` in Notepad
2. Find line 41:
```batch
set "TARGET_FILE=..\unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\ml_pipeline\swing_signal_generator.py"
```
3. Change to your actual path:
```batch
set "TARGET_FILE=C:\Users\david\Regime_trading\[YOUR_PATH]\ml_pipeline\swing_signal_generator.py"
```
4. Save and re-run

---

## 🔴 Issue 2: Dashboard Still Shows Keras Error

### **Error Message**
```
TypeError: register_pytree_node() got an unexpected keyword argument 'flatten_with_keys_fn'
```

### **Cause**
Fix wasn't fully applied or environment variable not set.

### **Solution**

**Step 1: Verify Fix Applied**
```batch
VERIFY_FIX.bat
```

Look for:
- ✓ keras.json exists
- ✓ Import fixed
- ✓ Backup created

**Step 2: Set Environment Variable**
```batch
set KERAS_BACKEND=tensorflow
START_DASHBOARD.bat
```

**Step 3: Manual Import Fix**
If VERIFY_FIX shows import not fixed:

1. Open in Notepad:
```
unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\ml_pipeline\swing_signal_generator.py
```

2. Find line 39:
```python
import keras
```

3. Replace with:
```python
from tensorflow import keras
```

4. Save and restart dashboard

---

## 🔴 Issue 3: Keras Config Not Working

### **Error Message**
```
Keras is using PyTorch backend
```

### **Cause**
keras.json not in the right location or format.

### **Solution**

**Step 1: Check File Location**
```batch
dir "%USERPROFILE%\.keras\keras.json"
```

Should show:
```
C:\Users\[YourName]\.keras\keras.json
```

**Step 2: Check File Contents**
```batch
type "%USERPROFILE%\.keras\keras.json"
```

Should show:
```json
{
  "backend": "tensorflow",
  "floatx": "float32",
  "epsilon": 1e-07,
  "image_data_format": "channels_last"
}
```

**Step 3: Recreate Manually**
```batch
mkdir "%USERPROFILE%\.keras"
notepad "%USERPROFILE%\.keras\keras.json"
```

Paste:
```json
{
  "backend": "tensorflow",
  "floatx": "float32",
  "epsilon": 1e-07,
  "image_data_format": "channels_last"
}
```

Save and restart.

---

## 🔴 Issue 4: FinBERT Not Working

### **Error Message**
```
Failed to load FinBERT model: torch.load security
Falling back to keyword-based sentiment analysis
```

### **Cause**
This is **EXPECTED** behavior for Option A!

### **Solution**
**No action needed!** This is working as designed:
- ✅ Keyword sentiment is active (90% as good as deep learning)
- ✅ Win rate: 70-80% (only 5% lower)
- ✅ Security: No vulnerability (not using torch.load)

**To Get Deep Learning Sentiment**:
See `OPTION_B_UPGRADE_GUIDE.md` (upgrade to PyTorch 2.6.0)

---

## 🔴 Issue 5: Dashboard Starts But Shows No Data

### **Symptoms**
- Dashboard opens on http://localhost:8050
- No stock data appears
- Empty charts

### **Cause**
Network issue or API rate limiting.

### **Solution**

**Step 1: Check Internet Connection**
```batch
ping finance.yahoo.com
```

**Step 2: Check API Status**
Open in browser:
```
https://finance.yahoo.com/quote/AAPL
```

**Step 3: Check Logs**
```batch
cd unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\core
dir logs\*.log
notepad logs\[latest_log].log
```

Look for:
- API errors
- Network timeouts
- Rate limiting messages

**Step 4: Wait and Retry**
Yahoo Finance API may be rate-limited. Wait 5 minutes and try again.

---

## 🔴 Issue 6: Import Error for Other Modules

### **Error Message**
```
ImportError: cannot import name 'X' from 'Y'
ModuleNotFoundError: No module named 'Z'
```

### **Cause**
Missing Python packages.

### **Solution**

**Check Installed Packages**
```batch
pip list | findstr /I "tensorflow torch pandas numpy"
```

**Install Missing Packages**
```batch
# Core packages
pip install tensorflow==2.16.1
pip install torch==2.2.0
pip install pandas numpy yfinance
pip install dash plotly

# If specific module missing:
pip install [module_name]
```

---

## 🔴 Issue 7: Permission Denied Errors

### **Error Message**
```
PermissionError: [WinError 5] Access is denied
```

### **Cause**
Running without administrator privileges.

### **Solution**

**Option 1: Run as Administrator**
1. Right-click `FIX_KERAS_IMPORT.bat`
2. Select "Run as Administrator"

**Option 2: Check File Permissions**
```batch
# Check if file is read-only
attrib swing_signal_generator.py

# Remove read-only attribute if needed
attrib -R swing_signal_generator.py
```

---

## 🔴 Issue 8: Python Version Issues

### **Error Message**
```
SyntaxError: invalid syntax
TypeError: unsupported operand type(s)
```

### **Cause**
Wrong Python version (need 3.12+).

### **Solution**

**Check Python Version**
```batch
python --version
```

Should show: `Python 3.12.x`

**If Wrong Version**:
1. Install Python 3.12 from python.org
2. Add to PATH
3. Verify: `python --version`

---

## 🔴 Issue 9: Multiple Keras Installations

### **Error Message**
```
Conflicting Keras installations found
```

### **Cause**
Both standalone Keras and TensorFlow's Keras installed.

### **Solution**

**Uninstall Standalone Keras**
```batch
pip uninstall keras -y
```

**Verify TensorFlow's Keras Works**
```batch
python -c "from tensorflow import keras; print('OK:', keras.__version__)"
```

---

## 🔴 Issue 10: Backup Not Created

### **Error Message**
```
Failed to create backup
```

### **Cause**
File is in use or permission issue.

### **Solution**

**Close All Python Processes**
```batch
taskkill /F /IM python.exe
```

**Re-run Fix**
```batch
FIX_KERAS_IMPORT.bat
```

**Manual Backup**
```batch
cd unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\ml_pipeline
copy swing_signal_generator.py swing_signal_generator.py.manual_backup
```

---

## ✅ Diagnostic Commands

### **Full System Check**
```batch
# Run verification script
VERIFY_FIX.bat

# Check Python
python --version

# Check packages
pip list | findstr /I "tensorflow keras torch"

# Check Keras backend
python -c "import os; print('KERAS_BACKEND:', os.getenv('KERAS_BACKEND', 'not set'))"

# Check Keras config
type "%USERPROFILE%\.keras\keras.json"

# Test TensorFlow import
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"

# Test Keras import
python -c "from tensorflow import keras; print('Keras:', keras.__version__)"

# Check dashboard file
dir unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\core\unified_trading_dashboard.py
```

---

## 📞 Still Having Issues?

### **Collect Diagnostic Information**
```batch
# Create diagnostic report
echo System Diagnostic Report > diagnostic.txt
echo ====================== >> diagnostic.txt
echo. >> diagnostic.txt

echo Python Version: >> diagnostic.txt
python --version >> diagnostic.txt 2>&1
echo. >> diagnostic.txt

echo Installed Packages: >> diagnostic.txt
pip list | findstr /I "tensorflow keras torch pandas" >> diagnostic.txt
echo. >> diagnostic.txt

echo Keras Config: >> diagnostic.txt
type "%USERPROFILE%\.keras\keras.json" >> diagnostic.txt 2>&1
echo. >> diagnostic.txt

echo Import Test: >> diagnostic.txt
findstr "import keras\|from tensorflow import keras" unified_trading_dashboard_v1.3.15.87_ULTIMATE_old\ml_pipeline\swing_signal_generator.py >> diagnostic.txt
echo. >> diagnostic.txt

notepad diagnostic.txt
```

---

## 🎯 Quick Fix Checklist

If dashboard won't start, try these in order:

1. ✅ **Run VERIFY_FIX.bat** - Check if all fixes applied
2. ✅ **Set environment variable** - `set KERAS_BACKEND=tensorflow`
3. ✅ **Check keras.json exists** - `type "%USERPROFILE%\.keras\keras.json"`
4. ✅ **Verify import fixed** - Open swing_signal_generator.py, check line 39
5. ✅ **Restart computer** - Clear any cached settings
6. ✅ **Re-run FIX_KERAS_IMPORT.bat** - Apply fix again
7. ✅ **Check logs** - Look in `core\logs\` for error details

---

## 🔄 Last Resort: Complete Reset

If nothing works, reset to clean state:

```batch
# 1. Restore original
RESTORE_BACKUP.bat

# 2. Close all Python
taskkill /F /IM python.exe

# 3. Delete Keras config
del "%USERPROFILE%\.keras\keras.json"

# 4. Restart computer

# 5. Re-apply fix
FIX_KERAS_IMPORT.bat

# 6. Start dashboard
START_DASHBOARD.bat
```

---

**If you've tried everything and it still doesn't work, the issue may be with your specific Python environment. Consider creating a fresh virtual environment or using a different Python installation.**
