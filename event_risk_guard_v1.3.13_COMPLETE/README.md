# Event Risk Guard v1.3.13 - Complete Deployment Package

## 📦 What's Included

This is the **COMPLETE** deployment package containing all files needed to run the Event Risk Guard overnight screening pipeline with market regime detection and LSTM training.

### Core Features
- ✅ **Market Regime Engine**: HMM/GMM-based regime detection (CALM, NORMAL, HIGH_VOL)
- ✅ **LSTM Training**: Automatic training integrated in PHASE 4.5 (trains 86 stocks)
- ✅ **86 Stocks Configuration**: All ASX sectors covered
- ✅ **Web UI**: Model monitoring and log viewing
- ✅ **Windows 11 Compatible**: No Unicode errors, tested on Windows 11
- ✅ **Diagnostic Tools**: Comprehensive regime engine testing

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: The requirements.txt includes all packages with optional components commented out. Uncomment if you want:
- `hmmlearn` - HMM-based regime detection (better than GMM fallback)
- `arch` - GARCH volatility forecasting (better than EWMA fallback)
- `xgboost` - XGBoost ensemble models

### Step 2: Verify Installation
```bash
# Windows
RUN_DIAGNOSTIC_SAFE.bat

# Linux/Mac
python diagnose_regime.py
```

Expected output:
```
Regime: HIGH_VOL (or NORMAL/CALM)
Volatility: 0.7% daily
Crash Risk: 61% (High)
```

### Step 3: Run Pipeline
```bash
# Windows
RUN_PIPELINE.bat

# Linux/Mac
python run_pipeline.py
```

---

## 📁 Package Structure

```
event_risk_guard_v1.3.13_COMPLETE/
│
├── 📄 README.md                          # This file
├── 📄 CLEAN_DEPLOYMENT_README.txt        # Detailed deployment guide
├── 📄 DIAGNOSTIC_INSTRUCTIONS.txt        # Diagnostic tool usage
├── 📄 requirements.txt                   # Python dependencies
│
├── 🐍 run_pipeline.py                    # Main entry point
├── 🐍 web_ui.py                          # Web interface (port 5000)
├── 🐍 diagnose_regime.py                 # Regime engine diagnostic
│
├── 🪟 RUN_PIPELINE.bat                   # Windows: Run full pipeline
├── 🪟 RUN_WEB_UI.bat                     # Windows: Start web UI
├── 🪟 RUN_DIAGNOSTIC_SAFE.bat            # Windows: Run diagnostic (basic)
├── 🪟 RUN_DIAGNOSTIC_WITH_LOG.bat        # Windows: Run diagnostic (save log)
│
├── 📂 models/                            # Core modules
│   ├── __init__.py
│   ├── 📂 config/
│   │   ├── __init__.py
│   │   ├── screening_config.json        # Pipeline configuration
│   │   └── asx_sectors.json             # 86 stocks (all sectors)
│   │
│   └── 📂 screening/
│       ├── __init__.py
│       │
│       ├── overnight_pipeline.py        # Main orchestrator (PHASE 4.5 integrated)
│       ├── lstm_trainer.py              # LSTM training logic
│       ├── stock_scanner.py             # Data collection
│       ├── batch_predictor.py           # Predictions
│       ├── opportunity_scorer.py        # Scoring logic
│       ├── spi_monitor.py               # SPI futures monitoring
│       ├── event_risk_guard.py          # Event risk analysis
│       ├── report_generator.py          # HTML report generation
│       │
│       ├── market_regime_engine.py      # Regime orchestrator
│       ├── regime_detector.py           # HMM/GMM detection
│       └── volatility_forecaster.py     # GARCH/EWMA forecasting
│
├── 📂 logs/                              # Execution logs (created automatically)
├── 📂 data/                              # Cached data (created automatically)
├── 📂 reports/                           # HTML reports (created automatically)
└── 📂 models/ (root)                     # LSTM models (*.keras files, created automatically)
```

---

## 🔧 Configuration

### Key Settings (models/config/screening_config.json)

