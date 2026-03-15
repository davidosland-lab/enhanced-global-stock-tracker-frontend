# QUICKSTART GUIDE - Patch v1.3.15.45

**⏱️ Total Time**: ~10-15 minutes  
**💾 Required Space**: ~500 MB (for FinBERT model)

---

## 🚀 5-Minute Installation

### Step 1: Extract Patch (30 seconds)

Extract `COMPLETE_PATCH_v1.3.15.45_FINAL.zip` to any location:

```
Example: C:\Users\david\Downloads\COMPLETE_PATCH_v1.3.15.45_FINAL\
```

### Step 2: Run Installer (5-10 minutes)

Double-click: **`INSTALL_PATCH.bat`**

When prompted:

1. **Choose installation method**:
   ```
   Enter choice (1 or 2): 1
   ```
   _(Press 1 for Virtual Environment - RECOMMENDED)_

2. **Enter installation directory** (or press Enter for default):
   ```
   C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15
   ```

3. **Wait for installation**:
   - Installing dependencies... (~2-3 minutes)
   - Downloading FinBERT model... (~2-5 minutes, ~500 MB)
   - Running tests... (~30 seconds)

4. **Verify tests passed**:
   ```
   ALL TESTS PASSED (6/6) ✅
   ```

### Step 3: Activate Virtual Environment

```cmd
cd C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15
venv\Scripts\activate
```

You'll see: `(venv)` in your prompt

---

## ▶️ First Run

### Run Overnight Pipeline (15-20 minutes)

Generate morning report with FinBERT sentiment:

```cmd
python run_au_pipeline_v1.3.13.py --full-scan --capital 100000
```

**What it does**:
- Scans 240 ASX stocks
- Analyzes sentiment with FinBERT v4.4.4
- Generates morning report with sentiment breakdown

**Expected output**:
```
Pipeline complete: 141 stocks processed
✓ Morning report: reports\screening\au_morning_report.json
✓ FinBERT sentiment: 85 stocks analyzed
```

### Start Dashboard

```cmd
python unified_trading_dashboard.py
```

**Navigate to**: http://localhost:8050

---

## ✅ Verify Installation

### Quick Test:

```cmd
python test_finbert_integration.py
```

**Expected**: `ALL TESTS PASSED (6/6) ✅`

### Check Morning Report:

```cmd
type reports\screening\au_morning_report.json
```

Look for `finbert_sentiment` section with real sentiment data.

---

## 🎯 What You Should See

### Morning Report Example:

```json
"finbert_sentiment": {
  "overall_scores": {
    "avg_negative": 0.42,
    "avg_neutral": 0.31,
    "avg_positive": 0.27,
    "avg_compound": -0.15
  },
  "dominant_sentiment": "negative",
  "count": 85
}
```

### Dashboard View:

1. **FinBERT Sentiment Panel** (top right):
   - Negative bar: 42% (Red)
   - Neutral bar: 31% (Gray)
   - Positive bar: 27% (Green)

2. **Trading Gate Status**:
   - Gate: **REDUCE** (0.5x)
   - Reason: "Negative sentiment 40-50%"
   - Indicator: 🟡 Yellow

---

## 🛡️ Trading Gates Explained

### Sentiment-Based Position Sizing:

| Negative % | Gate | Position Size | Trading |
|------------|------|---------------|---------|
| **> 50%** | **BLOCK** | 0.0x | 🚫 NO TRADES |
| **40-50%** | **REDUCE** | 0.5x | Half positions |
| **30-40%** | **CAUTION** | 0.8x | Smaller positions |
| **< 30%** | **ALLOW** | 1.0x | Normal trading |

### Positive Boost:

| Positive % | Position Size |
|------------|---------------|
| **> 60%** | 1.2x (boosted) |

### Example:

**Scenario**: FinBERT sentiment = 65% Negative

- **Before Patch**: ❌ Platform still trades (WRONG!)
- **After Patch**: ✅ **BLOCK gate** - NO TRADES (CORRECT!)

---

## 🔄 Daily Workflow

### Morning (Before Market Open):

```cmd
# Activate virtual environment
venv\Scripts\activate

# Run overnight pipeline
python run_au_pipeline_v1.3.13.py --full-scan --capital 100000
```

### During Trading:

```cmd
# Start dashboard
python unified_trading_dashboard.py

# Navigate to: http://localhost:8050
```

### After Trading:

```cmd
# Review trades
python paper_trading_coordinator.py --symbols <your_symbols> --capital 100000

# Deactivate virtual environment
deactivate
```

---

## 🐛 Common Issues

### Issue: "No module named 'transformers'"

**Quick Fix**:
```cmd
venv\Scripts\activate
python -m pip install transformers torch
```

### Issue: Tests fail with "No morning report found"

**Quick Fix**: Run overnight pipeline first (see above)

### Issue: Virtual environment not activated

**Symptom**: Commands fail or use wrong Python

**Quick Fix**:
```cmd
cd C:\Users\david\Regime_trading\complete_backend_clean_install_v1.3.15
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### Issue: FinBERT model download interrupted

**Quick Fix**:
```python
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('ProsusAI/finbert'); AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert'); print('Model downloaded successfully')"
```

---

## 📋 Checklist

Quick verification checklist:

- [x] Patch extracted
- [x] INSTALL_PATCH.bat executed
- [x] Virtual environment activated
- [x] Tests passed (6/6)
- [x] Overnight pipeline run
- [x] Morning report contains `finbert_sentiment`
- [x] Dashboard accessible
- [x] FinBERT sentiment panel visible
- [x] Trading gates working

---

## 🎯 Key Takeaways

1. **Always activate virtual environment** before running scripts:
   ```cmd
   venv\Scripts\activate
   ```

2. **Run overnight pipeline** to generate morning report with sentiment

3. **Check dashboard** for real-time FinBERT sentiment and trading gates

4. **Trading is blocked** when sentiment is negative (> 50%)

5. **Position sizes are adjusted** based on sentiment (REDUCE, CAUTION, ALLOW)

---

## 📖 Further Reading

- **Full Documentation**: `README.md`
- **Technical Details**: `FINBERT_SENTIMENT_INTEGRATION_v1.3.15.45.md`
- **Integration Plan**: `UNIFIED_FINBERT_INTEGRATION_PLAN.md`
- **Analysis**: `FINBERT_SENTIMENT_INTEGRATION_ANALYSIS.md`

---

## 🆘 Need Help?

1. **Check logs**:
   - `logs/au_pipeline.log`
   - `logs/paper_trading.log`

2. **Run diagnostics**:
   ```cmd
   python test_finbert_integration.py
   ```

3. **Verify FinBERT**:
   ```cmd
   python -c "from models.screening.finbert_bridge import get_finbert_bridge; print(get_finbert_bridge().is_available())"
   ```

---

**🎉 You're ready to trade with sentiment-aware position sizing! 🚀**
