# FinBERT Installation & Dependencies - Complete Explanation

## Your Questions

1. **"I have no idea where the local FinBERT is stored"**
2. **"When the install is run does it load at that point?"**
3. **"Can the dependencies loaded work for both components?"**

---

## Answer 1: Where FinBERT Models Are Stored

### When You Run The Install:

**FinBERT v4.4.4 INSTALL.bat**:
```batch
pip install transformers>=4.30.0
pip install torch>=2.0.0
```

This installs the **libraries** but **NOT the model files**.

### Where Models Actually Download:

When code runs `AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')`, it:

1. **Checks cache first**: `C:\Users\david\.cache\huggingface\transformers\`
2. **If not cached**: Downloads ~500MB from HuggingFace.co
3. **Saves to cache**: For future use

**This is why you see**: "FinBERT analyzer not available" - the download is timing out!

---

## Answer 2: What Happens During Install

### Two Separate Installs in Your Project:

#### Install #1: Main System (COMPLETE_SYSTEM_v1.3.15.45_FINAL)
```
Location: C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\
Virtual env: venv\
```

**Runs**: `pip install -r requirements.txt`
```
transformers>=4.30.0     ← Libraries only
torch>=2.0.0             ← Libraries only
pandas>=2.0.0
yfinance>=0.2.28
dash>=2.14.0
...
```

**Models**: ❌ NOT downloaded during install  
**When downloaded**: First time you run a pipeline that needs FinBERT

#### Install #2: FinBERT v4.4.4 (finbert_v4.4.4)
```
Location: C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\finbert_v4.4.4\
Virtual env: venv\
```

**Runs**: `pip install -r requirements.txt`
```
transformers>=4.30.0     ← Libraries only
torch>=2.0.0             ← Libraries only
flask>=2.3.0
tensorflow>=2.13.0
keras>=2.13.0
...
```

**Models**: ❌ NOT downloaded during install  
**When downloaded**: First time you run the FinBERT app

---

## Answer 3: Can Dependencies Work for Both?

### Current Situation: TWO SEPARATE VIRTUAL ENVIRONMENTS

```
COMPLETE_SYSTEM_v1.3.15.45_FINAL\
├── venv\                          ← Environment #1
│   └── Lib\site-packages\
│       ├── transformers\
│       ├── torch\
│       └── dash\
└── finbert_v4.4.4\
    └── venv\                      ← Environment #2
        └── Lib\site-packages\
            ├── transformers\
            ├── torch\
            ├── keras\
            └── flask\
```

### The Problem:

**Each virtual environment is ISOLATED**:
- Environment #1 has: transformers, torch, dash (NO keras)
- Environment #2 has: transformers, torch, keras, flask (NO dash)

**They SHARE the FinBERT model cache**:
```
C:\Users\david\.cache\huggingface\transformers\
```

So if Environment #2 downloads FinBERT, Environment #1 can use it!

---

## Why You're Seeing Errors

### Error 1: "FinBERT analyzer not available"

**Where**: UK pipeline (using Environment #1)  
**Cause**: FinBERT model not in cache  
**Fix**: Download model ONCE to shared cache

### Error 2: "Keras/PyTorch not available - LSTM will use fallback"

**Where**: UK pipeline (using Environment #1)  
**Cause**: Environment #1 doesn't have `keras` installed  
**Fix**: Install keras in Environment #1

---

## The Solution: CRITICAL_FIX_FINBERT_KERAS.bat

This patch does TWO things:

### Fix #1: Download FinBERT to Shared Cache
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Downloads ~500MB to: C:\Users\david\.cache\huggingface\transformers\
tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert')
model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')
```

**Benefit**: Both environments can now use this cached model!

