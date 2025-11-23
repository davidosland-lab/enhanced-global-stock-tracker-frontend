# FinBERT v4.4.4 - Clean Install Package

## 🚀 Quick Start (3 Steps)

### Step 1: Extract This ZIP
Extract to any folder on your computer.

### Step 2: Run Installer
Double-click: **`INSTALL_DEPENDENCIES.bat`**

This automated installer will:
- Check Python installation
- Check pip availability
- Let you choose installation mode
- Install all selected packages automatically
- Verify installation

### Step 3: Run Scanner
After installation completes:

**Quick Scanner**: `RUN_ALL_SECTORS_YAHOOQUERY.bat`
**Full System**: `RUN_OVERNIGHT_PIPELINE.bat`

---

## 💡 Installation Modes

### Mode 1: Quick Scanner (Recommended)
- Download: ~30 MB
- Time: 1-2 minutes
- Features: Technical screening only

### Mode 2: Full System
- Download: ~4 GB  
- Time: 10-30 minutes
- Features: LSTM + FinBERT + Technical

### Mode 3: Custom
- Pick specific components

---

## ✅ What the Installer Does

1. Checks Python 3.8+ is installed
2. Checks pip is available
3. Upgrades pip to latest
4. Shows interactive menu
5. Installs selected packages
6. Verifies all installations
7. Reports status and next steps

---

## 📦 Installation Commands

The installer runs these commands for you:

**Quick Scanner**:
```bash
pip install yahooquery pandas numpy
```

**Full System**:
```bash
pip install yahooquery pandas numpy yfinance ta tensorflow keras transformers torch scikit-learn feedparser pytz python-dateutil
```

---

## 🔍 Verification

After installation:

```bash
python test_integration_quick.py
```

Expected output:
```
✓ yahooquery import successful
✓ StockScanner initialized
✓ Loaded 8 sectors
✓ INTEGRATION TEST PASSED
```

---

## 🐛 Troubleshooting

### Python not found
Install from: https://www.python.org/downloads/
Check "Add Python to PATH" during install

### pip not found
Run: `python -m ensurepip --default-pip`

### TensorFlow fails
Try: `pip install tensorflow-cpu`

### PyTorch fails
Visit: https://pytorch.org for custom command

---

## 📚 Documentation

- **README_CLEAN_INSTALL.md** (this file)
- **DEPLOYMENT_SUMMARY.md** - Complete overview
- **INSTALLATION_GUIDE.md** - Detailed manual steps
- **STOCK_ANALYSIS_EXPLAINED.md** - Methodology
- **DEPLOYMENT_REQUIREMENTS.txt** - Package details

---

## 🎯 Next Steps

1. Run: `INSTALL_DEPENDENCIES.bat`
2. Choose installation mode
3. Wait for completion
4. Test: `python test_integration_quick.py`
5. Scan: `RUN_ALL_SECTORS_YAHOOQUERY.bat`

---

**That's it! The installer handles everything else.**
