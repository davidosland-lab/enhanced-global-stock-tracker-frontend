# 🚀 Quick Start Guide - Event Risk Guard v1.0

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
- Generates HTML + CSV reports
- Creates dashboard data

**Expected output:**
```
========================================================================
OVERNIGHT STOCK SCREENING
========================================================================

Scanning 81 stocks across 10 sectors...
Progress: [██████████] 100%

✅ Scan completed in 18.5 minutes
✅ Reports saved to: reports/
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
- ✅ Monitor logs in `logs/screening/`

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
- [ ] (Optional) Trained LSTM models
- [ ] (Optional) Configured email reports

---

**Everything working? You're ready to start analyzing stocks!** 📈

**Need help? See `docs/TROUBLESHOOTING.md` or check logs in `logs/screening/`**
