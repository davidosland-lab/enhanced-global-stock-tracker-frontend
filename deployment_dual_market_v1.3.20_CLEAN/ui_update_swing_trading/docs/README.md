# Swing Trading UI Update

## 🎯 What This Does

Adds a **NEW "Swing Trading" button** to your FinBERT v4.0 interface with:
- Rose/pink button in top navigation bar
- Complete modal for configuring 5-day swing trading backtests
- Results display with metrics, charts, and trade history
- Integration with `/api/backtest/swing` endpoint

## 📦 Package Contents

```
ui_update_swing_trading/
├── templates/
│   └── finbert_v4_enhanced_ui.html    # Updated UI file (205KB)
├── docs/
│   └── README.md                      # This file
└── INSTALL.bat                        # Windows installer
```

## 🚀 Installation (1 Minute)

### Step 1: Extract Package
Extract `ui_update_swing_trading.zip` to a temporary location:
```
C:\Temp\ui_update_swing_trading\
```

### Step 2: Run Installer
```batch
cd C:\Temp\ui_update_swing_trading
INSTALL.bat
```

### Step 3: Enter Path
When prompted:
```
Enter path to FinBERT v4.4.4 directory: C:\Users\david\AATelS
```

**Note**: Enter the BASE path, installer will auto-detect `finbert_v4.4.4` subdirectory

### Step 4: Restart Server
```batch
cd C:\Users\david\AATelS
python finbert_v4.4.4\app_finbert_v4_dev.py
```

### Step 5: Open Browser
```
http://localhost:5001
```

**Look for the NEW rose/pink "Swing Trading" button!**

## 📍 Where to Find It

### Navigation Bar
```
[🔵 STM Financial] [🟡 DEMO v2] [🔵 Backtest Strategy] [🟣 Portfolio Backtest] 
[🌹 Swing Trading] ← NEW BUTTON  [🟠 Optimize Parameters] [🟣 Train Model]
```

### Visual Appearance
- **Color**: Rose/Pink (bg-rose-600)
- **Icon**: 📈 Chart Area
- **Text**: "Swing Trading"
- **Position**: Between "Portfolio Backtest" and "Optimize Parameters"

## 🎨 What the Modal Includes

### Configuration Form
1. **Stock Symbol** - e.g., AAPL
2. **Initial Capital** - Default: $100,000
3. **Start Date** - Default: 10 months ago
4. **End Date** - Default: Today
5. **Holding Period** - Default: 5 days (adjustable 1-30)
6. **Stop Loss %** - Default: 3% (adjustable 0-20%)
7. **Confidence Threshold** - Default: 65% (adjustable 50-95%)
8. **Max Position Size** - Default: 25% (adjustable 10-100%)

### Feature Toggles
- ✅ **Use Real Sentiment** - FinBERT + Historical News (ON by default)
- ✅ **Use LSTM** - Neural Network for Pattern Recognition (ON by default)

### Results Display
- **Key Metrics**: Total Return, Win Rate, Profit Factor, Total Trades
- **Additional Metrics**: Sharpe Ratio, Max Drawdown, Avg Hold Time
- **Equity Curve Chart**: Interactive Plotly chart showing portfolio value
- **Trade History Table**: Detailed list of all trades with entry/exit prices and P&L

## 🔧 What Was Added to the File

### 1. Navigation Button (Line ~343)
```html
<button onclick="openSwingBacktestModal()" class="px-4 py-2 bg-rose-600 hover:bg-rose-700 rounded-lg transition">
    <i class="fas fa-chart-area mr-2"></i> Swing Trading
</button>
```

### 2. Modal HTML (Lines ~3729-3900)
- Complete form with all configuration options
- Results panel with metrics and charts
- Loading indicator

### 3. JavaScript Functions (Lines ~2371-2550)
```javascript
function openSwingBacktestModal()      // Opens the modal
function closeSwingBacktestModal()     // Closes the modal
function runSwingBacktest()            // Calls API endpoint
function displaySwingBacktestResults() // Shows results
function drawSwingEquityCurve()        // Plots chart
```

## ✅ Verification

After installation, verify the button was added:

