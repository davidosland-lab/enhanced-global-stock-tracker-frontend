# Event Risk Guard v1.3.20
## Market Regime Engine Configuration Fix

---

## 🚨 WHAT'S NEW IN v1.3.20

### Critical Configuration Fix
**ENABLED Market Regime Engine** in screening_config.json - was showing "DISABLED" during test runs.

**Configuration Added:**
```json
"regime_detector": {
  "enabled": true,
  "min_history_days": 252,
  "n_states": 3,
  "state_names": ["CALM", "NORMAL", "HIGH_VOL"],
  "risk_multipliers": {
    "CALM": 0.7,
    "NORMAL": 1.0,
    "HIGH_VOL": 1.5
  }
}
```

**Impact:** Regime engine now classifies market states and adjusts crash risk accordingly.

---

## 📋 QUICK START

### Windows (Recommended)
```cmd
1. Extract event_risk_guard_v1.3.20_COMPLETE.zip
2. Double-click INSTALL.bat (wait 5-15 minutes)
3. Double-click VERIFY_INSTALLATION.bat
4. Test run: Double-click RUN_PIPELINE_TEST.bat
5. Full run: Double-click RUN_PIPELINE.bat
6. View reports: Double-click START_WEB_UI.bat
```

### Linux/Mac
```bash
1. Extract event_risk_guard_v1.3.20_COMPLETE.zip
2. chmod +x install.sh verify_installation.sh run_pipeline_test.sh
3. ./install.sh
4. ./verify_installation.sh
5. Test run: ./run_pipeline_test.sh
6. Full run: ./run_pipeline.sh
```

---

## 📂 WHAT'S INCLUDED

### Core Files
- `models/` - All screening, prediction, and training modules
  - `screening/overnight_pipeline.py` - Main pipeline with PHASE 4.5 LSTM training
  - `screening/event_risk_guard.py` - Event risk + Regime-aware crash risk
  - `screening/market_regime_engine.py` - HMM-based market state classification
  - `screening/finbert_bridge.py` - FinBERT integration adapter
  - `screening/lstm_trainer.py` - LSTM model training orchestrator
  - `screening/regime_detector.py` - 3-state regime detection
  - `config/screening_config.json` - **UPDATED: Regime detector enabled**

- `finbert_v4.4.4/` - FinBERT components with proper package structure
  - `models/lstm_predictor.py` - LSTM prediction models
  - `models/finbert_sentiment.py` - FinBERT sentiment analyzer
  - `models/news_sentiment_real.py` - News scraping + sentiment
  - `models/train_lstm.py` - LSTM training implementation
  - `__init__.py` - Package structure file
  - `models/__init__.py` - Subpackage structure file

### Installation & Execution
- `INSTALL.bat` / `install.sh` - User package installation (no venv)
- `RUN_PIPELINE.bat` / `run_pipeline.sh` - Production run
- `RUN_PIPELINE_TEST.bat` / `run_pipeline_test.sh` - Test mode (--mode test)
- `START_WEB_UI.bat` - Launch web UI for viewing reports
- `VERIFY_INSTALLATION.py` - 5 critical checks
- `VERIFY_INSTALLATION.bat` / `verify_installation.sh` - Verification wrapper
- `requirements.txt` - Python dependencies

### Web UI & Reports
- `web_ui.py` - Flask web interface for viewing reports
- `models/screening/reports/morning_reports/` - HTML reports with charts
- Access at: http://localhost:5000 after running START_WEB_UI.bat

### Monitoring
- `CHECK_LOGS.bat` - Quick log viewer
- Logs: `models/screening/logs/overnight_screening_YYYYMMDD.log`

---

## 🔍 VERIFICATION CHECKLIST

Run `VERIFY_INSTALLATION.bat` (Windows) or `./verify_installation.sh` (Linux/Mac).

**Look for 5 green checkmarks:**
```
✓ FinBERT Package Structure: PASS
✓ FinBERT Bridge Integration: PASS
✓ LSTM Training (PHASE 4.5): PASS
✓ Market Regime Engine: PASS
✓ Event Risk Guard Integration: PASS
```

