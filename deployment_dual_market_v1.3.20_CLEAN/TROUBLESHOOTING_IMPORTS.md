# Troubleshooting Import Errors

## Common Error: "No module named 'finbert_sentiment'"

### Symptoms
```
WARNING - ⚠ LSTM predictor not available: No module named 'lstm_predictor'
WARNING - ⚠ FinBERT sentiment analyzer not available: No module named 'finbert_sentiment'
WARNING - ⚠ News sentiment module not available: No module named 'news_sentiment_real'
```

### Root Cause
These warnings occur when the FinBERT v4.4.4 integration is not present. **This is NORMAL and EXPECTED** in the standalone deployment package.

### Why These Are Optional
The system has **two modes**:

#### Mode 1: Standalone (Current Package) - ✅ FULLY FUNCTIONAL
- Uses built-in LSTM and sentiment analysis
- Does not require FinBERT v4.4.4 directory
- **All features work without these modules**
- Warnings can be safely ignored

#### Mode 2: With FinBERT Integration (Advanced)
- Requires separate FinBERT v4.4.4 package
- Provides enhanced sentiment analysis
- Optional upgrade

---

## What Should Work Out of the Box

### ✅ Core Features (No Warnings)
- Stock scanning (ASX + US)
- Market regime detection
- Volatility analysis  
- Technical indicators
- Opportunity scoring
- HTML report generation
- Web UI dashboard

### ⚠️ Optional Features (Warnings Expected)
- FinBERT sentiment analysis (requires separate package)
- Advanced LSTM predictions (uses built-in version)
- News sentiment (uses basic version)

---

## How to Verify Installation

### Run Diagnostic Check
```cmd
CHECK_INSTALLATION.bat
```

Expected output:
```
OK: pandas
OK: numpy
OK: yfinance
OK: yahooquery
OK: flask
OK: scikit-learn
OK: tensorflow
OK: transformers
OK: torch
OK: hmmlearn (optional)
OK: ASX Pipeline
OK: US Pipeline
WARNING: FinBERT Sentiment (optional) ← THIS IS NORMAL
WARNING: LSTM Predictor (optional) ← THIS IS NORMAL
```

---

## Real Errors vs. Expected Warnings

### ❌ REAL ERROR (Needs Fixing)
```
ERROR: Failed to import ASX Pipeline
ERROR: Failed to import US Pipeline
MISSING: pandas
MISSING: numpy
MISSING: yahooquery
```

**Solution:** Run `INSTALL.bat` again

---

### ⚠️ EXPECTED WARNING (Can Ignore)
```
WARNING - ⚠ FinBERT path not found: C:\...\finbert_v4.4.4
WARNING - ⚠ LSTM predictor not available: No module named 'lstm_predictor'
WARNING - ⚠ FinBERT sentiment analyzer not available
```

**This is normal!** The system will use built-in alternatives.

---

## If Dependencies Actually Failed to Install

### Symptom
```
ERROR: Failed to install dependencies
```

### Solutions

#### Solution 1: Upgrade pip
```cmd
python -m pip install --upgrade pip
```

#### Solution 2: Clear cache and retry
```cmd
pip install -r requirements.txt --no-cache-dir
```

#### Solution 3: Install packages individually
```cmd
pip install pandas numpy yahooquery yfinance
pip install flask flask-cors
pip install scikit-learn scipy
pip install tensorflow transformers torch
pip install hmmlearn ta pytz
```

#### Solution 4: Use conda (alternative)
```cmd
conda install pandas numpy scikit-learn scipy
pip install yahooquery yfinance flask flask-cors
pip install tensorflow transformers torch hmmlearn
```

---

## Testing After Installation

### Quick Test (30 seconds)
```cmd
python setup_paths.py
```

Expected: Should show paths added successfully

### Pipeline Test (3-5 minutes)
```cmd
python run_screening.py --market us --stocks 5
```

Expected: Should complete with "Pipeline completed successfully"

---

## Understanding the Architecture

### Import Path Setup
The system uses `setup_paths.py` to ensure imports work:

```python
# File: setup_paths.py
import sys
from pathlib import Path

INSTALL_DIR = Path(__file__).parent.resolve()

sys.path.insert(0, str(INSTALL_DIR))
sys.path.insert(0, str(INSTALL_DIR / 'models'))
sys.path.insert(0, str(INSTALL_DIR / 'models' / 'screening'))
```

### All scripts import this first:
```python
import setup_paths  # Sets up paths
from models.screening.overnight_pipeline import OvernightPipeline  # Now works!
```

---

## Windows-Specific Issues

### Issue: "Python is not recognized"
**Solution:** Add Python to PATH
1. Search "Environment Variables"
2. Edit System PATH
3. Add: `C:\Python312\` and `C:\Python312\Scripts\`

### Issue: Long path names on Windows
**Solution:** Enable long paths
1. Run: `regedit`
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Set `LongPathsEnabled` = 1

---

## Still Having Issues?

### Get Detailed Diagnostics
```cmd
python -c "import sys; print('\n'.join(sys.path))"
```

This shows all Python import paths.

### Check What's Actually Installed
```cmd
pip list | findstr "pandas numpy yahoo flask scikit tensor torch"
```

### Get Help
1. Run `CHECK_INSTALLATION.bat` and save output
2. Include output when reporting issues
3. Check `logs/screening/launcher.log` for detailed errors

---

## Summary

**Remember:** Warnings about FinBERT modules are **NORMAL** and **EXPECTED**.

The system is designed to work without them using built-in alternatives.

Only investigate if:
- ✅ Pipelines fail to run
- ✅ Core packages (pandas, numpy, yahooquery) are missing
- ✅ Import errors for OvernightPipeline or USOvernightPipeline

Ignore warnings if:
- ⚠️ FinBERT v4.4.4 not found
- ⚠️ Optional LSTM modules not available
- ⚠️ Advanced sentiment modules not available

**The system is fully functional with just the core dependencies!**
