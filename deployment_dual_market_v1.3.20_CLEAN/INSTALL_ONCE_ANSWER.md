# Do I Only Need to Run INSTALL.bat Once for Both Systems?

## ✅ YES - Run INSTALL.bat ONLY ONCE!

### Short Answer

**YES!** The main `INSTALL.bat` in the root directory installs ALL dependencies for BOTH systems:
- ✅ **ASX Market Pipeline** (`overnight_pipeline.py`)
- ✅ **US Market Pipeline** (`us_overnight_pipeline.py`)

**You run it ONCE, and both systems are ready!**

---

## Understanding "Two Systems"

Your deployment has **TWO MARKET PIPELINES** that share the same installation:

### 1. **ASX Market Pipeline** (Australian Stocks)
- **File:** `models/screening/overnight_pipeline.py`
- **Stocks:** 139 ASX stocks (BHP.AX, CBA.AX, etc.)
- **Run:** Typically at 3:00 AM AEST after market close

### 2. **US Market Pipeline** (American Stocks)
- **File:** `models/screening/us_overnight_pipeline.py`
- **Stocks:** US market stocks (AAPL, MSFT, etc.)
- **Run:** After US market hours

### Shared Infrastructure
Both pipelines use:
- ✅ Same Python packages (PyTorch, TensorFlow, yfinance)
- ✅ Same `finbert_v4.4.4` module (LSTM + sentiment)
- ✅ Same dependencies (installed by ONE `INSTALL.bat`)
- ✅ Same config directory structure

---

## Installation Flow

```
C:\Users\david\AATelS\
│
├─ INSTALL.bat                    ← RUN THIS ONCE!
│  │
│  ├─> Installs PyTorch (~1-2 GB)
│  ├─> Installs TensorFlow (~400-500 MB)
│  ├─> Installs all shared dependencies
│  └─> Creates directory structure
│
├─ models/screening/
│  ├─ overnight_pipeline.py      ← ASX system (uses installed packages)
│  └─ us_overnight_pipeline.py   ← US system (uses SAME packages)
│
└─ finbert_v4.4.4/               ← Shared by both systems
   └─ models/
      ├─ train_lstm.py
      └─ lstm_predictor.py
```

---

## What INSTALL.bat Does (Once for All)

### Step 1: Check Python
- Verifies Python 3.8+ is installed

### Step 2: Upgrade pip
- Ensures latest package manager

### Step 3: Install yahooquery
- Handles lxml dependency first

### Step 4: Install from requirements.txt
This installs **EVERYTHING** both systems need:
- ✅ **PyTorch** (~1-2 GB) - FinBERT sentiment for ASX + US
- ✅ **Transformers** - FinBERT models for ASX + US
- ✅ **TensorFlow** (~400-500 MB) - LSTM training for ASX + US
- ✅ **Keras** - LSTM API for ASX + US
- ✅ **yfinance** - Data fetching for ASX + US
- ✅ **yahooquery** - Fallback data for ASX + US
- ✅ **pandas, numpy** - Data processing for ASX + US
- ✅ **ta** - Technical analysis for ASX + US
- ✅ **scikit-learn** - ML utilities for ASX + US

### Step 5: Verify Installation
- Checks all packages are working
- Shows green ✓ for each component

### Step 6: Create Directories
- Creates `models/screening/logs/`
- Creates `results/`
- Creates `data/`

**Total Time:** 5-15 minutes  
**Total Download:** ~2-2.5 GB  
**Run Frequency:** ONCE!

---

## When Do You Need to Run Installation Again?

### ❌ You DON'T need to reinstall when:
- Switching between ASX and US pipelines
- Running both pipelines on the same day
- Updating config files (screening_config.json)
- Downloading fixed finbert_v4.4.4 files (Keras 3 fix)
- Training new models

### ✅ You DO need to reinstall when:
- Moving to a different computer
- Creating a new Python virtual environment
- Package corruption occurs
- Major version upgrade (e.g., v1.3.20 → v2.0.0)

---

## After Installation: Running Both Systems

### Option 1: Run ASX Pipeline
```cmd
cd models\screening
python overnight_pipeline.py
```

### Option 2: Run US Pipeline
```cmd
cd models\screening
python us_overnight_pipeline.py
```

### Option 3: Run Both Sequentially
```cmd
cd models\screening
python overnight_pipeline.py
python us_overnight_pipeline.py
```

**No reinstallation needed between runs!**

---

## Patch Files (Separate from INSTALL.bat)

You have several patch directories, each with their own `install.bat`:

```
deployment_dual_market_v1.3.20_CLEAN/
│
├─ INSTALL.bat                           ← MAIN: Run ONCE for base system
│
├─ KERAS3_MODEL_FIX_PATCH/
│  └─ install_keras_fix.bat             ← Optional: Only if Keras 3 issues
│
├─ FINBERT_UPGRADE_PATCH/
│  └─ INSTALL.bat                        ← Optional: FinBERT upgrades
│
├─ MACRO_NEWS_STANDALONE_PATCH/
│  └─ install.bat                        ← Optional: Macro news feature
│
└─ TELEGRAM_FIX_COMPLETE/
   └─ install.bat                        ← Optional: Telegram notifications
```

