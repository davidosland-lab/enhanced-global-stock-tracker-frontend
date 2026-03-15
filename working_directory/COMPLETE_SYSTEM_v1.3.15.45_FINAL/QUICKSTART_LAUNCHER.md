# 🚀 QUICK START GUIDE

## ⚡ Fastest Way to Get Started

### **Option 1: Smart Launcher (RECOMMENDED)** ⭐

The easiest way to use the system:

```cmd
LAUNCH_COMPLETE_SYSTEM.bat
```

**This single file does everything:**
- ✅ First-time setup (only once)
  - Creates virtual environment
  - Installs PyTorch CPU version (avoids conflicts)
  - Installs all dependencies
  - Downloads FinBERT model
- ✅ Interactive menu with options:
  1. Run AU Overnight Pipeline
  2. Run US Overnight Pipeline
  3. Run UK Overnight Pipeline
  4. Run All Markets
  5. Start Paper Trading
  6. View System Status
  7. Start Unified Dashboard
  8. Basic Dashboard
  9. Advanced Options
  0. Exit

**First time:** Takes 5-10 minutes to install everything  
**After that:** Instant menu access

---

### **Option 2: Manual Installation**

If you prefer step-by-step:

```cmd
REM Step 1: Install (one time only)
INSTALL.bat

REM Step 2: Start trading
START_UNIFIED_DASHBOARD.bat
```

---

## 📖 What Each File Does

### **LAUNCH_COMPLETE_SYSTEM.bat** ⭐ (RECOMMENDED)
The **all-in-one solution**:
- Detects first-time vs repeat usage
- Installs everything automatically on first run
- Presents menu with all options
- Handles virtual environment automatically
- **Use this file every time you want to use the system**

### **INSTALL.bat**
Manual installation script:
- Creates virtual environment
- Installs dependencies
- Downloads FinBERT model
- Run this once, then use other scripts

### **START_UNIFIED_DASHBOARD.bat**
Starts just the dashboard:
- Activates virtual environment
- Checks dependencies
- Starts unified trading dashboard
- Opens http://localhost:8050

---

## 🎯 Typical Workflow

### **Daily Use (Simple)**

```cmd
# Just double-click this file every day:
LAUNCH_COMPLETE_SYSTEM.bat

# Then select from menu:
# - Option 1: Run AU Pipeline (before market opens)
# - Option 7: Start Dashboard (to monitor trading)
```

That's it! The launcher handles everything.

---

### **Daily Use (Detailed)**

#### **Morning (Before Market Opens)**

```cmd
# 1. Run the launcher
LAUNCH_COMPLETE_SYSTEM.bat

# 2. Select your market pipeline:
#    - Option 1 for AU (Australian market)
#    - Option 2 for US (American market)
#    - Option 3 for UK (London market)
#    - Option 4 for ALL markets

# Wait 15-20 minutes for pipeline to complete
# This generates morning report with sentiment analysis
```

#### **Market Hours (During Trading)**

```cmd
# From the same launcher menu:
#    - Option 7: Start Unified Dashboard

# Or use the direct launcher:
START_UNIFIED_DASHBOARD.bat

# Dashboard shows:
# - FinBERT sentiment panel
# - Trading gates (BLOCK/REDUCE/CAUTION/ALLOW)
# - Live positions
# - Market status
# - Performance charts
```

---

## 🔧 Advanced Options

### **Menu Option 5: Paper Trading**

Starts automated paper trading:
- Uses morning pipeline signals
- Respects sentiment gates
- Manages positions automatically
- Runs in background

### **Menu Option 6: System Status**

Shows:
- Python version
- Virtual environment status
- Installed dependencies
- Recent reports
- Trading state

### **Menu Option 9: Advanced Options**
- Reinstall dependencies
- Clear logs
- Reset trading state
- View recent logs

---

## 📁 Important Files

### **Batch Files (Windows)**
```
LAUNCH_COMPLETE_SYSTEM.bat     ← Use this (all-in-one)
INSTALL.bat                    ← One-time setup
START_UNIFIED_DASHBOARD.bat    ← Dashboard only
START_PAPER_TRADING.bat        ← Trading only
```

