# FinBERT v4.4.4 - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Extract the ZIP
Extract `FinBERT_FULL_SYSTEM_WITH_INSTALLER_YYYYMMDD_HHMMSS.zip` to a folder on your computer.

### Step 2: Run the Installer
Double-click: **`INSTALL_AND_RUN.bat`**

This will:
- ✅ Check Python installation
- ✅ Install required packages (yahooquery, pandas, numpy)
- ✅ Run integration test
- ✅ Launch scanner

### Step 3: Choose Scanning Mode

**Option 1: Quick Technical Scanner** ⚡
- Runtime: 5-10 minutes
- Dependencies: 3 packages (~30 MB)
- Output: CSV with technical scores

**Option 2: Full Overnight Pipeline** 🚀
- Runtime: 30-60 minutes  
- Dependencies: All packages (~4 GB)
- Output: LSTM predictions + FinBERT sentiment

---

## ❓ Do I Need to Install Dependencies?

**YES!** Python doesn't work like compiled programs. You must install packages first.

### Minimum Installation (Quick Scanner):
```bash
pip install yahooquery pandas numpy
```

### Full Installation (LSTM + Sentiment):
```bash
pip install -r DEPLOYMENT_REQUIREMENTS.txt
```

---

## 📦 What's Included?

### 📄 Documentation
- **INSTALLATION_GUIDE.md** ← READ THIS for detailed setup
- **STOCK_ANALYSIS_EXPLAINED.md** ← Explains the analysis methodology
- **README_FULL_SYSTEM.md** ← System architecture details
- **DEPLOYMENT_REQUIREMENTS.txt** ← Complete package list

### 🎯 Quick Scanner (Technical Only)
- `RUN_ALL_SECTORS_YAHOOQUERY.bat` - Main runner
- `run_all_sectors_yahooquery.py` - Python script
- `test_integration_quick.py` - Verify installation

### 🚀 Full System (LSTM + Sentiment)
- `RUN_OVERNIGHT_PIPELINE.bat` - Main runner
- `models/screening/overnight_pipeline.py` - Orchestrator
- `finbert_v4.4.4/` - ML models folder

---

## 🎯 Recommended Workflow

### First Time Users:
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

4. **Review results**:
   ```
   screener_results_yahooquery_TIMESTAMP.csv
   ```

### Advanced Users:
1. **Install all packages** (10-30 minutes):
   ```bash
   pip install -r DEPLOYMENT_REQUIREMENTS.txt
   ```

2. **Run full pipeline** (30-60 minutes):
   ```bash
   RUN_OVERNIGHT_PIPELINE.bat
   ```

3. **Review results**:
   ```
   overnight_scan_results_TIMESTAMP.csv
   predictions_TIMESTAMP.csv
   opportunities_TIMESTAMP.csv
   morning_report_TIMESTAMP.html
   ```

---

## ⚠️ Common Issues

### "No module named 'yahooquery'"
**Fix**: `pip install yahooquery`

### "pip is not recognized"
**Fix**: `python -m pip install yahooquery`

### Unicode errors (✓/✗ not displaying)
**Fix**: Use `RUN_ALL_SECTORS_YAHOOQUERY_WINDOWS.bat` (ASCII version)

### TensorFlow/PyTorch installation fails
**Fix**: Visit installation guide in INSTALLATION_GUIDE.md

---

## 📊 Expected Results

### Quick Scanner Output:
```
✓ Loaded 8 sectors
✓ Scanning Financial sector (5 stocks)...
  ✓ CBA.AX - Score: 85/100
  ✓ WBC.AX - Score: 80/100
  ✓ NAB.AX - Score: 75/100
✓ Scanning Materials sector (40 stocks)...
✓ Scanning Healthcare sector (25 stocks)...
[...continues for all 8 sectors...]
✓ Results saved to: screener_results_yahooquery_20251112_153045.csv
```

### CSV Columns:
- `symbol` - Stock ticker (e.g., CBA.AX)
- `score` - Composite score (0-100)
- `current_price` - Latest closing price
- `avg_volume` - Average daily volume
- `ma_20` - 20-day moving average
- `ma_50` - 50-day moving average
- `rsi` - Relative Strength Index
- `volatility` - Price volatility measure
- `sector` - Sector classification

---

## 📚 Further Reading

- **INSTALLATION_GUIDE.md** - Detailed installation instructions
- **STOCK_ANALYSIS_EXPLAINED.md** - Answers to common questions:
  - What analysis is being performed?
  - What measures are used?
  - Is LSTM being used? (Yes, in full pipeline)
  - Does sentiment use real data? (Yes, from Yahoo Finance + Finviz)
  - Best time to run? (3:45 PM AEST before market close)
  
- **README_FULL_SYSTEM.md** - System architecture and ensemble weights
- **DEPLOYMENT_REQUIREMENTS.txt** - Complete dependency list with sizes

---

## 🎓 Understanding the Two Modes

### Mode 1: Quick Technical Scanner
**Purpose**: Fast technical screening using yahooquery  
**Data Source**: Yahoo Finance via yahooquery API  
**Analysis**: Technical indicators only (no ML)  
**Components**:
- Liquidity scoring (0-20 points)
- Momentum analysis (0-20 points)
- RSI calculation (0-20 points)
- Volatility measurement (0-20 points)
- Sector weighting (0-20 points)

**When to Use**: Daily screening, quick filters, pre-market scans

---

### Mode 2: Full Overnight Pipeline
**Purpose**: Comprehensive ML-based prediction system  
**Data Sources**: yahooquery + yfinance + news scraping  
**Analysis**: 4-component ensemble  
**Components**:
1. **LSTM Neural Network** (45% weight) - Price prediction using TensorFlow
2. **Trend Analysis** (25% weight) - Moving average crossovers
3. **Technical Analysis** (15% weight) - RSI, MACD, Bollinger Bands
4. **FinBERT Sentiment** (15% weight) - News sentiment from transformer model

**When to Use**: Overnight runs, weekly strategy, deep analysis

---

## 💡 Pro Tips

1. **Start Simple**: Run quick scanner first, add ML later
2. **Timing Matters**: Run overnight pipeline at 3:45 PM AEST for best results
3. **Check Logs**: Review console output for errors or warnings
4. **Staged Installation**: Install packages incrementally if slow connection
5. **Test First**: Always run `test_integration_quick.py` before full scans

---

## 📞 Need Help?

1. Check **INSTALLATION_GUIDE.md** for setup issues
2. Read **STOCK_ANALYSIS_EXPLAINED.md** for methodology questions
3. Review **DEPLOYMENT_REQUIREMENTS.txt** for package details
4. Verify installation: `python test_integration_quick.py`

---

## ✅ Checklist

Before your first scan:
- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip working (`pip --version`)
- [ ] Packages installed (`pip install yahooquery pandas numpy`)
- [ ] Integration test passed (`python test_integration_quick.py`)
- [ ] Internet connection available
- [ ] Sufficient disk space (30 MB for quick, 4 GB for full)

---

## 🎯 Next Steps

**Just Getting Started?**
→ Read **INSTALLATION_GUIDE.md**

**Want to Understand the Analysis?**
→ Read **STOCK_ANALYSIS_EXPLAINED.md**

**Ready to Run?**
→ Execute **INSTALL_AND_RUN.bat**

**Need ML Predictions?**
→ Install full packages, then run **RUN_OVERNIGHT_PIPELINE.bat**

---

**Happy Scanning! 📈**
