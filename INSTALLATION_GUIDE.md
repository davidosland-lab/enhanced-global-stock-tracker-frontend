# FinBERT v4.4.4 - Installation Guide

## Quick Answer: YES, You Need Dependencies!

**Minimum Installation** (Quick Scanner):
```bash
pip install yahooquery pandas numpy
```

**Full Installation** (LSTM + Sentiment):
```bash
pip install -r DEPLOYMENT_REQUIREMENTS.txt
```

---

## What You're Asking About

You're wondering if you can just download the ZIP and run it without installing anything.

**Short Answer**: **NO** - You need to install Python packages first.

**Why**: Python doesn't bundle dependencies in ZIP files like compiled programs do. Each package must be installed separately via `pip`.

---

## Two Installation Options

### Option 1: Quick Scanner Only ⚡ (RECOMMENDED TO START)

**What You Get**:
- Technical screening with yahooquery
- 5-10 minute runtime
- 90-100% success rate
- CSV output with scored stocks

**Installation** (~30 MB download):
```bash
pip install yahooquery pandas numpy
```

**Run**:
```bash
RUN_ALL_SECTORS_YAHOOQUERY.bat
```

**Output**:
```
screener_results_yahooquery_20251112_153045.csv
```

---

### Option 2: Full System 🚀 (LSTM + Sentiment)

**What You Get**:
- Everything from Option 1, PLUS:
- LSTM neural network predictions (45% weight)
- FinBERT sentiment analysis (15% weight)
- Trend analysis (25% weight)
- Technical analysis (15% weight)
- SPI 200 futures monitoring
- US market integration

**Installation** (~4 GB download):
```bash
pip install -r DEPLOYMENT_REQUIREMENTS.txt
```

**⚠️ WARNING**: This downloads TensorFlow (~500 MB) and PyTorch (~2 GB). Takes 10-30 minutes depending on internet speed.

**Run**:
```bash
RUN_OVERNIGHT_PIPELINE.bat
```

**Output**:
```
overnight_scan_results_TIMESTAMP.csv
predictions_TIMESTAMP.csv
opportunities_TIMESTAMP.csv
morning_report_TIMESTAMP.html
```

---

## Step-by-Step Installation

### Prerequisites

1. **Python 3.8+** installed
   - Check: `python --version`
   - Download: https://www.python.org/downloads/

2. **pip** working
   - Check: `pip --version`
   - Should come with Python

3. **Internet connection**
   - For downloading packages from PyPI

---

### Quick Scanner Installation (Recommended First)

```bash
# Step 1: Navigate to extracted folder
cd C:\path\to\extracted\FinBERT_FULL_SYSTEM

# Step 2: Install minimal dependencies
pip install yahooquery pandas numpy

# Step 3: Test installation
python test_integration_quick.py

# Step 4: Run scanner
RUN_ALL_SECTORS_YAHOOQUERY.bat
```

**Expected Output**:
```
✓ Loaded 8 sectors
✓ Scanning Financial sector...
✓ CBA.AX - Score: 85/100
✓ WBC.AX - Score: 80/100
✓ NAB.AX - Score: 75/100
✓ ANZ.AX - Score: 82/100
✓ MQG.AX - Score: 90/100
✓ Results saved to: screener_results_yahooquery_20251112_153045.csv
```

---

### Full System Installation (LSTM + Sentiment)

```bash
# Step 1: Navigate to extracted folder
cd C:\path\to\extracted\FinBERT_FULL_SYSTEM

# Step 2: Install ALL dependencies (this takes 10-30 minutes)
pip install -r DEPLOYMENT_REQUIREMENTS.txt

# Step 3: Verify installation
python -c "import yahooquery, tensorflow, transformers; print('All packages installed!')"

# Step 4: Run full pipeline
RUN_OVERNIGHT_PIPELINE.bat
```

**Expected Runtime**: 30-60 minutes (processes 240 stocks with ML predictions)

---

## Staged Installation (Recommended for Slow Connections)

If you have slow internet or want to test incrementally:

### Stage 1: Core (Required)
```bash
pip install yahooquery pandas numpy
# Test: python test_integration_quick.py
```

### Stage 2: Technical Analysis (Optional)
```bash
pip install yfinance requests ta python-dateutil pytz feedparser
# Enables: Enhanced data, technical indicators
```

### Stage 3: Machine Learning (Optional)
```bash
pip install tensorflow keras scikit-learn
# Enables: LSTM neural network predictions
```

