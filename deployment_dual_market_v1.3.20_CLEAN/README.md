# Event Risk Guard v1.3.20 - Clean Deployment Package

## 🚀 Quick Start

### Installation (5-15 minutes)

**Windows:**
```cmd
1. Extract ZIP file
2. Double-click: INSTALL.bat
3. Wait for completion
4. Run: VERIFY_INSTALLATION.bat (must show 5 green checks)
```

**Linux/Mac:**
```bash
1. Extract ZIP file
2. chmod +x install.sh verify_installation.sh
3. ./install.sh
4. ./verify_installation.sh (must show 5 green checks)
```

---

## 🎯 What's Fixed in v1.3.20

### ✅ Market Regime Engine - ENABLED
- Added `regime_detector` configuration to screening_config.json
- Uncommented `hmmlearn` package in requirements.txt
- HMM-based market state classification now operational
- 3 states: CALM, NORMAL, HIGH_VOL with risk multipliers

### ✅ Complete Feature Set
- FinBERT v4.4.4 sentiment analysis
- LSTM neural network training (PHASE 4.5)
- Event risk assessment with regime awareness
- Overnight pipeline with comprehensive screening
- Web UI dashboard for monitoring

---

## 📋 Running the Pipeline

### Test Mode (15 minutes, 10 stocks)
```cmd
Windows: Double-click RUN_PIPELINE_TEST.bat
Linux:   ./run_pipeline_test.sh
```

### Full Mode (4 hours, 240 stocks)
```cmd
Windows: Double-click RUN_PIPELINE.bat
Linux:   ./run_pipeline.sh
```

### View Reports
```cmd
Windows: Double-click START_WEB_UI.bat
Linux:   python3 web_ui.py
Then open: http://localhost:5000
```

---

## ✅ Expected Output

### PHASE 2.5: Event Risk Assessment
```
PHASE 2.5: EVENT RISK ASSESSMENT
✓ Market Regime Engine initialized successfully
Market Regime Engine: HIGH_VOL (enabled)
Crash Risk Multiplier: 1.5
Adjusted Crash Risk: 0.588
```

**Should NOT see:**
```
Market Regime Engine: DISABLED  ← This means hmmlearn not installed
```

---

## 🔧 Troubleshooting

### If "Market Regime Engine: DISABLED" appears:

**Solution:**
```bash
pip install hmmlearn>=0.3.0
```

Then re-run the pipeline.

### If INSTALL.bat hangs:
- Wait 5-15 minutes (PyTorch/TensorFlow are large downloads)
- Check internet connection
- Don't close window while packages are installing

### If VERIFY_INSTALLATION.bat shows red X:
- Re-run INSTALL.bat
- Check Python version (must be 3.8+)
- Ensure all 5 checks show green ✓

---

## 📦 Package Contents

### Core Directories
- `models/` - Complete screening pipeline
  - `screening/` - Main pipeline modules
  - `config/` - Configuration files (regime detector enabled!)
  - `backtesting/` - Backtesting tools

- `finbert_v4.4.4/` - FinBERT integration
  - `models/` - LSTM, sentiment, news scraping
  - `__init__.py` - Proper package structure

### Web UI
- `templates/` - Dashboard HTML templates
- `static/` - CSS and JavaScript
- `web_ui.py` - Flask web application

### Execution Files
- `INSTALL.bat` / `install.sh` - Installation
- `RUN_PIPELINE_TEST.bat` / `run_pipeline_test.sh` - Test mode
- `RUN_PIPELINE.bat` / `run_pipeline.sh` - Full mode
- `START_WEB_UI.bat` - Launch web dashboard
- `VERIFY_INSTALLATION.bat` / `verify_installation.sh` - Verification
- `CHECK_LOGS.bat` - Quick log viewer

### Configuration
- `requirements.txt` - Python dependencies (hmmlearn ENABLED)
- `models/config/screening_config.json` - Main configuration
- `models/config/asx_sectors.json` - Sector definitions

---

## 🎯 Success Criteria

