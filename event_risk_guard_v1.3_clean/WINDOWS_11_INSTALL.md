# Windows 11 Installation Guide - Event Risk Guard v1.1

## 📦 Package Information

**File**: `event_risk_guard_v1.1_factor_analysis.zip`  
**Size**: ~175 KB (code only)  
**Version**: 1.1 Factor Analysis  
**Release Date**: 2025-11-17  
**All Fixes Applied**: ✅ Yes (10 from v1.0)  
**New Features**: 🆕 Factor View + Macro Betas (v1.1)

---

## ⚡ Quick Install (15 Minutes Total)

### Step 1: Extract ZIP (1 minute)

1. **Download** the ZIP file to your Downloads folder
2. **Right-click** on `event_risk_guard_v1.0_final.zip`
3. Select: **"Extract All..."**
4. Choose location: `C:\Users\YourName\AASS\`
5. Click: **"Extract"**

**Result**: Folder created at `C:\Users\YourName\AASS\event_risk_guard_v1.1_factor_analysis\`

---

### Step 2: Install Python Dependencies (5-10 minutes)

1. **Open** the extracted folder
2. **Double-click**: `INSTALL.bat`

**What it does**:
```
Installing Event Risk Guard dependencies...

📦 Installing core packages...
   ✓ tensorflow>=2.13.0
   ✓ transformers>=4.30.0
   ✓ flask>=2.3.0
   ✓ flask-cors>=4.0.0
   ✓ yfinance>=0.2.28
   [... 17 more packages ...]

✅ All packages installed successfully!
Press any key to continue...
```

**Download size**: ~2.5 GB  
**Install time**: 5-10 minutes  
**Disk space after**: ~4 GB  
**Note**: v1.1 uses same dependencies as v1.0 (no additional packages needed)

---

### Step 3: Test Installation (30 seconds)

Double-click: `VERIFY_INSTALLATION.bat`

**Expected output**:
```
Event Risk Guard - Installation Verification
============================================

✅ Python detected: 3.12.9
✅ TensorFlow installed: 2.20.0
✅ Transformers installed: 4.36.0
✅ Flask installed: 3.0.0
✅ All required packages present
✅ FinBERT model accessible
✅ Configuration files valid
✅ Directory structure correct

Installation Status: COMPLETE ✓
```

---

## 🎯 First Run (20 Minutes)

### Step 4: Run Stock Screening (15-20 minutes)

Double-click: `RUN_OVERNIGHT_PIPELINE.bat`

**What it does**:
- Scans 80-100 ASX stocks
- Downloads 2 years of price data
- Analyzes with FinBERT AI
- 🆕 Calculates macro betas (XJO, Lithium) - v1.1
- Calculates opportunity scores
- 🆕 Generates factor attribution analysis - v1.1
- Generates HTML + CSV reports

**Expected output**:
```
========================================================================
OVERNIGHT STOCK SCREENING - Event Risk Guard
========================================================================

Loading FinBERT model...
✓ FinBERT loaded (ProsusAI/finbert)

Scanning stocks...
[████████████████████] 100% (81/81 stocks)

Generating reports...
✓ HTML report: reports/html/2025-11-17_overnight_report.html
✓ CSV export: reports/csv/2025-11-17_scored_stocks.csv
✓ Dashboard data: reports/pipeline_state/2025-11-17_pipeline_state.json
✓ 🆕 Factor view (stocks): reports/factor_view/2025-11-17_factor_view_stocks.csv
✓ 🆕 Factor view (sectors): reports/factor_view/2025-11-17_factor_view_sector_summary.csv
✓ 🆕 Factor view (summary): reports/factor_view/2025-11-17_factor_view_summary.json

Scan completed in 19.2 minutes
Top opportunities: 18 stocks
Factor analysis: 3 files generated
```

---

### Step 5: Launch Dashboard (Instant)

Double-click: `START_WEB_UI.bat`

**Expected output**:
```
================================================================================
EVENT RISK GUARD - WEB UI
================================================================================

[INFO] Starting Flask web server...
[All FinBERT loading messages...]

================================================================================
Event Risk Guard - Web UI
================================================================================
Starting web server...
Access dashboard at: http://localhost:5000
================================================================================
 * Serving Flask app 'web_ui'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**Then open browser to**: http://localhost:5000

---

## ✅ Installation Complete!

You should now see:
- ✅ Dashboard loaded in browser
- ✅ Top 10 opportunities displayed
- ✅ System status showing "Active"
- ✅ Latest report available

---

## 🔧 Windows 11 Specific Notes

### User Account Control (UAC)

If you see UAC prompts:
- ✅ Click **"Yes"** when asked to allow Python
- ✅ This is normal for first-time Python installations
- ✅ Only needed once

### Windows Defender

If SmartScreen blocks batch files:
1. Click: **"More info"**
2. Click: **"Run anyway"**
3. Batch files are safe (open in Notepad to review code)

### Windows Firewall

If asked to allow Python network access:
- ✅ Check: **"Private networks"**
- ✅ Click: **"Allow access"**
- This allows the web dashboard to work