---

## 🏃 RUNNING THE PIPELINE

### Test Mode (Recommended First)
Processes 10 stocks (~15 minutes)
```cmd
Double-click: RUN_PIPELINE_TEST.bat
```

Or manually:
```cmd
cd models\screening
python overnight_pipeline.py --mode test
```

### Full Mode
Processes 240 stocks (~4 hours)
```cmd
Double-click: RUN_PIPELINE.bat
```

Or manually:
```cmd
cd models\screening
python overnight_pipeline.py
```

### View Reports
```cmd
Double-click: START_WEB_UI.bat
Then open: http://localhost:5000
```

---

## ✅ WHAT TO EXPECT

### PHASE 2.5: Event Risk Assessment (NOW WITH REGIME ENGINE!)
```
PHASE 2.5: EVENT RISK ASSESSMENT
Market Regime Engine: HIGH_VOL (enabled)
Crash Risk Multiplier: 1.5
Adjusted Crash Risk: 0.588
```

**Previously showed:**
```
Market Regime Engine: DISABLED. Enable the regime engine
```

### PHASE 4.5: LSTM Model Training
```
PHASE 4.5: LSTM MODEL TRAINING
✓ AZJ.AX: Training completed in 45.2s
✓ CQR.AX: Training completed in 38.7s
...
Trained: 85/100
Failed: 15/100
Success Rate: 85.0%
```

### PHASE 5: Batch Prediction (Sentiment)
```
✓ Sentiment for CQR.AX: positive (75.3%), 12 articles
✓ Sentiment for AZJ.AX: negative (65.1%), 8 articles
```

### Final Report
- HTML report generated in: `models/screening/reports/morning_reports/`
- CSV export available
- View in web UI at: http://localhost:5000

---

## 🌐 WEB UI FEATURES

After running `START_WEB_UI.bat`:

1. **Dashboard**: Overview of latest screening results
2. **Stock Details**: Individual stock analysis with charts
3. **Reports Archive**: Historical screening reports
4. **Regime Analysis**: Market state visualization
5. **Model Performance**: LSTM training success rates

Access at: **http://localhost:5000**

---

## 🐛 TROUBLESHOOTING

### "Market Regime Engine: DISABLED" Message
**Solution:** Use v1.3.20 - this version enables the regime detector in config.