Installation successful if:
1. ✅ VERIFY_INSTALLATION.bat shows 5 green checks
2. ✅ Test pipeline completes all 6 phases
3. ✅ Regime engine shows: "Market Regime Engine: [STATE] (enabled)"
4. ✅ LSTM training shows: "Success Rate >70%"
5. ✅ Report generated in: models/screening/reports/morning_reports/
6. ✅ Web UI accessible at: http://localhost:5000

---

## 📊 System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- 5GB disk space
- Internet connection

**Recommended:**
- Python 3.10+
- 8GB RAM
- 10GB disk space
- SSD for faster training

---

## 🔑 Key Features

### Market Regime Engine (v1.3.20)
- 3-state HMM classification
- Risk multipliers: CALM (0.7x), NORMAL (1.0x), HIGH_VOL (1.5x)
- Daily updates with 24-hour cache
- Integration with crash risk assessment

### LSTM Training (PHASE 4.5)
- Up to 100 models per night
- 60-day sequence windows
- 7-day staleness threshold
- Success rate typically 70-90%

### FinBERT Sentiment Analysis
- Transformer-based analysis
- News scraping from Yahoo Finance and Finviz
- Real-time sentiment scoring
- Article count and polarity

### Event Risk Guard
- Earnings calendar detection
- Dividend event tracking
- News sentiment analysis
- Regime-aware crash risk

---

## 📝 Configuration

Edit `models/config/screening_config.json`:

### Enable/Disable Features
```json
{
  "lstm_training": {"enabled": true, "max_models_per_night": 100},
  "regime_detector": {"enabled": true, "n_states": 3},
  "finbert_integration": {"enabled": true}
}
```

### Adjust Risk Parameters
```json
{
  "regime_detector": {
    "risk_multipliers": {
      "CALM": 0.7,
      "NORMAL": 1.0,
      "HIGH_VOL": 1.5
    }
  }
}
```

---

## 🌐 Web UI Features

Access at: **http://localhost:5000**

- Dashboard with system status
- Latest report viewer
- Configuration editor
- Log viewer (last 200 lines)
- Trained models list
- API endpoints

---

## 📚 Output Files

### Reports
- `models/screening/reports/morning_reports/YYYY-MM-DD_market_report.html`
- `models/screening/reports/morning_reports/YYYY-MM-DD_data.json`

### Pipeline State
- `reports/pipeline_state/YYYY-MM-DD_pipeline_state.json`

### Logs
- `models/screening/logs/overnight_screening_YYYYMMDD.log`

### Trained Models
- `finbert_v4.4.4/models/lstm_models/[SYMBOL]_lstm_model.h5`

---

## 🆘 Support

**If issues persist:**
1. Run VERIFY_INSTALLATION.bat (must show 5 green checks)
2. Install hmmlearn: `pip install hmmlearn>=0.3.0`
3. Check logs: CHECK_LOGS.bat
4. Verify Python 3.8+ installed
5. Ensure all files extracted from ZIP

---

## 🔄 Version History

- **v1.3.20** - Market Regime Engine enabled, hmmlearn included
- v1.3.19 - Command argument fix (--mode test)
- v1.3.18 - RUN script creation
- v1.3.17 - FinBERT Bridge method addition
- v1.3.16 - Installation fixes, PHASE 4.5 restoration
- v1.3.15 - Import fixes with __init__.py files

---

**Version:** 1.3.20  
**Release Date:** 2025-11-20  
**Status:** Production Ready  
**Critical Fix:** Market Regime Engine configuration + hmmlearn dependency

---

## ⚠️ Important Notes

- **hmmlearn is REQUIRED** for Market Regime Engine
- Run VERIFY_INSTALLATION.bat before using pipeline
- Test mode recommended before full run
- Internet required for news scraping and downloads
- Full pipeline takes ~4 hours for 240 stocks

---

**Start Here:**
1. Run INSTALL.bat
2. Run VERIFY_INSTALLATION.bat (check for 5 green ✓)
3. Run RUN_PIPELINE_TEST.bat
4. Check for "Market Regime Engine: [STATE] (enabled)"
5. View reports with START_WEB_UI.bat

**If you see "DISABLED": Run `pip install hmmlearn>=0.3.0`**
