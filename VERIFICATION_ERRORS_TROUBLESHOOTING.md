# Verification Errors - Troubleshooting Guide

## Overview

This guide helps you troubleshoot common errors encountered during the `VERIFY_INSTALLATION.py` check.

---

## Common Errors and Solutions

### 1. **File Structure Check Failed**

**Error:**
```
✗ Missing: models/screening/finbert_bridge.py
✗ Missing: finbert_v4.4.4/models/lstm_predictor.py
```

**Cause:**
- ZIP file was not fully extracted
- Files were extracted to wrong directory
- Incomplete download of ZIP file

**Solution:**
```batch
REM 1. Delete partially extracted files
REM 2. Re-extract the complete ZIP file
REM 3. Make sure you extract to the correct directory
REM 4. Verify ZIP file size matches expected size (345 KB)

REM Expected structure:
C:\YourProjectFolder\
├── models\
│   ├── screening\
│   │   ├── overnight_pipeline.py
│   │   ├── event_risk_guard.py
│   │   ├── finbert_bridge.py        ← Must exist
│   │   └── ...
│   └── config\
│       └── screening_config.json
├── finbert_v4.4.4\                   ← Entire directory must exist
│   ├── models\
│   │   ├── finbert_sentiment.py
│   │   ├── lstm_predictor.py
│   │   └── ...
│   └── ...
└── INSTALL.bat
```

---

### 2. **Python Packages Check Failed**

**Error:**
```
✗ torch             - NOT INSTALLED (PyTorch - FinBERT backend)
✗ transformers      - NOT INSTALLED (HuggingFace Transformers - FinBERT)
✗ tensorflow        - NOT INSTALLED (TensorFlow - LSTM neural networks)
```

**Cause:**
- INSTALL.bat was not run
- Installation failed due to network issues
- Python environment is not activated (if using venv)

**Solution:**

#### Option A: Run Installation Script
```batch
REM Windows
INSTALL.bat

REM Linux/Mac
./install.sh
```

#### Option B: Manual Installation
```batch
REM Install PyTorch first (CRITICAL - must be before other packages)
python -m pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

REM Then install remaining packages
python -m pip install -r requirements.txt
```

#### Option C: Install Individual Packages
```batch
REM If installation fails, install one by one:
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install transformers
python -m pip install tensorflow
python -m pip install scikit-learn
python -m pip install yfinance
python -m pip install pandas numpy
python -m pip install arch
```

**Common PyTorch Issues:**
- **Error: "No matching distribution found"**
  - Solution: Use explicit CDN URL: `--index-url https://download.pytorch.org/whl/cpu`
  
- **Error: "CUDA not available"**
  - This is OKAY - we're using CPU version intentionally
  - PyTorch will work without CUDA

- **Error: "Could not find a version that satisfies the requirement torch"**
  - Solution: Specify exact version: `torch==2.1.0`

---

### 3. **FinBERT Bridge Check Failed**

**Error:**
```
✗ FinBERT Bridge initialization failed: No module named 'models.screening.finbert_bridge'
✗ LSTM Predictor: NOT AVAILABLE
✗ Sentiment Analyzer: NOT AVAILABLE
```

**Cause:**
- `finbert_bridge.py` file is missing
- `finbert_v4.4.4/` directory is missing
- Python import path issues
- Package dependencies not installed (torch, transformers)

**Solution:**

#### Step 1: Check Files Exist
```batch
REM Check if finbert_bridge.py exists
dir models\screening\finbert_bridge.py

REM Check if finbert_v4.4.4 directory exists
dir finbert_v4.4.4\models\
```

If files are missing, re-extract the ZIP file completely.

#### Step 2: Verify Dependencies
```python
# Test PyTorch
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
# Expected: PyTorch: 2.1.0+cpu

# Test Transformers
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
# Expected: Transformers: 4.30.0 or higher

# Test TensorFlow
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
# Expected: TensorFlow: 2.13.0 or higher
```

