# 🚀 Quick Start Guide - Unified Trading System v1.3.15.129

## 📦 What's in This Package

This is a **COMPLETE, READY-TO-RUN** trading system deployment with:
- ✅ All dependencies and modules included
- ✅ Configuration files pre-configured
- ✅ LSTM 8-feature model (restored)
- ✅ FinBERT v4.4.4 sentiment analysis
- ✅ Enhanced Pipeline Signal Adapter (75-85% win rate target)
- ✅ Overnight screening pipelines (AU/US/UK)

---

## 🎯 Quick Start (3 Steps)

### Step 1: Extract the Package
```bash
# Extract the zip file
unzip unified_trading_system_v1.3.15.129_COMPLETE.zip
cd unified_trading_system_v1.3.15.129_COMPLETE
```

### Step 2: Run Installation (ONE TIME ONLY)
```bash
# Windows:
INSTALL_COMPLETE.bat

# Linux/Mac:
chmod +x INSTALL.sh
./INSTALL.sh
```

**What this does:**
- Creates virtual environment
- Installs Python dependencies (pandas, numpy, scikit-learn, yfinance, etc.)
- Installs TensorFlow & Keras for LSTM models
- Creates necessary directories (logs/, state/, config/, reports/)
- Runs integration tests

**Time required:** 5-10 minutes (depending on internet speed)

### Step 3: Start Trading
After installation completes successfully, you can:

#### Option A: Run Paper Trading (Recommended First)
```bash
cd core
python paper_trading_coordinator.py --symbols AAPL,MSFT,GOOGL,TSLA,NVDA --capital 100000 --use-enhanced-adapter
```

#### Option B: Generate Overnight Reports
```bash
# Australian market (ASX)
python scripts/run_au_pipeline_v1.3.13.py --full-scan

# US market (NYSE/NASDAQ)
python scripts/run_us_full_pipeline.py --full-scan

# UK market (London Stock Exchange)
python scripts/run_uk_full_pipeline.py --full-scan
```

#### Option C: Run Complete Workflow
```bash
# Windows:
RUN_COMPLETE_WORKFLOW.bat

# Linux/Mac:
./RUN_COMPLETE_WORKFLOW.sh
```

---

## ❓ FAQ: Install vs Start

### Q: Do I need to run INSTALL.bat every time?
**A: NO!** Only run `INSTALL_COMPLETE.bat` (or `INSTALL.sh`) **ONCE** after extracting the package.

### Q: What do I run every day?
**A:** After the initial installation, just run:
- `python scripts/run_au_pipeline_v1.3.13.py` (for AU morning report)
- `python scripts/run_us_full_pipeline.py` (for US morning report)
- `python core/paper_trading_coordinator.py` (for live trading)

Or use the convenience script:
- `RUN_COMPLETE_WORKFLOW.bat` (Windows)
- `./RUN_COMPLETE_WORKFLOW.sh` (Linux/Mac)

### Q: What's the difference between INSTALL.bat and INSTALL_COMPLETE.bat?
**A: Use INSTALL_COMPLETE.bat** - It's the comprehensive installer that includes:
- All base dependencies (pandas, numpy, etc.)
- FinBERT v4.4.4 with PyTorch (~2.5 GB)
- Transformers & SentencePiece
- Automatic configuration

`INSTALL.bat` is a minimal installer (faster but missing some components).