```json
{
  "scan_schedule": {
    "run_time": "18:00",              // 6 PM daily
    "timezone": "Australia/Sydney"
  },
  
  "data_collection": {
    "lookback_days": 180,             // 6 months history
    "chunk_size": 10                  // Process 10 stocks at a time
  },
  
  "lstm_training": {
    "enabled": true,
    "max_models_per_night": 100,      // Train up to 100 stocks
    "stale_threshold_days": 7,        // Re-train after 7 days
    "epochs": 50,
    "train_all_scanned_stocks": true  // Train all 86 stocks
  },
  
  "regime_integration": {
    "enabled": true,
    "weight_in_opportunity_score": 0.15  // 15% of total score
  }
}
```

### 86 Stocks Coverage (models/config/asx_sectors.json)

**All ASX sectors covered:**
- Financials: 21 stocks (CBA, WBC, NAB, ANZ, MQG, etc.)
- Materials: 18 stocks (BHP, RIO, FMG, MIN, S32, etc.)
- Healthcare: 12 stocks (CSL, COH, RMD, SHL, etc.)
- Consumer: 10 stocks (WES, JBH, HVN, etc.)
- Industrials: 8 stocks (WOR, BXB, SEK, etc.)
- Energy: 7 stocks (WDS, STO, ORG, etc.)
- Technology: 5 stocks (WTC, XRO, CPU, etc.)
- Telecom: 3 stocks (TLS, TPG, etc.)
- Utilities: 2 stocks (APA, ORG)

---

## 🏃 Running the Pipeline

### Full Pipeline Execution

**Windows:**
```bash
RUN_PIPELINE.bat
```

**Linux/Mac:**
```bash
python run_pipeline.py
```

### Test Mode (5 Stocks Only)

**Windows:**
```bash
python run_pipeline.py --test
```

**Linux/Mac:**
```bash
python run_pipeline.py --test
```

### Expected Execution Flow

```
PHASE 1: SPI FUTURES MONITORING (5 mins)
├── Downloads ASX SPI futures data
└── Checks for market gaps

PHASE 2: STOCK DATA COLLECTION (15-20 mins)
├── Downloads 86 stocks (180 days history)
└── Processes in chunks of 10

PHASE 3: FINBERT SENTIMENT ANALYSIS (10-15 mins)
├── Analyzes recent news for each stock
└── Sentiment: Positive, Negative, Neutral

PHASE 4: TECHNICAL & EVENT SCORING (5-10 mins)
├── Calculates technical indicators
├── Integrates regime engine (crash risk)
└── Generates opportunity scores (0-100)

⭐ PHASE 4.5: LSTM MODEL TRAINING (30-60 mins) ⭐
├── Creates training queue (top 100 by score)
├── Trains models (50 epochs each)
└── Saves to models/*.keras

PHASE 5: REPORT GENERATION (2-3 mins)
├── Ranks opportunities
└── Generates HTML report

PHASE 6-9: WEB SERVER & MONITORING (Continuous)
├── Starts Flask web server (port 5000)
└── Auto-refresh every 5 minutes
```

**Total Runtime:**
- First run: 70-110 minutes
- Subsequent runs: 40-60 minutes (re-trains stale models only)

---

## 🌐 Web UI

### Starting the Web UI

**Windows:**
```bash
RUN_WEB_UI.bat
```

**Linux/Mac:**
```bash
python web_ui.py
```

### Accessing the UI

Open browser to: **http://localhost:5000**

### Features

- 📊 View all trained LSTM models (86 stocks)
- 📋 Monitor pipeline logs in real-time
- 🎯 Check current market regime (HIGH_VOL, NORMAL, CALM)
- 📈 Browse latest opportunities
- 🔍 Search and filter models

---

## 🔍 Diagnostic Tools

### Quick Diagnostic (Windows)

```bash
RUN_DIAGNOSTIC_SAFE.bat
```

- Runs diagnostic
- Shows results in console
- Pauses before closing

### Diagnostic with Log (Windows)

```bash
RUN_DIAGNOSTIC_WITH_LOG.bat
```

- Runs diagnostic
- Saves output to timestamped log file
- Opens log in Notepad automatically

### Manual Diagnostic (All Platforms)

```bash
python diagnose_regime.py
```

### What Diagnostic Tests

1. ✅ Package versions (pandas, numpy, yfinance, etc.)
2. ✅ Data download (ASX 200)
3. ✅ MultiIndex structure validation
4. ✅ Regime detection (HMM/GMM)
5. ✅ Volatility forecasting (GARCH/EWMA)
6. ✅ Crash risk calculation

