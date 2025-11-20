# 🚀 Quick Start Guide - Event Risk Guard v1.1

## ⚡ Get Running in 5 Minutes

### Prerequisites

✅ **Windows 10/11** (64-bit)  
✅ **Python 3.8+** installed  
✅ **Internet connection** (for package downloads)  
✅ **8 GB RAM minimum** (16 GB recommended)

---

## Step 1: Install Dependencies (5 minutes)

Double-click:
```
INSTALL.bat
```

**What it does:**
- Installs TensorFlow (LSTM neural networks)
- Installs Transformers (FinBERT AI)
- Installs Flask (Web dashboard)
- Installs data libraries (yfinance, pandas, etc.)

**Expected output:**
```
Installing Event Risk Guard dependencies...
[Progress bars...]
✅ All packages installed successfully!
```

**Download size**: ~2.5 GB  
**Install time**: 5-10 minutes

---

## Step 2: Run First Scan (15 minutes)

Double-click:
```
RUN_OVERNIGHT_PIPELINE.bat
```

**What it does:**
- Scans 80-100 ASX stocks
- Analyzes with FinBERT AI
- Calculates opportunity scores
- 🆕 Calculates macro betas (XJO, Lithium) - v1.1
- 🆕 Generates factor attribution analysis - v1.1
- Generates HTML + CSV reports
- Creates dashboard data

**Expected output:**
```
========================================================================
OVERNIGHT STOCK SCREENING
========================================================================

Scanning 81 stocks across 10 sectors...
Progress: [██████████] 100%

✅ Scan completed in 19.2 minutes
✅ Reports saved to: reports/
✅ Factor view saved to: reports/factor_view/
```

---

## Step 3: Launch Dashboard (Instant)

Double-click:
```
START_WEB_UI.bat
```

**Then open your browser to:**
```
http://localhost:5000
```

**You should see:**
- System status cards
- Top 10 opportunities
- Latest report summary
- Charts and metrics

**Dashboard auto-refreshes** every 30 seconds.

---

## ✅ You're Done!

The system is now running. You can:

- ✅ View dashboard at http://localhost:5000
- ✅ Check reports in `reports/html/`
- ✅ Review CSV exports in `reports/csv/`
- ✅ 🆕 Analyze factor breakdowns in `reports/factor_view/` (v1.1)
- ✅ Monitor logs in `logs/screening/`

---

## 📊 Understanding Factor Analysis Outputs (v1.1)

### New Output Files

Each pipeline run now generates 3 additional factor analysis files:

**1. Per-Stock Factor View**
```
reports/factor_view/2025-11-17_factor_view_stocks.csv
```
**Contains**: Detailed breakdown of each stock's opportunity score into 6 factors:
- Prediction confidence, technical strength, SPI alignment
- Liquidity, volatility, sector momentum
- Macro betas (XJO, Lithium)
- Adjustment impacts (bonuses/penalties)

**Use this for**: 
- Filtering stocks by specific factors
- Understanding what drives each score
- Building custom factor-based screens

---

**2. Sector Summary**
```
reports/factor_view/2025-11-17_factor_view_sector_summary.csv
```
**Contains**: Sector-level aggregations:
- Average opportunity scores per sector
- Average factor scores per sector
- Average betas per sector (market sensitivity)
- Buy/Hold/Sell distribution per sector

**Use this for**:
- Sector rotation strategies
- Identifying defensive vs aggressive sectors
- Comparing sector risk profiles

---

**3. Portfolio Summary**
```
reports/factor_view/2025-11-17_factor_view_summary.json
```
**Contains**: Overall portfolio statistics in JSON format:
- Total stocks analyzed
- Sector breakdown with detailed metrics
- Top performers by factor
- Overall prediction distribution

**Use this for**:
- Automated reporting dashboards
- API integration
- Time series tracking of portfolio characteristics

---

### Quick Analysis Examples

**Example 1: Find Defensive Stocks**
1. Open `factor_view_stocks.csv` in Excel
2. Filter: `beta_xjo < 0.8` (low market sensitivity)
3. Filter: `volatility > 70` (stable prices)
4. Sort by: `opportunity_score` (descending)
5. Result: Top defensive stocks with lower market correlation

**Example 2: Identify Lithium Plays**
1. Open `factor_view_stocks.csv`
2. Filter: `beta_lithium > 0.5` (high commodity exposure)
3. Filter: `opportunity_score > 75` (attractive opportunities)
4. Result: Stocks leveraged to lithium price movements

**Example 3: Compare Sectors**
1. Open `factor_view_sector_summary.csv`
2. Sort by: `avg_opportunity_score` (descending)
3. Review: `avg_beta_xjo` (market sensitivity by sector)
4. Result: Identify strongest sectors and their risk profiles

---

### Understanding Betas

**Beta XJO** (ASX 200 Market Sensitivity):
- **Beta > 1.0**: Aggressive stock (amplifies market moves)
  - Example: Beta = 1.3 means +13% when market up +10%