### Patch Installation Order

1. **First:** Run main `INSTALL.bat` (root directory) - **REQUIRED**
2. **Then (optional):** Run specific patch installers if needed

**Each patch installer is INDEPENDENT and can be run separately.**

---

## Example Installation Session

### First Time Setup (Run ONCE):

```cmd
C:\Users\david\AATelS>

Step 1: Main Installation
-------------------------
INSTALL.bat
[Wait 5-15 minutes]
✓ Installation successful!

Step 2: Verify Installation
---------------------------
VERIFY_INSTALLATION.bat
✓ All 5 core packages verified!

Step 3a: Apply Keras 3 Fix (if needed)
--------------------------------------
cd KERAS3_MODEL_FIX_PATCH
install_keras_fix.bat
[2 minutes]
✓ Keras 3 fix applied!

Step 3b: Download Fixed Files from GenSpark
-------------------------------------------
[Download lstm_predictor.py and train_lstm.py]
[Copy to finbert_v4.4.4\models\]
✓ Symbol-specific model saving enabled!

Done! Both ASX and US systems ready!
```

### Daily Operation (No Reinstall):

```cmd
C:\Users\david\AATelS>

Morning: Run ASX Pipeline
-------------------------
cd models\screening
python overnight_pipeline.py
[Runs for 2-4 hours]
✓ ASX analysis complete!

Evening: Run US Pipeline
------------------------
python us_overnight_pipeline.py
[Runs for 2-4 hours]
✓ US analysis complete!

No reinstallation needed!
```

---

## Common Misconceptions

### ❌ Misconception 1:
"I need to run INSTALL.bat before each pipeline run"
- **Reality:** NO! Install once, run pipelines forever

### ❌ Misconception 2:
"ASX and US systems need separate installations"
- **Reality:** NO! They share the same Python packages

### ❌ Misconception 3:
"Patch installers replace the main INSTALL.bat"
- **Reality:** NO! Patches are ADDITIONS to the base install

### ❌ Misconception 4:
"I need to reinstall when downloading Keras 3 fix files"
- **Reality:** NO! Just download and copy the 2 Python files

---

## Verification After Installation

### Check Both Systems Work:

```cmd
# Test ASX Pipeline
cd models\screening
python overnight_pipeline.py --test
# Should complete in ~15 minutes with 10 stocks

# Test US Pipeline  
python us_overnight_pipeline.py --test
# Should complete in ~15 minutes with 10 stocks
```

If BOTH complete successfully → Installation worked for BOTH systems!

---

## Directory Structure After Installation

```
C:\Users\david\AATelS\
│
├─ finbert_v4.4.4/                      ← Shared LSTM + sentiment
│  └─ models/                              (used by ASX + US)
│     ├─ lstm_predictor.py
│     ├─ train_lstm.py
│     └─ finbert_sentiment.py
│
├─ models/screening/
│  ├─ overnight_pipeline.py             ← ASX system
│  ├─ us_overnight_pipeline.py          ← US system
│  ├─ lstm_trainer.py                   ← Shared trainer
│  ├─ batch_predictor.py                ← Shared predictor
│  └─ models/                           ← Shared model storage
│     ├─ BHP.AX_lstm_model.keras       (ASX models)
│     └─ AAPL_lstm_model.keras         (US models)
│
└─ venv/ (if using virtual environment)
   └─ Lib/site-packages/               ← ALL packages here
      ├─ torch/                           (shared by ASX + US)
      ├─ tensorflow/                      (shared by ASX + US)
      ├─ transformers/                    (shared by ASX + US)
      └─ ...                              (all shared)
```

**One installation → Everything shared → Both systems work!**

---

## Summary

### ✅ DO THIS:
1. Run `INSTALL.bat` **ONCE** from root directory
2. Run `VERIFY_INSTALLATION.bat` to confirm
3. (Optional) Apply patches if needed
4. Download Keras 3 fix files from GenSpark
5. Run ASX and US pipelines as needed

### ❌ DON'T DO THIS:
1. Don't run `INSTALL.bat` before each pipeline run
2. Don't install packages separately for ASX and US
3. Don't think patches replace the main installation
4. Don't reinstall when switching pipelines

---

## Bottom Line

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  ONE INSTALL.bat                                        │
│  ↓                                                       │
│  ALL Python Packages                                    │
│  ↓                                                       │
│  BOTH Systems Ready:                                    │
│    ├─ ASX Pipeline ✓                                   │
│    └─ US Pipeline ✓                                    │
│                                                          │
│  Run INSTALL.bat ONCE                                   │
│  Use both pipelines FOREVER                             │
│  (until you change computers or environments)           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Created:** 2024-12-02  
**Purpose:** Clarify that INSTALL.bat runs ONCE for BOTH ASX and US systems  
**Status:** ✅ One installation, two market pipelines, infinite runs!