### Expected Results

```
=== SYSTEM CHECK ===
[OK] pandas: 2.0.3
[OK] numpy: 1.24.3
[OK] yfinance: 0.2.66
[OK] scikit-learn: 1.3.0
[OK] tensorflow: 2.10.0

=== DATA DOWNLOAD TEST ===
[SUCCESS] Downloaded 125 days of ASX 200 data

=== REGIME DETECTION RESULTS ===
Regime: HIGH_VOL
Volatility: 0.71% daily (11.30% annualized)
Crash Risk: 61.1% (High)
Confidence: High (125 data points)
Method: GARCH
```

---

## ✅ Verification Checklist

After running the pipeline, verify:

### 1. Files Created
```
✓ models/*.keras (86 files)
✓ reports/opportunities_YYYYMMDD.html
✓ logs/screening/overnight_pipeline_YYYYMMDD.log
✓ data/stocks_cache.json
```

### 2. Log File Contents
```bash
# Check log file
cat logs/screening/overnight_pipeline_*.log
```

Look for:
```
✓ "PHASE 4.5: LSTM MODEL TRAINING"
✓ "Models trained: 86/86"
✓ "Successful: XX"
✓ "Report generated successfully"
```

### 3. Web UI
```bash
# Start web UI
python web_ui.py

# Open browser
http://localhost:5000
```

Verify:
```
✓ See 86 models listed
✓ See latest opportunities
✓ Regime shows HIGH_VOL or NORMAL
✓ Logs visible
```

### 4. Model Files
```bash
# List all trained models
ls -lh models/*.keras
```

Should show 86 files like:
```
CBA.keras (Commonwealth Bank)
BHP.keras (BHP Group)
WBC.keras (Westpac)
... (83 more)
```

---

## 🐛 Troubleshooting

### Issue: "UNKNOWN" Regime

**Symptoms**: Regime shows "UNKNOWN" instead of HIGH_VOL/NORMAL/CALM

**Solutions**:
```bash
# 1. Check data download
python -c "import yfinance as yf; print(yf.download('^AXJO', period='6mo'))"

# 2. Verify package versions
python -c "import pandas; print(pandas.__version__)"  # Should be 2.0+

# 3. Run diagnostic
python diagnose_regime.py
```

### Issue: No Models in Web UI

**Symptoms**: Web UI shows "No models found"

**Solutions**:
```bash
# 1. Check if models exist
ls models/*.keras

# 2. Check web UI search paths
python -c "from pathlib import Path; print(list(Path('models').glob('*.keras')))"

# 3. Re-run pipeline
python run_pipeline.py
```

### Issue: Training Fails

**Symptoms**: "Failed: 86" in PHASE 4.5 logs

**Solutions**:
```bash
# 1. Verify TensorFlow installation
python -c "import tensorflow as tf; print(tf.__version__)"

# 2. Check memory (need 4GB+)
# Windows: wmic OS get FreePhysicalMemory /Value

# 3. Clear cache and retry
rm -f data/stocks_cache.json
python run_pipeline.py
```

### Issue: Import Errors

**Symptoms**: `ModuleNotFoundError: No module named 'xxx'`

**Solutions**:
```bash
# 1. Reinstall requirements
pip install -r requirements.txt

# 2. Verify Python version (need 3.8+)
python --version

# 3. Check package installation
pip list | grep -E "pandas|numpy|tensorflow"
```

### Issue: yfinance Errors

**Symptoms**: `TypeError: download() got an unexpected keyword argument 'show_errors'`

**Solutions**:
```bash
# 1. Check yfinance version (need 0.2.66+)
python -c "import yfinance; print(yfinance.__version__)"

# 2. Upgrade if needed
pip install --upgrade yfinance
```

---

## 📊 Expected Results

### First Run (70-110 minutes)

After the first run, you should have:

1. **86 LSTM Models Trained**
   - Location: `models/*.keras`
   - Size: ~500KB - 2MB each
   - Total size: ~50-100MB

2. **Opportunity Report**
   - Location: `reports/opportunities_YYYYMMDD.html`
   - Contains: Top opportunities ranked by score
   - Includes: Regime status, crash risk, predictions

3. **Detailed Logs**
   - Location: `logs/screening/overnight_pipeline_YYYYMMDD.log`
   - Contains: Full execution trace
   - Includes: All 9 phases with timing