```batch
findstr /C:"Swing Trading" C:\Users\david\AATelS\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html
```

**Expected Output:**
```
343:<button onclick="openSwingBacktestModal()" class="px-4 py-2 bg-rose-600 hover:bg-rose-700 rounded-lg transition">
344:    <i class="fas fa-chart-area mr-2"></i> Swing Trading
```

## 🔄 Rollback

If you need to restore the original file, use the automatic backup:

```batch
cd C:\Users\david\AATelS\finbert_v4.4.4\templates
dir finbert_v4_enhanced_ui.html.backup.*
copy finbert_v4_enhanced_ui.html.backup.YYYYMMDD_HHMMSS finbert_v4_enhanced_ui.html
```

## 📊 How to Use the Button

### 1. Click "Swing Trading" Button
The rose/pink button in the top navigation bar

### 2. Configure Backtest
- Enter stock symbol (e.g., AAPL, GOOGL, TSLA)
- Adjust dates (default: last 10 months)
- Modify parameters if desired
- Keep toggles checked for LSTM and sentiment

### 3. Run Backtest
Click "Run Swing Trading Backtest" button

### 4. Wait for Results
Takes 1-2 minutes depending on date range

### 5. Review Results
- Check total return, win rate, profit factor
- View equity curve chart
- Analyze trade history table
- Compare different stocks/parameters

## 🎯 Example Results

```
Total Return:    +8.45% (green)
Win Rate:        62.3%
Profit Factor:   2.1
Total Trades:    42
Sharpe Ratio:    1.84
Max Drawdown:    -5.2%
Avg Hold Time:   5.0 days
```

## 🆘 Troubleshooting

### Q: Button doesn't appear after installation?
**A:** 
1. Clear browser cache (Ctrl + F5)
2. Verify file was updated: `dir C:\Users\david\AATelS\finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html`
3. Check file timestamp is recent (today's date)
4. Restart the server completely

### Q: "API endpoint not found" error?
**A:** 
- Make sure you applied the bug fix patch first
- Verify `/api/backtest/swing` endpoint exists in `app_finbert_v4_dev.py`
- Check server logs for errors

### Q: Installer can't find directory?
**A:** 
- Enter BASE path: `C:\Users\david\AATelS`
- NOT the finbert_v4.4.4 subfolder
- Installer auto-detects subdirectories

### Q: Need to undo the changes?
**A:** 
- Use the backup file created automatically
- Location: `finbert_v4.4.4\templates\finbert_v4_enhanced_ui.html.backup.YYYYMMDD_HHMMSS`

## 📝 Technical Details

### File Modified
- **Path**: `finbert_v4.4.4/templates/finbert_v4_enhanced_ui.html`
- **Size**: 205KB (was ~145KB, added 60KB)
- **Lines Added**: 361 new lines
- **Backup**: Automatic before installation

### API Endpoint Used
```
POST /api/backtest/swing
```

### Request Format
```json
{
  "symbol": "AAPL",
  "start_date": "2024-01-01",
  "end_date": "2024-11-01",
  "initial_capital": 100000,
  "holding_period": 5,
  "stop_loss_pct": 3,
  "confidence_threshold": 0.65,
  "max_position_size": 0.25,
  "use_real_sentiment": true,
  "use_lstm": true
}
```

### Response Format
```json
{
  "backtest_type": "swing_trading",
  "symbol": "AAPL",
  "total_return": 8.45,
  "win_rate": 0.623,
  "profit_factor": 2.1,
  "total_trades": 42,
  "sharpe_ratio": 1.84,
  "max_drawdown": 0.052,
  "avg_hold_time": 5.0,
  "equity_curve": [...],
  "trades": [...]
}
```

## 🎉 Summary

| Item | Value |
|------|-------|
| **Installation** | 1 minute, fully automated |
| **File Modified** | 1 file (finbert_v4_enhanced_ui.html) |
| **Lines Added** | 361 lines |
| **Backup** | Automatic |
| **Browser** | No cache issues (force refresh if needed) |
| **Rollback** | Easy with backup file |
| **UI Location** | Top navigation bar (rose/pink button) |

---

**🚀 Ready to install! Just run INSTALL.bat and restart your server.**