---

## 📁 Folder Structure (After Install)

```
C:\Users\YourName\AASS\event_risk_guard_v1.1_factor_analysis\
│
├── 📋 DOCUMENTATION
│   ├── README.md                      Main guide
│   ├── QUICK_START.md                 5-minute setup
│   ├── CHANGELOG.md                   Version history
│   ├── RELEASE_NOTES_v1.1.md          🆕 What's new in v1.1
│   └── WINDOWS_11_INSTALL.md          This file
│
├── ⚡ BATCH FILES (Double-click to run)
│   ├── INSTALL.bat                    ← Run first
│   ├── VERIFY_INSTALLATION.bat        ← Run second
│   ├── RUN_OVERNIGHT_PIPELINE.bat     ← Run third
│   ├── START_WEB_UI.bat               ← Run fourth
│   ├── TRAIN_LSTM_SINGLE.bat          (Optional)
│   ├── TRAIN_LSTM_OVERNIGHT_FIXED.bat (Optional)
│   ├── TRAIN_LSTM_CUSTOM.bat          (Optional)
│   ├── TEST_FINBERT.bat               (Optional test)
│   └── TEST_EMAIL.bat                 (Optional test)
│
├── 🐍 PYTHON FILES
│   ├── web_ui.py                      Flask web server (FIXED)
│   ├── train_lstm_batch.py            LSTM training
│   ├── train_lstm_custom.py           Custom training
│   └── requirements.txt               Dependencies list
│
├── 📁 DIRECTORIES
│   ├── models/                        Core system code
│   │   └── screening/                 Stock scanning modules
│   │       ├── factor_view.py         🆕 Factor builder (v1.1)
│   │       └── macro_beta.py          🆕 Beta calculator (v1.1)
│   ├── templates/                     Web UI HTML
│   ├── static/                        CSS + JavaScript
│   ├── reports/                       Output files (created)
│   ├── logs/                          System logs (created)
│   └── docs/                          Documentation
│       ├── FACTOR_VIEW_AND_BETAS.md   🆕 Factor guide (v1.1)
│       └── FACTOR_ANALYSIS_EXAMPLES.md🆕 Examples (v1.1)
│
└── 📊 REPORTS (Created after first run)
    ├── reports/html/                  HTML reports
    ├── reports/csv/                   CSV exports
    ├── reports/pipeline_state/        Dashboard data (JSON)
    ├── reports/factor_view/           🆕 Factor analysis (v1.1)
    │   ├── *_factor_view_stocks.csv   Per-stock breakdown
    │   ├── *_factor_view_sector_summary.csv  Sector aggregations
    │   └── *_factor_view_summary.json Portfolio stats
    └── logs/screening/                Pipeline logs
```

---

## 🎓 Optional: LSTM Training

LSTM models improve prediction accuracy but take 1.5-2 hours to train.

**Skip this if you want to use the system right away.**

### Quick Test (10-15 minutes)

Train one stock to test:
```
TRAIN_LSTM_SINGLE.bat CBA.AX
```

### Full Training (1.5-2 hours)

Train 10 major ASX stocks:
```
TRAIN_LSTM_OVERNIGHT_FIXED.bat
```

**Recommendation**: Run this overnight once installed.

---

## 📧 Optional: Email Configuration

### Get Gmail App Password

1. Visit: https://myaccount.google.com/apppasswords
2. Sign in to your Gmail account
3. Select:
   - App: **Mail**
   - Device: **Windows Computer**
4. Click: **Generate**
5. **Copy** the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Update Configuration