### Import Errors: "No module named 'models.finbert_sentiment'"
**Solution:**
1. Verify `finbert_v4.4.4/__init__.py` exists
2. Verify `finbert_v4.4.4/models/__init__.py` exists
3. Extract complete v1.3.20 ZIP (don't mix versions)

### INSTALL.bat Hangs
**Solution:**
1. Check internet connection (downloads PyTorch, TensorFlow)
2. Wait 5-15 minutes - installation is slow but shows progress
3. DON'T close window if you see package names scrolling

### No Reports Generated
**Solution:**
1. Check logs: `CHECK_LOGS.bat`
2. Ensure pipeline completed all phases
3. Check: `models/screening/reports/morning_reports/` directory
4. Run `START_WEB_UI.bat` to view reports

---

## 📊 OUTPUT FILES

### Reports
- `models/screening/reports/morning_reports/YYYY-MM-DD_market_report.html`
- `models/screening/reports/morning_reports/YYYY-MM-DD_data.json`

### Results
- `results/overnight_screening_results_YYYYMMDD.csv` - Scored stocks

### Logs
- `models/screening/logs/overnight_screening_YYYYMMDD.log`

### Trained Models
- `finbert_v4.4.4/models/lstm_models/[SYMBOL]_lstm_model.h5`
- `finbert_v4.4.4/models/[SYMBOL]_lstm_metadata.json`

---

## 🔧 CONFIGURATION

Edit `models/config/screening_config.json`:

### LSTM Training
```json
{
  "lstm_training": {
    "enabled": true,
    "max_models_per_night": 100,
    "stale_threshold_days": 7,
    "epochs": 50
  }
}
```

### Regime Detector (NEW IN v1.3.20)
```json
{
  "regime_detector": {
    "enabled": true,
    "min_history_days": 252,
    "n_states": 3,
    "state_names": ["CALM", "NORMAL", "HIGH_VOL"],
    "risk_multipliers": {
      "CALM": 0.7,
      "NORMAL": 1.0,
      "HIGH_VOL": 1.5
    }
  }
}
```

### FinBERT Integration
```json
{
  "finbert_integration": {
    "enabled": true,
    "components": {
      "lstm_prediction": {"enabled": true},
      "sentiment_analysis": {"enabled": true},
      "news_scraping": {"enabled": true}
    }
  }
}
```

---

## 🔄 VERSION HISTORY

### v1.3.20 (Current - 2025-11-20)
- ✅ **ENABLED:** Market Regime Engine in configuration
- ✅ Added regime_detector config section
- ✅ Regime-aware crash risk assessment now functional
- ✅ Added START_WEB_UI.bat for easy report viewing

### v1.3.19 (2025-11-20)
- ✅ Fixed --mode test argument (was --test)
- ✅ RUN_PIPELINE_TEST.bat now works correctly

### v1.3.18 (2025-11-20)
- ✅ Created RUN_PIPELINE.bat and RUN_PIPELINE_TEST.bat
- ✅ Added Linux shell script equivalents

### v1.3.17 (2025-11-20)
- ✅ Added get_trained_models_count() to finbert_bridge.py

### v1.3.16 (2025-11-20)
- ✅ Fixed INSTALL.bat (user packages, no venv)
- ✅ Restored PHASE 4.5 LSTM training
- ✅ Integrated Market Regime Engine into event_risk_guard.py

### v1.3.15 (2025-11-20)
- ✅ Added __init__.py files for proper package structure
- ✅ Fixed sentiment analysis import errors
- ✅ Fixed LSTM training import errors

---

## 💡 TIPS

1. **Always verify first:** `VERIFY_INSTALLATION.bat` must show 5 green checks
2. **Test before full run:** `RUN_PIPELINE_TEST.bat` (10 stocks, 15 minutes)
3. **View reports in browser:** `START_WEB_UI.bat` → http://localhost:5000
4. **Check logs:** `CHECK_LOGS.bat` for troubleshooting
5. **Some failures are normal:** Rate limits, insufficient data expected

---

## 🆘 SUPPORT

If you encounter issues:
1. Run `VERIFY_INSTALLATION.bat` - must show 5 green checks
2. Check logs: `CHECK_LOGS.bat`
3. Ensure complete v1.3.20 extraction (don't mix versions)
4. Review troubleshooting section above
5. Check regime engine is enabled: Look for "Market Regime Engine: [STATE]" not "DISABLED"

---

## ⚠️ IMPORTANT NOTES

- **Internet required:** News scraping, PyTorch/TensorFlow downloads
- **Disk space:** ~5GB for models and data
- **Memory:** 8GB RAM recommended (4GB minimum)
- **Time:** Test mode 15min, Full mode 4 hours
- **Web UI:** Port 5000 must be available for web interface

---

## 🎯 SUCCESS CRITERIA

Installation successful if:
1. ✅ `VERIFY_INSTALLATION.bat` shows 5 green checkmarks
2. ✅ Test mode completes: `RUN_PIPELINE_TEST.bat`
3. ✅ Regime engine shows: `Market Regime Engine: [CALM/NORMAL/HIGH_VOL]`
4. ✅ LSTM training: `Success Rate: >70%`
5. ✅ Report generated: `models/screening/reports/morning_reports/`
6. ✅ Web UI accessible: http://localhost:5000

---

**Version:** 1.3.20  
**Release Date:** 2025-11-20  
**Critical Fix:** Market Regime Engine configuration enabled  
**Status:** Production Ready  
**New Feature:** Web UI for report viewing
