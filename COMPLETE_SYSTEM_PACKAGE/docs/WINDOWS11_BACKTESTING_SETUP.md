# Windows 11 - Backtesting Setup Instructions

## 📋 What You Need to Update

You need to update **3 files** in your Windows 11 deployment to add backtesting functionality:

---

## 📁 Files to Update

### Location on Windows 11:
```
FinBERT_v4.0_Windows11_ENHANCED/
├── app_finbert_v4_dev.py          ← Update this
├── templates/
│   └── finbert_v4_enhanced_ui.html ← Update this
└── models/
    └── backtesting/                ← Add these files (entire folder)
        ├── __init__.py
        ├── cache_manager.py
        ├── data_loader.py
        ├── data_validator.py
        ├── prediction_engine.py
        └── trading_simulator.py
```

---

## 🚀 Step-by-Step Instructions

### **Option 1: Download Updated Files** (Recommended)

1. **Download the entire `FinBERT_v4.0_Windows11_ENHANCED` folder**
   - From: `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/`
   - This contains all the updated files with backtesting integrated

2. **Replace your local folder**
   - Back up your current `FinBERT_v4.0_Windows11_ENHANCED` folder
   - Extract the new one in its place

3. **Done!** Skip to "Testing the Integration" below

---

### **Option 2: Manual File Updates**

If you want to update files individually:

#### **Step 1: Update the Flask App**

**File**: `app_finbert_v4_dev.py`

**Download from**: `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/app_finbert_v4_dev.py`

**What changed**:
- Added backtesting API endpoints (~200 lines)
- Updated startup messages

#### **Step 2: Update the UI Template**

**File**: `templates/finbert_v4_enhanced_ui.html`

**Download from**: `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/templates/finbert_v4_enhanced_ui.html`

**What changed**:
- Added "Backtest Strategy" button
- Added backtesting modal
- Added JavaScript functions (~270 lines)

#### **Step 3: Add Backtesting Modules**

**Create folder**: `models/backtesting/`

**Download these 6 files** from `/home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/models/backtesting/`:

1. `__init__.py` - Package initialization
2. `cache_manager.py` - SQLite caching system
3. `data_loader.py` - Historical data loading
4. `data_validator.py` - Data quality validation
5. `prediction_engine.py` - Walk-forward predictions
6. `trading_simulator.py` - Trading simulation