1. Navigate to: `models\config\`
2. Open: `screening_config.json` (in Notepad)
3. Find the `email_notifications` section
4. Update these fields:

```json
{
  "email_notifications": {
    "enabled": true,
    "smtp_username": "your-email@gmail.com",
    "smtp_password": "abcd efgh ijkl mnop",
    "sender_email": "your-email@gmail.com",
    "recipient_emails": [
      "your-email@gmail.com",
      "another-email@example.com"
    ]
  }
}
```

5. **Save** the file (Ctrl+S)

### Test Email

Double-click: `TEST_EMAIL.bat`

**Expected**:
```
Testing email configuration...
✓ Email sent successfully!
Check your inbox for test email.
```

---

## 🔄 Daily Usage (Windows 11)

### Automated Schedule (Recommended)

Use **Windows Task Scheduler** to automate:

**1. Schedule Morning Scan**
```
Task: Run Overnight Pipeline
Trigger: Daily at 7:00 AM
Action: C:\Users\...\event_risk_guard_v1.1_factor_analysis\RUN_OVERNIGHT_PIPELINE.bat
```

**2. Auto-start Dashboard**
```
Task: Start Web UI
Trigger: At startup (optional: only when logged in)
Action: C:\Users\...\event_risk_guard_v1.1_factor_analysis\START_WEB_UI.bat
```

**3. Weekly LSTM Training**
```
Task: Train LSTM Models
Trigger: Weekly, Sunday, 11:00 PM
Action: C:\Users\...\event_risk_guard_v1.1_factor_analysis\TRAIN_LSTM_OVERNIGHT_FIXED.bat
```

### Manual Workflow

**Each morning**:
```
1. Double-click: RUN_OVERNIGHT_PIPELINE.bat (15-20 min)
2. Double-click: START_WEB_UI.bat (instant)
3. Open browser: http://localhost:5000
4. Review opportunities
```

---

## 🐛 Troubleshooting (Windows 11)

### Python Not Found

**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Install Python from https://python.org
2. During installation, check: ✅ **"Add Python to PATH"**
3. Restart Command Prompt
4. Test: `python --version`

---

### Port 5000 Already in Use

**Error**: `OSError: [WinError 10048] Only one usage of each socket address`

**Solution 1**: Close iTunes (uses port 5000 on Windows)

**Solution 2**: Find and kill process
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

**Solution 3**: Change port
1. Open `web_ui.py` in Notepad
2. Line 242: Change `port=5000` to `port=5001`
3. Save and restart
4. Access: http://localhost:5001

---

### No Data on Dashboard

**Cause**: Pipeline hasn't run yet

**Solution**: Run `RUN_OVERNIGHT_PIPELINE.bat` first

---

### Email Not Sending

**Check**:
1. ✅ Using Gmail **App Password** (not regular password)
2. ✅ Configuration saved in `screening_config.json`
3. ✅ Internet connection working

**Test**: `TEST_EMAIL.bat`

---

### Antivirus Blocking

If Windows Defender or antivirus blocks Python:

**Solution**:
1. Open Windows Security
2. Virus & threat protection → Manage settings
3. Exclusions → Add an exclusion
4. Choose: **Folder**
5. Select: `C:\Users\YourName\AASS\event_risk_guard_v1.1_factor_analysis`

---

## 🆕 What's New in v1.1

### New Features (v1.1)

✅ **Factor Attribution Analysis**
- Breaks down opportunity scores into 6 constituent factors
- Shows which factors drive each stock's score
- Generates per-stock and sector-level breakdowns
- Exports to CSV + JSON for Excel/Python analysis

✅ **Macro Beta Calculator**
- Calculates stock sensitivity to market factors (OLS regression)
- Default factors: ASX 200 (XJO), Lithium commodity
- 90-day lookback period with statistical validation
- Identifies defensive (beta < 1.0) vs aggressive (beta > 1.0) stocks

✅ **Enhanced Output Files**
- Per-stock factor breakdown CSV (~25 KB per run)
- Sector summary CSV with aggregations (~2 KB per run)
- Portfolio summary JSON for automation (~5 KB per run)
- Total: ~32 KB additional storage per run

✅ **100% Backwards Compatible**
- All v1.0 functionality preserved
- No breaking changes
- Optional features (system works without factor view)

### All v1.0 Fixes Included

All 10 fixes from v1.0 are included in v1.1:

✅ **Fix #1**: LSTM Single training variable issue  
✅ **Fix #2**: LSTM Overnight TensorFlow check  
✅ **Fix #3**: Web UI Unicode decode error  
✅ **Fix #4**: FinBERT full AI mode  
✅ **Fix #5-10**: Module imports and configuration

**All batch files work correctly on Windows 11!**

---

## 📊 System Requirements (Windows 11)

### Minimum
- **OS**: Windows 11 (64-bit)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 10 GB free
- **Internet**: Broadband

### Recommended
- **OS**: Windows 11 Pro (64-bit)
- **CPU**: 6+ cores
- **RAM**: 16 GB
- **Disk**: 20 GB free (SSD)
- **Internet**: Fast broadband (for downloads)

### Storage Impact (v1.1)

**Additional storage for factor analysis:**
- Per run: ~32 KB (3 new files)
- Daily usage (30 runs): ~960 KB (~1 MB/month)
- Annual usage (365 runs): ~11.4 MB/year

**Conclusion**: Negligible storage impact

---

## 🎯 Success Checklist

After installation, you should have:

- [ ] Python 3.8+ installed
- [ ] All packages installed (INSTALL.bat completed)
- [ ] Installation verified (VERIFY_INSTALLATION.bat passed)
- [ ] First scan completed (RUN_OVERNIGHT_PIPELINE.bat finished)
- [ ] Dashboard accessible (http://localhost:5000 shows data)
- [ ] (Optional) LSTM models trained
- [ ] (Optional) Email configured and tested

---

## 📞 Getting Help

If something doesn't work:

1. **Check logs**: `logs\screening\overnight_pipeline.log`
2. **Run diagnostic**: `VERIFY_INSTALLATION.bat`
3. **Review troubleshooting**: `docs\TROUBLESHOOTING.md`
4. **Check README**: `README.md` for detailed info

---

## 🎉 Installation Complete!

**Your Event Risk Guard system is ready to use on Windows 11.**

**Quick access**:
- Dashboard: http://localhost:5000
- Reports: `reports\html\`
- Logs: `logs\screening\`
- Config: `models\config\screening_config.json`

**Happy trading!** 📈