- **Beta = 1.0**: Moves with market
- **Beta < 1.0**: Defensive stock (cushions market moves)
  - Example: Beta = 0.7 means +7% when market up +10%
- **Beta ≈ 0**: Independent of market moves

**Beta Lithium** (Commodity Exposure):
- **High (> 0.5)**: Direct lithium/materials exposure
- **Medium (0.2-0.5)**: Moderate commodity link
- **Low (< 0.2)**: Minimal commodity sensitivity

---

### For More Details

See comprehensive factor analysis guide:
```
docs/FACTOR_VIEW_AND_BETAS.md
docs/FACTOR_ANALYSIS_EXAMPLES.md
```

---

## 🎓 Optional: Train LSTM Models

LSTM models improve accuracy but are **optional**.

### Quick Test (10-15 minutes)

Train just one stock to test:
```
TRAIN_LSTM_SINGLE.bat CBA.AX
```

### Full Training (1.5-2 hours)

Train 10 major ASX stocks:
```
TRAIN_LSTM_OVERNIGHT_FIXED.bat
```

**Recommendation**: Run this overnight once per week/month.

---

## 📧 Optional: Setup Email Reports

1. Get Gmail App Password:
   - Visit: https://myaccount.google.com/apppasswords
   - Create password for "Mail" + "Windows Computer"
   - Copy the 16-character password

2. Edit configuration:
   ```
   models/config/screening_config.json
   ```

3. Update these fields:
   ```json
   "smtp_username": "your-email@gmail.com",
   "smtp_password": "your-app-password-here",
   "recipient_emails": ["your-email@gmail.com"]
   ```

4. Test it:
   ```
   TEST_EMAIL.bat
   ```

---

## 🔄 Daily Usage

### Morning Routine (Automated)

**Option A**: Run manually each morning:
```
1. RUN_OVERNIGHT_PIPELINE.bat  (10-20 min)
2. START_WEB_UI.bat            (instant)
3. Open http://localhost:5000
```

**Option B**: Use Windows Task Scheduler:
- Schedule `RUN_OVERNIGHT_PIPELINE.bat` for 7:00 AM daily
- Schedule `START_WEB_UI.bat` to run at startup
- Dashboard always available

---

## 🐛 Troubleshooting

### "Python not found"

**Solution**: Install Python from https://python.org  
**Tip**: Check "Add Python to PATH" during installation

---

### "TensorFlow not detected"

**Solution**: Run `INSTALL.bat` again, or:
```
pip install tensorflow>=2.13.0
```

---

### "Port 5000 already in use"

**Solution**: Close other programs using port 5000, or:
1. Edit `web_ui.py`
2. Change line 242: `port=5000` to `port=5001`
3. Access dashboard at http://localhost:5001

---

### Dashboard shows no data

**Solution**: Run the pipeline first:
```
RUN_OVERNIGHT_PIPELINE.bat
```

Dashboard displays data from pipeline runs.

---

### Email not sending

**Check**:
1. Using Gmail App Password (not regular password)
2. Configuration saved in `screening_config.json`
3. Internet connection working

**Test**:
```
TEST_EMAIL.bat
```

---

## 📚 Next Steps

### Learn More

- **Full README**: `README.md`
- **🆕 Factor Analysis Guide**: `docs/FACTOR_VIEW_AND_BETAS.md` (v1.1)
- **🆕 Factor Examples**: `docs/FACTOR_ANALYSIS_EXAMPLES.md` (v1.1)
- **System Architecture**: `docs/SYSTEM_ARCHITECTURE.md`
- **Configuration Guide**: `docs/CONFIGURATION.md`
- **API Reference**: `docs/API_REFERENCE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

### Customize

- **Adjust LSTM parameters**: `models/config/screening_config.json`
- **Change dashboard port**: `web_ui.py` line 242
- **Add more stocks**: `models/config/stock_universe.json`
- **Modify email templates**: `models/screening/send_notification.py`

---

## 🎯 Summary

| Task | Command | Time |
|------|---------|------|
| **Install** | `INSTALL.bat` | 5-10 min |
| **First scan** | `RUN_OVERNIGHT_PIPELINE.bat` | 15-20 min |
| **Launch dashboard** | `START_WEB_UI.bat` | Instant |
| **Train LSTM (optional)** | `TRAIN_LSTM_OVERNIGHT_FIXED.bat` | 1.5-2 hrs |
| **Setup email (optional)** | Edit config + `TEST_EMAIL.bat` | 5 min |

---

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] Ran `INSTALL.bat` successfully
- [ ] Ran `RUN_OVERNIGHT_PIPELINE.bat` successfully
- [ ] Started web UI with `START_WEB_UI.bat`
- [ ] Accessed dashboard at http://localhost:5000
- [ ] 🆕 (v1.1) Reviewed factor analysis outputs in `reports/factor_view/`
- [ ] (Optional) Trained LSTM models
- [ ] (Optional) Configured email reports

---

**Everything working? You're ready to start analyzing stocks!** 📈

**Need help? See `docs/TROUBLESHOOTING.md` or check logs in `logs/screening/`**
