# Quick Start Guide - v1.3.15.169

## 📋 After Extraction

You've successfully extracted the package. Here's what to do next:

---

## ✅ Step 1: Run the Test (Verify Installation)

```bash
cd "C:\Users\david\REgime trading V4 restored\unified_trading_system_v1.3.15.129_COMPLETE"
python test_lstm_model_loading.py
```

**Expected Output**:
```
ALL TESTS COMPLETED ✅
  ✓ Model loading logic implemented
  ✓ Registry structure validated
  ✓ _analyze_lstm flow working
  ✓ Format error fixes validated
```

**If tests fail**: Something went wrong during extraction. Re-extract the ZIP.

---

## ✅ Step 2: Run the Pipeline (Train LSTM Models)

### Option A: Run AU Market Pipeline (Recommended)

**Using Batch File** (Easiest):
```bash
cd pipelines
RUN_AU_PIPELINE.bat
```

**Using Python**:
```bash
cd "C:\Users\david\REgime trading V4 restored\unified_trading_system_v1.3.15.129_COMPLETE"
python pipelines/run_au_pipeline.py
```

### Option B: Run All Markets

```bash
cd pipelines
RUN_ALL_PIPELINES.bat
```

**This will**:
- Scan AU market (~150 stocks)
- Scan UK market (~100 stocks)
- Scan US market (~150 stocks)
- Total time: 2-3 hours

### What the Pipeline Does

1. **Scans Markets** (15-30 minutes per market)
   - Fetches stock data
   - Analyzes sentiment
   - Scores opportunities

2. **Trains LSTM Models** (20-40 minutes)
   - Selects top 20 stocks
   - Trains neural network models
   - **Saves models to `finbert_v4.4.4/models/saved_models/`**
   - **Creates registry: `lstm_models_registry.json`** ✨ NEW

3. **Generates Reports**
   - Morning report: `reports/screening/au_morning_report.json`
   - Summary statistics
   - Top opportunities

---

## ✅ Step 3: Verify Registry Created

After pipeline completes, check:

```bash
cd "C:\Users\david\REgime trading V4 restored\unified_trading_system_v1.3.15.129_COMPLETE"
dir finbert_v4.4.4\models\saved_models\
```

**Expected Files**:
```
lstm_models_registry.json  ← NEW (this is the key file!)
AAPL_lstm_model.h5
AAPL_lstm_scaler.pkl
GOOGL_lstm_model.h5
GOOGL_lstm_scaler.pkl
MSFT_lstm_model.h5
MSFT_lstm_scaler.pkl
... (up to 20 models)
```

**Check Registry Content**:
```bash
type finbert_v4.4.4\models\saved_models\lstm_models_registry.json
```

**Expected**:
```json
{
  "metadata": {
    "created_date": "2026-02-19 03:00:00",
    "total_models": 20
  },
  "models": {
    "GOOGL": {
      "model_path": "GOOGL_lstm_model.h5",
      "validation_accuracy": 0.74,
      ...
    }
  }
}
```

---

## ✅ Step 4: Start Dashboard

```bash
cd "C:\Users\david\REgime trading V4 restored\unified_trading_system_v1.3.15.129_COMPLETE"
python dashboard.py
```

**Expected Output**:
```
Dash is running on http://127.0.0.1:8050/
```

Open browser: `http://127.0.0.1:8050/`

---

## ✅ Step 5: Test Force BUY (Verify Fast Loading)

1. **In Dashboard**:
   - Load symbols: Click "📊 Auto-Load Top 50 from Pipeline Reports"
   - Set capital: $100,000
   - Click "▶ Start Trading"

2. **Force BUY a Trained Stock**:
   - Enter symbol: `GOOGL`
   - Click "🔥 Force BUY"

3. **Check Logs** (terminal running dashboard):

   **BEFORE v169** (OLD):
   ```
   WARNING - Insufficient data to train LSTM for GOOGL
   [Training LSTM model...] (30-60 seconds)
   Signal GOOGL: SELL (conf=0.54)
   ```

   **AFTER v169** (NEW):
   ```
   [LOADED] ✓ LSTM model for GOOGL (trained 2026-02-19, acc=0.74)
   Signal GOOGL: BUY (conf=0.74)
   [ENTRY] GOOGL: Entry allowed (conf=74%)
   ```

   **Time**: <1 second (instead of 30-60 seconds) ✅

---

## ⚠️ Common Issues

### Issue 1: "File not found: overnight_scan_AU.py"

**Cause**: Wrong filename (doesn't exist)

**Fix**: Use correct command:
```bash
python pipelines/run_au_pipeline.py
```

**OR**:
```bash
cd pipelines
RUN_AU_PIPELINE.bat
```

---

### Issue 2: "Registry not found"

**Symptom**:
```
[LOAD] Registry not found at .../lstm_models_registry.json
```

**Cause**: Pipeline hasn't been run yet

**Fix**: Run pipeline first (Step 2)

---

### Issue 3: "Still training models in dashboard"

**Symptom**:
```
[TRAIN] No pre-trained model for TSLA, training from scratch...
```

**Cause**: TSLA wasn't in top 20 trained by pipeline

**Expected Behavior**: System falls back to training (this is correct)

**Solution**: Force BUY on stocks trained by pipeline (check registry for list)

---

## 📊 File Locations Reference

| File | Location |
|------|----------|
| **Pipeline Scripts** | `pipelines/run_au_pipeline.py` |
| **Batch Files** | `pipelines/RUN_AU_PIPELINE.bat` |
| **LSTM Models** | `finbert_v4.4.4/models/saved_models/*.h5` |
| **Registry** | `finbert_v4.4.4/models/saved_models/lstm_models_registry.json` |
| **Reports** | `reports/screening/au_morning_report.json` |
| **Dashboard** | `dashboard.py` |
| **Test Script** | `test_lstm_model_loading.py` |

---

## 🎯 Verification Checklist

After installation, verify:

- [x] Test script passes all tests
- [ ] Pipeline completes without errors
- [ ] Registry file created (20 models)
- [ ] Dashboard starts successfully
- [ ] Auto-load shows stocks
- [ ] Force BUY shows "[LOADED] ✓" in logs
- [ ] No "Insufficient data" warnings
- [ ] Response time <1 second

---

## 🚀 Quick Command Reference

```bash
# Navigate to installation
cd "C:\Users\david\REgime trading V4 restored\unified_trading_system_v1.3.15.129_COMPLETE"

# Test installation
python test_lstm_model_loading.py

# Run AU pipeline (train models)
python pipelines/run_au_pipeline.py

# Start dashboard
python dashboard.py

# View registry
type finbert_v4.4.4\models\saved_models\lstm_models_registry.json

# Check logs
type logs\unified_trading.log | findstr LOADED
```

---

## 📞 If You Get Stuck

**Check**:
1. Test passes? → Installation OK
2. Pipeline runs? → Models training
3. Registry exists? → Models saved
4. Dashboard starts? → Ready to trade
5. Force BUY fast? → Fix working!

**Still having issues?** Share the exact error message and I'll help debug.

---

*Quick Start Guide v1.3.15.169*  
*Last Updated: 2026-02-19*
