# Event Risk Guard v1.3.14 - CRITICAL FIXES

## Release Date: November 19, 2025

## 🚨 CRITICAL FIXES

### 1. **PHASE 4.5: LSTM Model Training - RESTORED**
**Issue**: LSTM training phase was completely missing from the pipeline, causing:
- No LSTM models being trained overnight
- `BatchPredictor` reporting "FinBERT LSTM Available: False"
- Training statistics showing 0 models trained

**Fix**:
- ✅ Added `_train_lstm_models()` method to `overnight_pipeline.py`
- ✅ Integrated PHASE 4.5 between PHASE 4 (Scoring) and PHASE 5 (Report Generation)
- ✅ Added comprehensive debug logging for training conditions
- ✅ Updated pipeline statistics to include LSTM training results
- ✅ Fixed configuration loading in `OvernightPipeline.__init__()`

**Location**: `models/screening/overnight_pipeline.py` (lines 707-768)

---

### 2. **Market Regime Engine Integration - ACTIVATED**
**Issue**: Market Regime Engine was present but never called:
- No regime detection logs during pipeline execution
- No crash risk scoring
- Event Risk Guard not leveraging regime data

**Fix**:
- ✅ Integrated `MarketRegimeEngine` into `EventRiskGuard.__init__()`
- ✅ Added `_get_regime_crash_risk()` method to EventRiskGuard
- ✅ Regime analysis now runs once per batch for performance
- ✅ Crash risk score included in event risk assessment
- ✅ Added logging for regime detection (CALM/NORMAL/HIGH_VOL)

**Location**: `models/screening/event_risk_guard.py` (lines 387-427, 446-467)

---

### 3. **FinBERT Integration - COMPLETE**
**Issue**: FinBERT components were referenced but missing:
- `finbert_bridge.py` module did not exist in deployment
- `finbert_v4.4.4` directory was missing entirely
- No real sentiment analysis or news scraping
- LSTM predictions falling back to trend-based estimates

**Fix**:
- ✅ Added `finbert_bridge.py` - Adapter pattern for FinBERT integration
- ✅ Included complete `finbert_v4.4.4` directory with all modules:
  - `finbert_sentiment.py` - Real FinBERT transformer sentiment analysis
  - `lstm_predictor.py` - Real neural network LSTM predictions
  - `news_sentiment_real.py` - Real news scraping (Yahoo Finance, Finviz)
  - `train_lstm.py` - LSTM model training for new symbols
- ✅ `BatchPredictor` now accesses real FinBERT components via bridge
- ✅ Graceful fallback when components unavailable

**New Files**:
- `models/screening/finbert_bridge.py`
- `finbert_v4.4.4/` (complete directory)

---

### 4. **Configuration Fixes**
**Issue**: `screening_config.json` had incorrect values:
- `max_models_per_night: 20` (should be 100)
- Missing `train_all_scanned_stocks` flag

**Fix**:
- ✅ Updated `max_models_per_night: 20 → 100`
- ✅ Added `train_all_scanned_stocks: true`
- ✅ Configuration now correctly loaded in pipeline `__init__()`
- ✅ Added debug logging for config values

**Location**: `models/config/screening_config.json` (lines 23-31)

---

## 📊 Expected Behavior After This Update

### LSTM Training
```
PHASE 4.5: LSTM MODEL TRAINING
================================
Creating training queue (max 100 stocks)...
Training 86 LSTM models...
[1/86] Training CBA.AX...
✅ CBA.AX: Training completed in 180.5s
...
[SUCCESS] LSTM Training Complete:
  Models trained: 86/86
  Successful: 86
  Failed: 0
  Total Time: 257.3 minutes
```

### Market Regime Engine
```
PHASE 2.5: EVENT RISK ASSESSMENT
=================================
Market Regime Engine: ENABLED
Batch assessment starting for 86 tickers
Market Regime: HIGH_VOL, Crash Risk: 0.725
Event Risk Assessment Complete:
  Upcoming Events: 12
  🚨 Regulatory Reports (Basel III/Pillar 3): 3
```

### FinBERT Integration
```
Batch Predictor initialized
  FinBERT LSTM Available: True
  FinBERT Sentiment Available: True
  FinBERT News Available: True
  
✓ Using REAL FinBERT LSTM for CBA.AX: direction=0.234
✓ Sentiment for CBA.AX: positive (78.5%), 15 articles
```

---

## 🔧 Installation Instructions

1. **Extract Package**:
   ```bash
   unzip event_risk_guard_v1.3.14_COMPLETE.zip
   cd event_risk_guard_v1.3.13_COMPLETE
   ```

2. **Install Dependencies** (Windows):
   ```bash
   INSTALL.bat
   ```
   
   **Install Dependencies** (Linux/Mac):
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Verify FinBERT Installation**:
   ```bash
   python -c "from models.screening.finbert_bridge import test_bridge; test_bridge()"
   ```

4. **Run Pipeline**:
   ```bash
   # Test mode (5 stocks from Financials)
   RUN_PIPELINE.bat --test
   
   # Full mode (all sectors)
   RUN_PIPELINE.bat
   ```

---

## 📋 Verification Checklist

After installation, verify these components:

### ✅ LSTM Training
- [ ] `PHASE 4.5: LSTM MODEL TRAINING` appears in logs
- [ ] Training statistics show models trained > 0
- [ ] `BatchPredictor` reports "FinBERT LSTM Available: True"

### ✅ Market Regime Engine
- [ ] `Market Regime Engine: ENABLED` in event risk assessment
- [ ] Regime label shown (CALM/NORMAL/HIGH_VOL)
- [ ] Crash risk score reported (0.0-1.0)

### ✅ FinBERT Integration
- [ ] `finbert_bridge.py` exists in `models/screening/`
- [ ] `finbert_v4.4.4/` directory exists
- [ ] Sentiment analysis shows article counts > 0
- [ ] LSTM predictions use "REAL FinBERT LSTM" (check logs)

---

## 🐛 Known Issues

### 1. First Run - No Trained Models
- **Symptom**: First pipeline run shows "No trained LSTM model found for XXX"
- **Solution**: This is expected! Models train overnight. Second run will use trained models.
- **Workaround**: Pre-train models using `train_lstm_batch.py` in `finbert_v4.4.4/`

### 2. FinBERT Model Download
- **Symptom**: First sentiment analysis is slow (downloads ProsusAI/finbert from HuggingFace)
- **Solution**: Wait for initial download (1.2GB). Subsequent runs use cached model.

### 3. News API Rate Limits
- **Symptom**: Some stocks show "No news articles" or "Sentiment unavailable"
- **Solution**: Yahoo Finance/Finviz rate limiting. Pipeline uses SPI fallback automatically.

---

## 📞 Support

If you encounter issues:

1. **Check Logs**:
   - `logs/screening/overnight_pipeline.log`
   - `logs/screening/lstm_training.log`

2. **Run Diagnostics**:
   ```bash
   RUN_DIAGNOSTIC_WITH_LOG.bat
   ```

3. **Verify FinBERT**:
   ```bash
   python finbert_v4.4.4/diagnose_environment.py
   ```

---

## 🎯 Summary

This release fixes **3 CRITICAL issues**:
1. ✅ LSTM training now executes correctly (PHASE 4.5)
2. ✅ Market Regime Engine actively detects market conditions
3. ✅ FinBERT provides real sentiment analysis and LSTM predictions

**Status**: PRODUCTION READY ✅

All originally promised features are now **ACTIVE and VERIFIED**.