4. **Cached Data**
   - Location: `data/stocks_cache.json`
   - Contains: Downloaded stock data
   - Speeds up subsequent runs

### Subsequent Runs (40-60 minutes)

- Re-trains stale models (>7 days old)
- Updates data for all 86 stocks
- Generates new opportunity report
- Maintains model freshness

---

## 🔒 System Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- 1GB disk space
- Internet connection

### Recommended
- Python 3.10+ (tested on 3.12.9)
- 8GB RAM
- 2GB disk space
- Stable internet (for data downloads)

### Operating Systems
- ✅ Windows 10/11 (primary, tested)
- ✅ Linux (Ubuntu 20.04+)
- ✅ macOS (10.15+)

---

## 📝 Notes

### Optional Dependencies

The system works without these packages (graceful degradation):

- **hmmlearn**: Falls back to GMM for regime detection
- **arch**: Falls back to EWMA for volatility forecasting
- **xgboost**: Ensemble predictions disabled

To enable, uncomment in `requirements.txt` and reinstall:
```bash
pip install -r requirements.txt
```

### Training Schedule

- **Night 1**: Trains all 86 stocks
- **Night 2+**: Re-trains stale models (>7 days) + new opportunities
- **Lifecycle**: Models stay fresh, automatic maintenance

### Performance Tips

1. **Use SSD**: Faster model loading and saving
2. **More RAM**: Parallel processing possible
3. **Stable Internet**: Reduces data download retries
4. **Close Other Apps**: More memory for training

---

## 🆘 Support

### Documentation
- **CLEAN_DEPLOYMENT_README.txt**: Comprehensive guide (19.7 KB)
- **DIAGNOSTIC_INSTRUCTIONS.txt**: Diagnostic tool usage
- **This README**: Quick reference

### Common Issues
- Unicode errors: ✅ FIXED in v1.3.9 (ASCII-safe)
- yfinance compatibility: ✅ FIXED in v1.3.10 (0.2.66+)
- Model detection: ✅ FIXED in v1.3.12 (multi-location search)
- Training integration: ✅ FIXED in v1.3.13 (PHASE 4.5 added)

### Getting Help
1. Run diagnostic: `python diagnose_regime.py`
2. Check logs: `logs/screening/*.log`
3. Verify installation: Check this README's troubleshooting section

---

## 📜 Version History

### v1.3.13 (2025-11-19) - Current
- ✅ Complete deployment package
- ✅ All essential files included
- ✅ __init__.py files added
- ✅ requirements.txt with all dependencies
- ✅ Main entry point (run_pipeline.py)
- ✅ Windows batch files
- ✅ Comprehensive documentation

### v1.3.12
- Enhanced web UI model detection
- Multi-location search (.keras and .h5)
- Log size validation

### v1.3.11
- Added model file format support
- Fixed web UI search paths

### v1.3.10
- yfinance 0.2.66 compatibility
- Removed show_errors parameter

### v1.3.9
- Windows 11 compatibility (ASCII-safe)
- Unicode character replacement

### v1.3.3
- MultiIndex extraction fix
- Regime detection working

### v1.3.2
- Data sufficiency improvements
- Post-feature validation

### v1.3.1
- VIX symbol fix (optional)
- GARCH volatility fallback

---

## 🎯 Production Status

**✅ PRODUCTION READY**

All features verified and tested:
- Market regime engine: WORKING (HIGH_VOL detection confirmed)
- LSTM training: INTEGRATED (PHASE 4.5 in pipeline)
- 86 stocks: CONFIGURED (all sectors covered)
- Web UI: ENHANCED (multi-location model search)
- Windows 11: COMPATIBLE (no Unicode errors)
- Documentation: COMPLETE (3 comprehensive guides)

**Ready for immediate deployment and use.**

---

## 📦 Quick Reference

```bash
# Install
pip install -r requirements.txt

# Test regime engine
python diagnose_regime.py

# Run full pipeline
python run_pipeline.py

# Run in test mode (5 stocks)
python run_pipeline.py --test

# Start web UI
python web_ui.py

# Check results
ls models/*.keras
ls reports/*.html
tail -f logs/screening/*.log
```

---

**Event Risk Guard v1.3.13** - Complete Deployment Package  
© 2025 FinBERT Trading System