### Stage 4: Sentiment Analysis (Optional)
```bash
pip install transformers torch
# Enables: FinBERT sentiment from news
```

---

## Verification Commands

### Check What's Installed
```bash
pip list | findstr "yahooquery pandas numpy tensorflow transformers"
```

### Test Quick Scanner
```bash
python test_integration_quick.py
```

**Expected Output**:
```
Testing yahooquery integration...
✓ yahooquery import successful
✓ StockScanner initialized
✓ Loaded 8 sectors
✓ Testing Financial sector scan...
✓ Processed 5 stocks in 47.2 seconds
✓ Success rate: 100.0%
✓ INTEGRATION TEST PASSED
```

### Test Full System Components
```bash
python -c "from finbert_v4.4.4.models.lstm_predictor import LSTMPredictor; print('LSTM: OK')"
python -c "from finbert_v4.4.4.models.finbert_sentiment import FinBERTSentiment; print('FinBERT: OK')"
```

---

## Troubleshooting

### "No module named 'yahooquery'"
**Problem**: Package not installed  
**Fix**: `pip install yahooquery`

### "pip is not recognized"
**Problem**: pip not in PATH  
**Fix**: `python -m pip install yahooquery`

### TensorFlow installation fails
**Problem**: Compatibility issues  
**Fix**: Try conda: `conda install tensorflow`

### PyTorch installation fails
**Problem**: Platform-specific build needed  
**Fix**: Visit https://pytorch.org and get custom install command

### Unicode errors on Windows
**Problem**: Console encoding issues  
**Fix**: Use `RUN_ALL_SECTORS_YAHOOQUERY_WINDOWS.bat` (ASCII version)

### "ImportError: DLL load failed" (Windows)
**Problem**: Missing Visual C++ Redistributable  
**Fix**: Download from https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## Package Sizes Reference

| Package | Size | Purpose |
|---------|------|---------|
| yahooquery | ~500 KB | Yahoo Finance data (PRIMARY) |
| pandas | ~10 MB | Data manipulation |
| numpy | ~20 MB | Numerical operations |
| yfinance | ~5 MB | Backup data source |
| ta | ~1 MB | Technical indicators |
| tensorflow | ~500 MB | LSTM neural network |
| torch | ~2 GB | PyTorch framework |
| transformers | ~1 GB | FinBERT sentiment |
| **Quick Scanner Total** | **~30 MB** | Option 1 |
| **Full System Total** | **~4 GB** | Option 2 |

---

## What Happens If You Don't Install?

If you try to run without installing dependencies:

```bash
python run_all_sectors_yahooquery.py
```

**You'll get**:
```
Traceback (most recent call last):
  File "run_all_sectors_yahooquery.py", line 8, in <module>
    from models.screening.stock_scanner import StockScanner
  File "models\screening\stock_scanner.py", line 12, in <module>
    from yahooquery import Ticker
ModuleNotFoundError: No module named 'yahooquery'
```

**Why**: Python can't find the packages because they're not installed.

---

## Summary

| Question | Answer |
|----------|--------|
| Do I need to install dependencies? | **YES** |
| Can I just run the ZIP? | **NO** - install packages first |
| What's the minimum I need? | yahooquery, pandas, numpy |
| How long does installation take? | 1-2 min (quick) or 10-30 min (full) |
| How much space? | ~30 MB (quick) or ~4 GB (full) |
| What if I skip ML packages? | Quick scanner still works |

---

## Recommended Workflow

1. **Install minimal packages** (1-2 minutes):
   ```bash
   pip install yahooquery pandas numpy
   ```

2. **Test quick scanner** (2 minutes):
   ```bash
   python test_integration_quick.py
   ```

3. **Run quick scan** (5-10 minutes):
   ```bash
   RUN_ALL_SECTORS_YAHOOQUERY.bat
   ```

4. **If satisfied, install ML packages** (10-30 minutes):
   ```bash
   pip install tensorflow keras transformers torch
   ```

5. **Run full pipeline** (30-60 minutes):
   ```bash
   RUN_OVERNIGHT_PIPELINE.bat
   ```

---

## Still Have Questions?

- Check: `DEPLOYMENT_REQUIREMENTS.txt` for detailed package info
- Read: `README_FULL_SYSTEM.md` for system architecture
- Review: `STOCK_ANALYSIS_EXPLAINED.md` for methodology
- Test: `python test_integration_quick.py` to verify setup