**Place them in**: `models/backtesting/` (create the folder if it doesn't exist)

---

## 🔧 Install Required Packages

Open **Command Prompt** or **PowerShell** in your FinBERT directory:

```bash
pip install yfinance pandas numpy
```

These packages are needed for the backtesting framework to work.

---

## ✅ Verify the Setup

### Check File Structure:

```
FinBERT_v4.0_Windows11_ENHANCED/
├── app_finbert_v4_dev.py          ✓ Updated
├── templates/
│   └── finbert_v4_enhanced_ui.html ✓ Updated
└── models/
    ├── backtesting/                ✓ New folder
    │   ├── __init__.py
    │   ├── cache_manager.py
    │   ├── data_loader.py
    │   ├── data_validator.py
    │   ├── prediction_engine.py
    │   └── trading_simulator.py
    ├── finbert_sentiment.py        (existing)
    └── lstm_predictor.py           (existing)
```

---

## 🧪 Testing the Integration

### 1. Start the Server:

Open Command Prompt in the `FinBERT_v4.0_Windows11_ENHANCED` folder:

```bash
python app_finbert_v4_dev.py
```

### 2. Check the Console Output:

You should see:

```
======================================================================
  FinBERT v4.0 Development Server - FULL AI/ML Experience
======================================================================

🎯 Features:
✓ LSTM Neural Networks: Trained & Loaded
✓ FinBERT Sentiment: Active
✓ Ensemble Predictions (Multi-Model)
✓ Enhanced Technical Analysis
✓ Real-time Market Data (Yahoo Finance)
✓ Candlestick & Volume Charts
✓ Backtesting Framework (Walk-Forward Validation)    ← NEW!

📊 API Endpoints:
  /api/stock/<symbol>     - Stock data with AI predictions
  /api/sentiment/<symbol> - FinBERT sentiment analysis
  /api/train/<symbol>     - Train LSTM model (POST)
  /api/models             - Model information
  /api/backtest/run       - Run backtesting (POST)      ← NEW!
  /api/backtest/models    - Available backtest models   ← NEW!
```

### 3. Open the UI:

Open your browser to:
```
http://127.0.0.1:5001
```

### 4. Look for the Backtest Button:

In the header (top right), you should see:
```
[Backtest Strategy]  [Train Model]
      ↑ NEW!
```

### 5. Test a Backtest:

1. Enter a stock symbol (e.g., **AAPL**)
2. Click **"Backtest Strategy"** (blue button)
3. A modal should open with:
   - Stock Symbol: AAPL (auto-filled)
   - Model Type: Ensemble
   - Date range: Last year
   - Capital: $10,000
4. Click **"Run Backtest"**
5. Wait 30-60 seconds
6. View results!

---

## 🐛 Troubleshooting

### Error: "Backtesting framework not available"

**Solution**: Make sure the `models/backtesting/` folder exists with all 6 files.

**Verify**:
```bash
dir models\backtesting
```

You should see:
```
__init__.py
cache_manager.py
data_loader.py
data_validator.py
prediction_engine.py
trading_simulator.py
```

### Error: "No module named 'yfinance'"

**Solution**: Install required packages:
```bash
pip install yfinance pandas numpy
```

### Error: "No module named 'backtesting'"

**Solution**: Check that `__init__.py` exists in `models/backtesting/`

### Button Not Showing

**Solution**: 
1. Clear browser cache (Ctrl + F5)
2. Verify `finbert_v4_enhanced_ui.html` was updated
3. Restart the Flask server

### Modal Opens But Backtest Fails

**Solution**:
1. Check internet connection (needs to download stock data)
2. Try a different stock symbol
3. Check the console for detailed error messages

---

## 📊 Expected Results

When you run a backtest successfully, you should see:

```
┌──────────────────────────────────────────────┐
│  📈 Backtest Results                         │
├──────────────────────────────────────────────┤
│                                              │
│  Total Return        Total Trades           │
│  +12.5%              25                      │
│                                              │
│  Win Rate            Sharpe Ratio            │
│  60.0%               1.40                    │
│                                              │
│  Max Drawdown        Profit Factor           │
│  -8.2%               1.85                    │
│                                              │
│  Final Equity: $11,250.00                    │
└──────────────────────────────────────────────┘
```

---

## 📁 Where to Download Files

### Method 1: ZIP Package (Easiest)

Create a ZIP file of the entire updated folder:

```bash
# On the server (where files are located):
cd /home/user/webapp
zip -r FinBERT_v4.0_Windows11_ENHANCED_WITH_BACKTESTING.zip FinBERT_v4.0_Windows11_ENHANCED/
```

Then download: `FinBERT_v4.0_Windows11_ENHANCED_WITH_BACKTESTING.zip`

### Method 2: Individual Files

Download from these exact paths:

1. **Main App**:
   ```
   /home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/app_finbert_v4_dev.py
   ```

2. **UI Template**:
   ```
   /home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/templates/finbert_v4_enhanced_ui.html
   ```

3. **Backtesting Modules** (all files in folder):
   ```
   /home/user/webapp/FinBERT_v4.0_Windows11_ENHANCED/models/backtesting/
   ```

---

## ✨ Features You'll Get

Once setup is complete, you'll be able to:

- ✅ **One-click backtesting** from the landing page
- ✅ Test any stock (US, Australian, etc.)
- ✅ Choose from 3 prediction models (FinBERT, LSTM, Ensemble)
- ✅ Configure date ranges and capital
- ✅ View comprehensive performance metrics
- ✅ See color-coded results (green=profit, red=loss)
- ✅ Get results in under 1 minute
- ✅ Automatic data caching (faster subsequent runs)

---

## 🎯 Quick Summary

**What to do**:
1. Download the updated `FinBERT_v4.0_Windows11_ENHANCED` folder
2. Replace your existing folder (back up first!)
3. Install packages: `pip install yfinance pandas numpy`
4. Run: `python app_finbert_v4_dev.py`
5. Open: `http://127.0.0.1:5001`
6. Click "Backtest Strategy" button
7. Done!

**Time required**: ~5-10 minutes

**Result**: Full backtesting framework integrated into your landing page!

---

## 📞 Need Help?

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify all files are in the correct locations
3. Make sure all required packages are installed
4. Check the console output for detailed error messages
5. Try restarting the Flask server

---

**Last Updated**: November 1, 2024  
**Backtesting Framework Version**: 1.0.0  
**FinBERT Version**: 4.0 Enhanced