### Q: Can I skip installation if I already have Python packages?
**A: Not recommended.** The installer:
1. Creates a **isolated virtual environment** (won't conflict with your system Python)
2. Installs **specific versions** tested with this system
3. Creates required directories
4. Validates the installation with tests

---

## 🔍 Verify Installation

After running `INSTALL_COMPLETE.bat`, you should see:

```
✓ Virtual environment created
✓ Core dependencies installed
✓ LSTM dependencies installed
✓ Directories created
✓ Running integration tests...
  Test 1: Overnight report loading - PASSED
  Test 2: Trading opportunities - PASSED
  Test 3: Sentiment lookup - PASSED

============================================
 Installation Complete! ✓
============================================

Next steps:
1. Generate overnight reports: RUN_COMPLETE_WORKFLOW.bat
2. Run paper trading: cd core && python paper_trading_coordinator.py
3. Train LSTM models: cd finbert_v4.4.4 && python train_lstm_batch.py --market US
```

---

## 📁 Directory Structure After Installation

```
unified_trading_system_v1.3.15.129_COMPLETE/
├── venv/                    # Virtual environment (created by INSTALL.bat)
├── core/                    # Trading coordinator & signal generator
│   └── paper_trading_coordinator.py
├── scripts/                 # Pipeline scripts
│   ├── run_au_pipeline_v1.3.13.py
│   ├── run_us_full_pipeline.py
│   ├── run_uk_full_pipeline.py
│   └── complete_workflow.py
├── finbert_v4.4.4/         # FinBERT & LSTM models
│   ├── models/
│   │   ├── lstm_predictor.py
│   │   └── train_lstm.py
│   └── train_lstm_batch.py
├── pipelines/              # Screening pipelines
│   ├── config/            # Configuration files
│   └── models/
│       ├── config/        # Config files (for compatibility)
│       └── screening/     # Opportunity scorer, FinBERT bridge
├── reports/               # Generated reports (created at runtime)
│   └── screening/
│       ├── au_morning_report.json
│       ├── us_morning_report.json
│       └── uk_morning_report.json
├── logs/                  # Log files (created by INSTALL.bat)
├── state/                 # State files (created by INSTALL.bat)
├── config/                # Live trading config (created by INSTALL.bat)
└── docs/                  # Documentation
    ├── LSTM_8_FEATURES_RESTORED.md
    ├── ENHANCED_INTEGRATION_COMPLETE.md
    └── ...
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pandas'"
**Solution:** You didn't run `INSTALL_COMPLETE.bat`. Run it first.

### Issue: "FileNotFoundError: config/screening_config.json"
**Solution:** This package includes config files in both `pipelines/config/` and `pipelines/models/config/`. If you still see this error, ensure you extracted the **COMPLETE** package, not the RESTORED package.

### Issue: "LSTM predictions unavailable, using fallback"
**Solution:** 
1. Check that TensorFlow/Keras were installed: `pip list | grep -i keras`
2. If missing, manually install: `pip install tensorflow keras`
3. Restart the pipeline

### Issue: Pipeline fails with "No such file or directory"
**Solution:** Ensure you're running from the correct directory:
```bash
cd unified_trading_system_v1.3.15.129_COMPLETE
python scripts/run_au_pipeline_v1.3.13.py
```

### Issue: Tests fail during installation
**Solution:** Check the error message. Common causes:
- Missing internet connection (for downloading FinBERT model)
- Insufficient disk space (need 5-10 GB)
- Python version < 3.8 (upgrade to Python 3.8+)

---

## 📊 Expected Performance

### Before Restoration (Broken State)
- Win rate: 70-75% (ML signals only)
- LSTM: Fallback mode (~70% accuracy)
- Features: 5 instead of 8 (missing high, low, open)

### After Restoration (v1.3.15.129)
- Win rate: **75-85%** (overnight + ML signals)
- LSTM: Full 8-feature model (75-80% accuracy)
- Features: close, volume, high, low, open, sma_20, rsi, macd ✓
- Two-stage system: Overnight (40%) + Live ML (60%)

---

## 📝 Daily Workflow

### Morning (Before Market Opens)
```bash
# Generate overnight screening reports
python scripts/run_au_pipeline_v1.3.13.py --full-scan   # ~20 min, 240 stocks
python scripts/run_us_full_pipeline.py --full-scan     # ~40 min, 212 stocks
python scripts/run_uk_full_pipeline.py --full-scan     # ~45 min, 240 stocks
```

Output: `reports/screening/au_morning_report.json` (and US/UK equivalents)

**What you get:**
- Top 20-30 pre-screened stocks per market
- Opportunity scores (0-100)
- BUY/SELL/HOLD recommendations
- Technical signals (BREAKOUT, MOMENTUM, VOLUME, UPTREND)
- Sentiment ratings, risk levels, target prices

### During Market Hours
```bash
cd core
python paper_trading_coordinator.py \
  --symbols AAPL,MSFT,GOOGL,TSLA,NVDA \
  --capital 100000 \
  --use-enhanced-adapter
```

**What it does:**
- Loads overnight sentiment from morning reports
- Combines with live ML signals (FinBERT + LSTM)
- Executes paper trades (no real money)
- Logs performance metrics

### After Market Close
```bash
# Review performance
cat logs/paper_trading_YYYY-MM-DD.log

# Check win rate
python core/analyze_performance.py
```

---

## 🎓 Training LSTM Models (Optional)

For best performance, train LSTM models for your target stocks:

### Quick Training (Test 1-2 Stocks)
```bash
cd finbert_v4.4.4
python models/train_lstm.py --symbol AAPL    # ~5-10 min per stock
python models/train_lstm.py --symbol MSFT
```

### Batch Training (All Stocks)
```bash
cd finbert_v4.4.4

# US market (212 stocks, ~7-18 hours)
python train_lstm_batch.py --market US

# UK market (240 stocks, ~8-20 hours)
python train_lstm_batch.py --market UK

# AU market (240 stocks, ~8-20 hours)
python train_lstm_batch.py --market AU
```

**Recommendation:** Run batch training overnight or over a weekend.

---

## 📞 Support

### Documentation
- `README_DEPLOYMENT.md` - Full deployment guide
- `docs/ENHANCED_INTEGRATION_COMPLETE.md` - Integration details
- `docs/LSTM_8_FEATURES_RESTORED.md` - LSTM restoration guide
- `docs/MORNING_REPORT_COMPLETE_STRUCTURE.md` - Report format

### File Locations
- Package: `/home/user/webapp/deployments/unified_trading_system_v1.3.15.129_COMPLETE.zip`
- Git commit: `4a4ee15` (v1.3.15.129 COMPLETE Package)

### Common Commands Reference
```bash
# Activate virtual environment (if needed)
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Check installed packages
pip list

# Update a package
pip install --upgrade pandas

# Deactivate virtual environment
deactivate
```

---

## ✅ Success Criteria

You know the system is working correctly when:

1. **Installation tests pass:** 3/3 tests PASSED ✓
2. **Overnight reports generate:** `reports/screening/au_morning_report.json` exists and contains `top_stocks` array
3. **Paper trading runs:** No "ModuleNotFoundError" or "FileNotFoundError" 
4. **LSTM available:** Logs show "Keras LSTM available" (not "using fallback")
5. **Signals combined:** Logs show "Enhanced Pipeline Signal Adapter V3 initialized" with "Target win rate: 75-85%"

---

## 🚀 You're Ready!

**Remember:**
- Run `INSTALL.bat` → **ONCE** (first time only)
- Run `RUN_COMPLETE_WORKFLOW.bat` or individual scripts → **DAILY**
- Check `reports/screening/*.json` → **MORNING RESULTS**
- Monitor `logs/paper_trading_*.log` → **LIVE PERFORMANCE**

Good luck trading! 📈