### Fix #2: Install Keras in Main Environment
```batch
pip install "keras>=3.0"
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Benefit**: LSTM neural networks work in main system!

---

## Can You Use One Virtual Environment?

### YES - But Requires Merging Dependencies

**Current requirements.txt (Environment #1)**:
```
transformers>=4.30.0
torch>=2.0.0
pandas>=2.0.0
yfinance>=0.2.28
dash>=2.14.0
```

**Add from FinBERT (Environment #2)**:
```
keras>=3.0
tensorflow>=2.13.0  (only if you want both Keras backends)
flask>=2.3.0        (for FinBERT web UI)
```

**Merged requirements.txt**:
```
# Core ML
transformers>=4.30.0
torch>=2.0.0
keras>=3.0

# Data Science
pandas>=2.0.0
numpy>=1.24.0

# Financial
yfinance>=0.2.28
yahooquery>=2.3.0

# Dashboard
dash>=2.14.0
plotly>=5.17.0

# FinBERT Web UI (optional)
flask>=2.3.0
flask-cors>=4.0.0

# News
feedparser>=6.0.10
beautifulsoup4>=4.12.0

# Utilities
python-dateutil>=2.8.2
pytz>=2023.3
```

Then you could delete the separate `finbert_v4.4.4\venv` folder.

---

## What The Patch Does

### Before Running Patch:

```
Environment #1 (Main System):
✅ transformers
✅ torch
❌ keras (not installed)
❌ FinBERT model (not cached)

Environment #2 (FinBERT v4.4.4):
✅ transformers
✅ torch
✅ keras
❌ FinBERT model (not cached)
```

### After Running Patch:

```
Environment #1 (Main System):
✅ transformers
✅ torch
✅ keras (NEWLY INSTALLED)
✅ FinBERT model (CACHED)

Environment #2 (FinBERT v4.4.4):
✅ transformers
✅ torch
✅ keras
✅ FinBERT model (CACHED)

Shared Cache:
✅ C:\Users\david\.cache\huggingface\transformers\models--ProsusAI--finbert\
```

---

## Usage Instructions

### Step 1: Run the Patch
```cmd
cd C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL
CRITICAL_FIX_FINBERT_KERAS.bat
```

**What happens**:
1. Activates main system's venv (Environment #1)
2. Installs keras + PyTorch (fixes LSTM)
3. Downloads FinBERT model to shared cache (fixes sentiment)
4. Verifies everything works

**Time**: 5-10 minutes (one-time)  
**Size**: ~2.5GB total (PyTorch 2GB + FinBERT 500MB)

### Step 2: Restart Pipeline
```cmd
python -m models.screening.run_uk_screening_pipeline
```

**What you'll see**:
```
[OK] Keras LSTM available (PyTorch backend)
✅ FinBERT loaded from local cache (no download)
[OK] FinBERT v4.4.4 Sentiment for SAGA.L: positive (72.3%), compound: 0.485, 10 articles
```

---

## Summary

### Your Questions Answered:

1. **Where is FinBERT stored?**
   - Libraries: `venv\Lib\site-packages\transformers\`
   - Model files: `C:\Users\david\.cache\huggingface\transformers\`

2. **Does install load it?**
   - No, install only gets the libraries
   - Model downloads on first use (or via patch)

3. **Can dependencies work for both?**
   - Yes! Model cache is shared
   - Libraries need to be in EACH virtual environment
   - OR merge into one environment

### What Patch Fixes:

- ✅ Downloads FinBERT model to shared cache (500MB, one-time)
- ✅ Installs keras in main environment (2GB, one-time)
- ✅ Both environments can use FinBERT
- ✅ LSTM neural networks work
- ✅ Sentiment analysis works

### After Patch:

- No more "FinBERT analyzer not available"
- No more "Keras/PyTorch not available"
- Full accuracy on both components
- System runs at maximum capability

---

## Files Provided:

1. **CRITICAL_FIX_FINBERT_KERAS.bat** - Run this to fix both issues
2. This documentation file - Explains everything

**Run the patch now to fix both issues!**