#### Step 3: Test FinBERT Bridge Directly
```python
# Run from project root directory
python
>>> from models.screening.finbert_bridge import get_finbert_bridge
>>> bridge = get_finbert_bridge()
>>> print(bridge.is_available())
# Expected: {'lstm_available': True, 'sentiment_available': True, 'news_available': True}
```

---

### 4. **Configuration Check Failed**

**Error:**
```
✗ LSTM Training Enabled: False (SHOULD BE TRUE)
✗ Max Models Per Night: 20 (SHOULD BE 100)
```

**Cause:**
- Old version of `screening_config.json` was extracted
- Configuration file was manually edited incorrectly
- Wrong ZIP file was downloaded (v1.3.13 instead of v1.3.14)

**Solution:**

#### Fix Configuration File
Edit `models/config/screening_config.json`:

```json
{
  "lstm_training": {
    "enabled": true,                    // Must be true
    "max_models_per_night": 100,        // Must be 100 (not 20)
    "train_all_scanned_stocks": true,   // Recommended
    "stale_threshold_days": 7,
    "epochs": 50,
    "batch_size": 32,
    "validation_split": 0.2,
    "priority_strategy": "highest_opportunity_score"
  },
  "market_sentiment": {
    "vix_weight": 0.3,
    "spy_weight": 0.4,
    "sector_weight": 0.3
  },
  "event_risk": {
    "earnings_risk_weight": 0.05,
    "dividend_risk_weight": 0.02,
    "basel_concentration_weight": 0.04,
    "regime_crash_weight": 0.10
  },
  "opportunity_scoring": {
    "min_confidence_threshold": 0.5,
    "prediction_weight": 0.60,
    "technical_weight": 0.20,
    "sentiment_weight": 0.10,
    "momentum_weight": 0.10
  }
}
```

**Quick Fix Command:**
```batch
REM Windows - Check current values
findstr /C:"enabled" models\config\screening_config.json
findstr /C:"max_models_per_night" models\config\screening_config.json
```

---

### 5. **PHASE 4.5 Code Check Failed**

**Error:**
```
✗ _train_lstm_models() method exists - NOT FOUND
✗ PHASE 4.5 logging exists - NOT FOUND
✗ PHASE 4.5 is called in pipeline - NOT FOUND
```

**Cause:**
- Wrong version of `overnight_pipeline.py` was extracted
- Old v1.3.13 file was not replaced
- ZIP file extraction failed for this file

**Solution:**

#### Verify File Version
```batch
REM Check if _train_lstm_models method exists
findstr /C:"_train_lstm_models" models\screening\overnight_pipeline.py
# Expected: Should find multiple matches (lines 251, 712, etc.)

REM Check if PHASE 4.5 exists
findstr /C:"PHASE 4.5" models\screening\overnight_pipeline.py
# Expected: Should find at least 2 matches
```

**If Not Found:**
1. Delete the old `overnight_pipeline.py`
2. Re-extract the ZIP file
3. Ensure you're extracting from v1.3.14 (not v1.3.13)

**File Size Check:**
- `overnight_pipeline.py` should be approximately 25-30 KB
- If it's smaller (20 KB), it's likely the old version

---

### 6. **Regime Engine Integration Check Failed**

**Error:**
```
✗ MarketRegimeEngine imported - NOT FOUND
✗ Regime Engine initialized - NOT FOUND
✗ _get_regime_crash_risk() method exists - NOT FOUND
✗ Regime Engine called in assess_batch() - NOT FOUND
```

**Cause:**
- Wrong version of `event_risk_guard.py` was extracted
- Old v1.3.13 file was not replaced

**Solution:**

#### Verify File Version
```batch
REM Check if MarketRegimeEngine is imported
findstr /C:"MarketRegimeEngine" models\screening\event_risk_guard.py
# Expected: Should find multiple matches

REM Check if _get_regime_crash_risk exists
findstr /C:"_get_regime_crash_risk" models\screening\event_risk_guard.py
# Expected: Should find at least 2 matches (definition and call)
```

