# WHICH START FILE TO USE?

## 🎯 **USE THIS ONE: `START_YAHOO.bat`** (Windows) or `START_YAHOO.sh` (Mac/Linux)

This is the **LATEST and BEST** version that:
- ✅ Uses Yahoo Finance ONLY (most reliable)
- ✅ Auto-detects Australian stocks (CBA → CBA.AX)
- ✅ NO Alpha Vantage issues
- ✅ Works perfectly with Commonwealth Bank and all ASX stocks

---

## File Guide:

### ✅ **RECOMMENDED:**
- **`START_YAHOO.bat`** (Windows) / **`START_YAHOO.sh`** (Mac/Linux)
  - The BEST choice for Australian stocks
  - Yahoo Finance only - no Alpha Vantage problems
  - Auto-detection for ASX symbols

### ⚠️ **ALTERNATIVE FILES (older versions):**
- `START.bat` - Original unified system (includes Alpha Vantage)
- `START_UNIFIED_SYSTEM.bat` - Full system with ML training
- `START_WINDOWS_SAFE.bat` - Safe mode for troubleshooting
- `START_CLEAN.bat` - Clean environment startup
- `START_REAL_DATA.bat` - Emphasizes real data only
- `START_WORKING.bat` - Previous working version
- `RUN_NOW.bat` - Quick start
- `RUN_FIXED.bat` - Fixed version

### 📁 **SERVER FILES:**
- **`yahoo_only_server.py`** - The BEST server (Yahoo only, Australian stocks optimized)
- `unified_system.py` - Full system with Alpha Vantage
- `working_server.py` - Previous working version
- `universal_predictor.py` - Command-line predictions

---

## 🚀 **QUICK START:**

### Windows:
```cmd
START_YAHOO.bat
```

### Mac/Linux:
```bash
chmod +x START_YAHOO.sh
./START_YAHOO.sh
```

### Manual Start:
```bash
python3 yahoo_only_server.py
```

---

## 📊 **FEATURES:**
- Real Yahoo Finance data
- Australian stocks (CBA.AX, BHP.AX, etc.)
- US stocks (AAPL, MSFT, etc.)
- Natural language AI assistant
- Price predictions with confidence scores
- Technical indicators (RSI, MACD, Moving Averages)

---

## ❓ **TROUBLESHOOTING:**
If START_YAHOO doesn't work, try:
1. `python3 yahoo_only_server.py` directly
2. Install dependencies: `pip install flask flask-cors yfinance pandas numpy requests`
3. Check Python version: `python --version` (needs 3.8+)