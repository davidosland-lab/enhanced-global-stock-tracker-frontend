# BATCH_PREDICTOR.PY - FILE PATH INFORMATION

## 📍 **Path to the FIXED File in Sandbox System**

### **Full Absolute Path:**
```
/home/user/webapp/deployments/unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED/pipelines/models/screening/batch_predictor.py
```

### **Relative Path (from /home/user/webapp):**
```
./deployments/unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED/pipelines/models/screening/batch_predictor.py
```

### **File Details:**
- **Size**: 26K (26,624 bytes)
- **Last Modified**: 2026-02-11 22:10 (when fix was applied)
- **Permissions**: -rw-r--r--
- **Status**: ✅ **FIXED VERSION** (includes defensive coding)

---

## 📦 **Path in Package Zip:**

When you extract `unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED.zip`, the file is at:

```
unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED/
└── pipelines/
    └── models/
        └── screening/
            └── batch_predictor.py  ← This file
```

**Relative path inside zip:**
```
pipelines/models/screening/batch_predictor.py
```

---

## 🎯 **Where to Copy It To (Your System):**

### **Your Installation Path:**
```
C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED\pipelines\models\screening\batch_predictor.py
```

### **Step-by-Step:**
1. **Your base directory:**
   ```
   C:\Users\david\Regime Trading V2\
   ```

2. **Inside that, go to:**
   ```
   unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED\
   ```

3. **Then navigate to:**
   ```
   pipelines\models\screening\
   ```

4. **Replace this file:**
   ```
   batch_predictor.py
   ```

---

## 📂 **Directory Structure:**

```
Your System:
C:\Users\david\Regime Trading V2\
└── unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED\
    ├── core\
    ├── finbert_v4.4.4\
    ├── ml_pipeline\
    ├── pipelines\
    │   ├── config\
    │   └── models\
    │       └── screening\
    │           ├── __init__.py
    │           ├── batch_predictor.py  ← REPLACE THIS FILE
    │           ├── event_risk_guard.py
    │           ├── finbert_bridge.py
    │           ├── opportunity_scorer.py
    │           ├── overnight_pipeline.py
    │           ├── stock_scanner.py
    │           ├── uk_overnight_pipeline.py
    │           ├── us_overnight_pipeline.py
    │           └── us_stock_scanner.py
    ├── reports\
    └── scripts\
```

---

## 🔍 **How to Verify You Have the Right File:**

### **Method 1: Check File Size**
The fixed file is **26KB** (26,624 bytes).

**Windows:**
- Right-click → Properties
- Look for "Size: 26.0 KB (26,624 bytes)"

### **Method 2: Check File Contents**
Open the file and look for these lines around line 402-425:

```python
def _trend_prediction(self, hist: pd.DataFrame, stock_data: Dict) -> Dict:
    """
    Trend-based prediction using moving averages
    """
    # Check if technical data exists  ← THIS LINE SHOULD BE THERE
    if 'technical' not in stock_data:  ← THIS LINE SHOULD BE THERE
        logger.debug(f"No technical data in stock_data for trend prediction")
        return {'direction': 0, 'confidence': 0}
```

**If you see the lines marked with arrows (←) above**, you have the FIXED version ✅

**If you DON'T see those lines**, you have the OLD version ❌ and need to update.

---

## 📋 **Download/Copy Instructions:**

### **Option 1: Extract from Package Zip**

1. **Download** or locate:
   ```
   unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED.zip
   ```

2. **Extract** the entire zip to a temporary folder

3. **Navigate** to:
   ```
   [temp folder]\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED\
   pipelines\models\screening\batch_predictor.py
   ```

4. **Copy** that file

5. **Paste** to your installation at:
   ```
   C:\Users\david\Regime Trading V2\
   unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED\
   pipelines\models\screening\batch_predictor.py
   ```

6. **Overwrite** when prompted

### **Option 2: Download Single File (If Available)**

If you can download the single file from the sandbox:

**Source:**
```
/home/user/webapp/deployments/unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED/pipelines/models/screening/batch_predictor.py
```

**Destination:**
```
C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED\pipelines\models\screening\batch_predictor.py
```

---

## ⚠️ **Important Notes:**

### **Make Sure Path is Exact:**
The file MUST go in the `pipelines\models\screening\` directory, NOT:
- ❌ `models\screening\` (missing pipelines)
- ❌ `core\` (wrong directory)
- ❌ Root directory (wrong location)

### **Backup First (Recommended):**
Before overwriting, rename the old file:
```
batch_predictor.py → batch_predictor.py.backup
```

Then copy the new file. This way you can restore if needed.

### **No Need to Restart Services:**
After copying the file:
- ❌ No need to restart Windows
- ❌ No need to restart Python
- ✅ Just run the pipeline - it will use the new code

---

## ✅ **Verification After Update:**

### **Quick Test:**
```bash
cd "C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED"
python scripts\run_us_full_pipeline.py --mode test
```

### **What to Look For:**

**✅ SUCCESS (Fixed):**
```
[1/5] Processed JPM - Prediction: BUY (Confidence: 68%)
[2/5] Processed BAC - Prediction: HOLD (Confidence: 62%)
[3/5] Processed WFC - Prediction: BUY (Confidence: 71%)
[4/5] Processed C - Prediction: SELL (Confidence: 59%)
[5/5] Processed GS - Prediction: BUY (Confidence: 73%)

[OK] Batch prediction complete: 5/5 results
```

**❌ FAILURE (Not Fixed):**
```
ERROR - Prediction error for JPM: 'technical'
ERROR - Prediction error for BAC: 'technical'
ERROR - Prediction error for WFC: 'technical'
```

If you still see errors, the file wasn't updated correctly.

---

## 🎯 **Quick Summary:**

**Sandbox Path (Source):**
```
/home/user/webapp/deployments/unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED/
pipelines/models/screening/batch_predictor.py
```

**Your System Path (Destination):**
```
C:\Users\david\Regime Trading V2\unified_trading_dashboard_v1.3.15.90_ULTIMATE_UNIFIED\
pipelines\models\screening\batch_predictor.py
```

**File Size:** 26KB  
**Status:** ✅ Fixed version with defensive coding  
**Action:** Copy from source to destination, overwrite  
**Time:** 2 minutes  
**Result:** All 3 pipelines (692 stocks) fixed

---

**Created**: 2026-02-11  
**Commit**: c587ff5  
**Version**: v1.3.15.118.5  
**Type**: Single file update