**If Not Found:**
1. Delete the old `event_risk_guard.py`
2. Re-extract the ZIP file
3. Ensure you're extracting from v1.3.14

**File Size Check:**
- `event_risk_guard.py` should be approximately 18-20 KB
- If it's smaller (14 KB), it's likely the old version

---

## Verification After Fixing

After fixing issues, run verification again:

```batch
REM Windows
VERIFY_INSTALLATION.bat

REM Linux/Mac
./verify_installation.sh

REM Or directly with Python
python VERIFY_INSTALLATION.py
```

**Expected Output When All Checks Pass:**
```
================================================================================
VERIFICATION SUMMARY
================================================================================

✓ File Structure: PASSED
✓ Python Packages: PASSED
✓ FinBERT Bridge: PASSED
✓ Configuration: PASSED
✓ PHASE 4.5 Code: PASSED
✓ Regime Engine Integration: PASSED

================================================================================
✓ ALL CHECKS PASSED - Installation is complete!

You can now run the pipeline with: RUN_PIPELINE.bat
================================================================================

Press Enter to close...
```

---

## Quick Troubleshooting Checklist

### Step 1: File Extraction
- [ ] Downloaded v1.3.14 ZIP (345 KB)
- [ ] Extracted all files to correct directory
- [ ] Verified `finbert_v4.4.4/` directory exists
- [ ] Verified `models/screening/finbert_bridge.py` exists

### Step 2: Python Environment
- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip is working (`python -m pip --version`)
- [ ] Virtual environment activated (if using one)

### Step 3: Dependencies
- [ ] Ran `INSTALL.bat` or `install.sh`
- [ ] PyTorch installed successfully
- [ ] No error messages during installation
- [ ] Can import torch, transformers, tensorflow

### Step 4: Configuration
- [ ] `screening_config.json` has `enabled: true`
- [ ] `screening_config.json` has `max_models_per_night: 100`
- [ ] JSON file is valid (no syntax errors)

### Step 5: Code Files
- [ ] `overnight_pipeline.py` contains PHASE 4.5 code
- [ ] `event_risk_guard.py` contains Regime Engine integration
- [ ] File sizes match expected sizes (25KB, 18KB)

### Step 6: Final Verification
- [ ] Run `VERIFY_INSTALLATION.bat`
- [ ] All 6 checks pass
- [ ] Ready to run pipeline

---

## Getting Additional Help

### If Verification Still Fails:

1. **Capture Full Error Output:**
   ```batch
   python VERIFY_INSTALLATION.py > verification_errors.txt 2>&1
   ```
   
2. **Check Log Files:**
   - Review `verification_errors.txt` for detailed error messages
   
3. **Test Individual Components:**
   ```python
   # Test 1: Python imports
   python -c "import torch, transformers, tensorflow; print('OK')"
   
   # Test 2: FinBERT Bridge
   python -c "from models.screening.finbert_bridge import get_finbert_bridge; print('OK')"
   
   # Test 3: Configuration
   python -c "import json; print(json.load(open('models/config/screening_config.json')))"
   ```

4. **Clean Reinstall:**
   ```batch
   REM Delete all extracted files
   REM Re-download ZIP file (verify size: 345 KB)
   REM Extract to clean directory
   REM Run INSTALL.bat
   REM Run VERIFY_INSTALLATION.bat
   ```

---

## Success Indicators

When verification passes, you should see:
- ✅ All 6 checks marked as PASSED
- ✅ Green checkmarks for all components
- ✅ Message: "ALL CHECKS PASSED - Installation is complete!"

After successful verification, you can:
1. Run test mode: `RUN_PIPELINE.bat --test` (15-20 minutes)
2. Run full pipeline: `RUN_PIPELINE.bat` (70-110 minutes)
3. Check logs: `CHECK_LOGS.bat` (after completion)

---

## Contact Information

If you continue to encounter errors after following this guide:
1. Note the exact error messages
2. Note your Python version (`python --version`)
3. Note your operating system (Windows 10/11, Linux, Mac)
4. Provide the full output from `VERIFY_INSTALLATION.bat`
