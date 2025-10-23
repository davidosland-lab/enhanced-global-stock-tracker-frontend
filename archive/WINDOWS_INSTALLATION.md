# GSMT Stock Tracker - Windows Installation Package

## 📦 Download

**Latest Version:** [GSMT_Stock_Tracker_Windows.zip](https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/raw/main/GSMT_Stock_Tracker_Windows.zip)

## ✅ What's Included

- **ML-Enhanced Stock Prediction System** with Phase 3 & 4 models
- **Real-time Stock Tracking** with fixed UI responsiveness
- **Technical Analysis** (RSI, MACD, Bollinger Bands, etc.)
- **Multiple ML Models** (LSTM, GNN, Ensemble, Reinforcement Learning)
- **Performance Dashboard** with backtesting
- **Windows-Optimized** installation with all fixes

## 🚀 Quick Installation Guide

### Step 1: Download and Extract
1. Download `GSMT_Stock_Tracker_Windows.zip`
2. Create folder `C:\GSMT`
3. Extract the ZIP to `C:\GSMT`
4. You should have: `C:\GSMT\GSMT_Windows11_Complete\`

### Step 2: Install
1. Open File Explorer
2. Navigate to `C:\GSMT\GSMT_Windows11_Complete`
3. **Double-click** `INSTALL_ULTIMATE.bat`
   - ⚠️ **DO NOT** run from Command Prompt
   - ⚠️ **DO NOT** run from System32 directory
4. Follow the on-screen prompts
5. Choose "Y" to start the application

### Step 3: Run
- Use desktop shortcut "GSMT Stock Tracker"
- Or double-click `RUN_APP.bat`
- Access at: http://localhost:8000

## 🔧 Troubleshooting

### If Installation Fails
1. Run `FIX_INSTALLATION.bat`
2. Choose Option 1 (Full Clean Install)
3. If still fails, use Option 4 (Simple Backend)

### Common Issues

#### "Installation Directory: C:\Windows\System32"
- **Solution:** You're running from wrong directory
- Close window and follow Step 2 above correctly

#### "Package installation failed"
- **Solution:** Run `FIX_INSTALLATION.bat` → Option 1

#### Python 3.13 Issues
- **Solution:** Use `INSTALL_ULTIMATE.bat` (handles compatibility)
- Or install Python 3.11/3.12 instead

## 📋 Requirements

- **Windows:** 10 or 11 (64-bit)
- **Python:** 3.8 to 3.12 (3.11 recommended)
- **RAM:** 4GB minimum
- **Storage:** 500MB free space
- **Internet:** Required for stock data

## 📁 Package Contents

```
GSMT_Windows11_Complete/
├── INSTALL_ULTIMATE.bat      # Main installer (use this)
├── FIX_INSTALLATION.bat      # Troubleshooting tool
├── CHECK_PYTHON.bat          # Python version checker
├── RUN_APP.bat              # Quick start launcher
├── backend/                  # Server files
│   ├── enhanced_ml_backend.py
│   └── simple_ml_backend.py  # Numpy-free alternative
├── frontend/                 # Web interface
│   ├── dashboard.html
│   └── tracker.html
└── [configuration files]
```

## 🆘 Help Resources

- **Installation Help:** See `INSTALLATION_HELP.txt` in package
- **Troubleshooting:** Run `TROUBLESHOOT.bat`
- **Python Issues:** Run `CHECK_PYTHON.bat`
- **GitHub Issues:** [Report Here](https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/issues)

## 🎯 Features

- ✅ Real-time stock price tracking
- ✅ ML predictions (LSTM, GNN, Ensemble)
- ✅ Technical indicators and analysis
- ✅ Trading signals (BUY/SELL/HOLD)
- ✅ Performance monitoring
- ✅ Strategy backtesting
- ✅ Market regime detection
- ✅ Support/Resistance levels

## 📝 Notes

- All previous package versions have been removed
- This is the only official Windows package
- Tested on Windows 10 and 11
- Python 3.11 gives best compatibility

---

**Version:** 3.2 Ultimate
**Last Updated:** September 2024
**License:** MIT