### **Python Scripts**
```
run_au_pipeline_v1.3.13.py     ← AU overnight pipeline
run_us_full_pipeline.py        ← US overnight pipeline
run_uk_full_pipeline.py        ← UK overnight pipeline
unified_trading_dashboard.py   ← Main dashboard
paper_trading_coordinator.py   ← Trading engine
```

### **Generated Files**
```
reports/screening/             ← Morning reports
logs/                          ← Log files
state/                         ← Trading state
venv/                          ← Virtual environment
```

---

## ✅ Verification

After first-time setup, verify everything works:

### **Check 1: Virtual Environment**
```cmd
# Should see (venv) in prompt after activation
venv\Scripts\activate
```

### **Check 2: Dependencies**
```cmd
python -c "import dash, transformers, torch; print('OK')"
```

### **Check 3: FinBERT**
```cmd
python -c "from sentiment_integration import IntegratedSentimentAnalyzer; print('OK')"
```

### **Check 4: Dashboard**
```cmd
python unified_trading_dashboard.py
# Should start without errors
# Open http://localhost:8050
```

---

## 🐛 Troubleshooting

### **Issue: Launcher doesn't start**

**Solution**: Run as Administrator
```cmd
Right-click LAUNCH_COMPLETE_SYSTEM.bat → Run as Administrator
```

### **Issue: "Python not found"**

**Solution**: Install Python 3.8+
- Download from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation

### **Issue: Dependencies fail to install**

**Solution**: The launcher will retry with core packages
- If still failing, check internet connection
- Try running as Administrator

### **Issue: FinBERT model download fails**

**Solution**: Model will download on first use
- Or manually: Run menu Option 9 → Reinstall dependencies

### **Issue: Dashboard shows "FinBERT data loading..."**

**Solution**: Run pipeline first
- Menu Option 1 (AU Pipeline)
- Wait for completion
- Then start dashboard (Option 7)

---

## 💡 Tips

### **Tip 1: Always Use the Launcher**

Don't run Python scripts directly. Use:
```cmd
LAUNCH_COMPLETE_SYSTEM.bat
```

This ensures:
- Virtual environment is activated
- Dependencies are installed
- Everything is set up correctly

### **Tip 2: Run Pipelines Before Market Open**

Best practice:
1. Morning: Run overnight pipeline
2. Market hours: Start dashboard
3. Monitor trading during the day

### **Tip 3: Check System Status**

Before trading, check:
```cmd
LAUNCH_COMPLETE_SYSTEM.bat → Option 6
```

Verify:
- Virtual environment is active
- Dependencies are installed
- Recent pipeline reports exist

### **Tip 4: Keep Logs Clean**

Periodically:
```cmd
LAUNCH_COMPLETE_SYSTEM.bat → Option 9 → Option 2
```

This clears old log files.

---

## 📊 What the Launcher Does (Technical)

### **First-Time Setup**
1. Checks for `.system_installed` marker
2. If not found:
   - Verifies Python installation
   - Creates virtual environment in `venv/`
   - Activates virtual environment
   - Upgrades pip
   - Installs PyTorch CPU version (no DLL conflicts)
   - Installs transformers, dash, plotly, etc.
   - Creates required directories
   - Creates `.system_installed` marker

### **Subsequent Runs**
1. Detects `.system_installed` marker
2. Activates virtual environment
3. Verifies core dependencies
4. Shows interactive menu

### **Menu Options**
- Execute Python scripts with proper environment
- Show real-time progress
- Handle errors gracefully
- Provide helpful messages

---

## 🎉 Summary

### **For First-Time Users**

```cmd
# 1. Extract ZIP to a folder
# 2. Double-click this file:
LAUNCH_COMPLETE_SYSTEM.bat

# 3. Wait 5-10 minutes for first-time setup
# 4. Menu appears - select what you want to do
```

### **For Daily Use**

```cmd
# Just double-click this file:
LAUNCH_COMPLETE_SYSTEM.bat

# Select from menu:
# - Morning: Option 1 (Run AU Pipeline)
# - Trading: Option 7 (Start Dashboard)
```

### **That's It!**

No manual steps. No command line knowledge needed.  
The launcher handles everything automatically. 🚀

---

**System Version**: v1.3.15.45 FINAL  
**Launcher Version**: Smart Launcher with Auto-Setup  
**FinBERT**: v4.4.4 (Integrated with Sentiment Gates)
