# Installation Guide - Complete Setup
**Phase 3 Trading System - All Dependencies**  
**Version: 1.3.5**  
**Date: January 1, 2026**

---

## 📦 **Complete Requirements**

Your trading system needs these Python packages to run all features.

---

## 🚀 **Quick Install (Recommended)**

### **Option 1: Install from requirements.txt**

```bash
cd C:\Users\david\Trading\phase3_intraday_deployment
pip install -r requirements.txt
```

This will install all required packages automatically.

---

## 📋 **Manual Installation (If Needed)**

If you prefer to install packages individually or troubleshoot specific issues:

### **Core Dependencies (Required)**

```bash
# Data processing
pip install pandas>=2.0.0
pip install numpy>=1.24.0

# Market data
pip install yahooquery>=2.3.0
pip install yfinance>=0.2.0

# Web/API
pip install requests>=2.31.0
pip install beautifulsoup4>=4.12.0

# Dashboard (Essential for unified dashboard)
pip install dash>=2.14.0
pip install plotly>=5.18.0

# Timezone support (Essential for market calendar)
pip install pytz

# Web framework
pip install flask>=3.0.0

# Machine Learning
pip install scikit-learn>=1.3.0
```

### **Optional Dependencies**

```bash
# Notifications (Optional - only if you want alerts)
pip install python-telegram-bot>=20.0
pip install twilio>=8.0.0

# Live trading (Optional - only for real broker integration)
pip install alpaca-trade-api>=3.0.0

# Deep Learning (Optional - only if you want TensorFlow models)
pip install tensorflow>=2.15.0
```

---

## 🔍 **Minimal Requirements (Audit System)**

If you only want to audit/test the system without full ML:

```bash
# Minimum required packages
pip install pandas numpy
pip install yahooquery yfinance
pip install dash plotly
pip install pytz
pip install flask
pip install requests beautifulsoup4
pip install scikit-learn
```

---

## ✅ **Verify Installation**

After installing, verify everything is working:

### **Test 1: Basic Imports**

```bash
python -c "import pandas; import numpy; import dash; import plotly; import pytz; print('✅ Core packages installed')"
```

### **Test 2: Market Data**

```bash
python -c "import yfinance; import yahooquery; print('✅ Market data packages installed')"
```

### **Test 3: Market Calendar**

```bash
cd C:\Users\david\Trading
python -c "from ml_pipeline.market_calendar import MarketCalendar; cal = MarketCalendar(); print('✅ Market calendar working')"
```

### **Test 4: Dashboard**

```bash
cd C:\Users\david\Trading\phase3_intraday_deployment
python -c "import dash; from dash import dcc, html; print('✅ Dashboard packages installed')"
```

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: pip not found**

**Error:**
```
'pip' is not recognized as an internal or external command
```

**Solution:**
```bash
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### **Issue 2: Permission Denied**

**Error:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solution:**
```bash
# Install for current user only
pip install --user -r requirements.txt
```

### **Issue 3: SSL Certificate Error**

**Error:**
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solution:**
```bash
# Temporary workaround (use with caution)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### **Issue 4: pytz not found**

**Error:**
```
ModuleNotFoundError: No module named 'pytz'
```

**Solution:**
```bash
pip install pytz
```

### **Issue 5: Dash not found**

**Error:**
```
ModuleNotFoundError: No module named 'dash'
```

**Solution:**
```bash
pip install dash plotly
```

### **Issue 6: Conflicting Versions**

**Error:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

---

## 🔧 **Advanced Installation**

### **Virtual Environment (Recommended)**

Create an isolated Python environment:

```bash
# Create virtual environment
python -m venv trading_env

# Activate it
# Windows:
trading_env\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### **Upgrade Existing Packages**

```bash
# Upgrade all packages to latest versions
pip install --upgrade -r requirements.txt
```

### **Check Installed Versions**

```bash
# List all installed packages
pip list

# Check specific package version
pip show pandas
pip show dash
pip show pytz
```

---

## 📊 **Package Size & Download Time**

Approximate sizes:

| Package | Size | Purpose |
|---------|------|---------|
| pandas | ~50 MB | Data processing |
| numpy | ~20 MB | Numerical computing |
| dash | ~10 MB | Dashboard UI |
| plotly | ~30 MB | Charts/graphs |
| yfinance | ~5 MB | Market data |
| yahooquery | ~3 MB | Market data |
| pytz | ~500 KB | Timezone support |
| scikit-learn | ~30 MB | Machine learning |
| tensorflow | ~500 MB | Deep learning (optional) |

**Total (without TensorFlow):** ~150 MB  
**Total (with TensorFlow):** ~650 MB  
**Download time:** 2-10 minutes (depending on internet speed)

---

## 🎯 **Recommended Installation Order**

Install in this order to avoid dependency issues:

```bash
# Step 1: Upgrade pip
python -m pip install --upgrade pip

# Step 2: Core data processing
pip install numpy pandas

# Step 3: Market data
pip install yfinance yahooquery

# Step 4: Web/Dashboard
pip install flask dash plotly

# Step 5: Utilities
pip install pytz requests beautifulsoup4

# Step 6: Machine Learning
pip install scikit-learn

# Step 7: Optional - Deep Learning
pip install tensorflow

# Step 8: Optional - Notifications
pip install python-telegram-bot twilio

# Step 9: Optional - Live Trading
pip install alpaca-trade-api
```

---

## 📝 **Create Your Own Requirements File**

If you want to save your exact versions:

```bash
# Save current environment
pip freeze > my_requirements.txt

# Install from saved file
pip install -r my_requirements.txt
```

---

## 🔍 **Audit-Only Installation**

If you only want to audit/review the system without running it:

```bash
# Minimum packages for code review
pip install pandas numpy pytz
```

This allows you to:
- Read the code
- Understand the logic
- Test individual functions
- Review the market calendar

But you won't be able to:
- Run the dashboard
- Execute trades (even paper trading)
- View charts

---

## 🧪 **Testing After Installation**

### **Complete System Test**

```bash
# Test 1: Market Calendar
cd C:\Users\david\Trading
python ml_pipeline/market_calendar.py

# Test 2: ML Stack (if installed)
python test_ml_stack.py

# Test 3: Dashboard
cd phase3_intraday_deployment
python unified_trading_dashboard.py
# Open: http://localhost:8050
```

### **Individual Component Tests**

```bash
# Test imports
python -c "
import pandas as pd
import numpy as np
import dash
from dash import dcc, html
import plotly.graph_objs as go
import pytz
import yfinance as yf
from yahooquery import Ticker
print('✅ All imports successful!')
"
```

---

## 💾 **Offline Installation**

If you need to install without internet:

### **Step 1: Download Packages**

On a computer with internet:
```bash
pip download -r requirements.txt -d packages/
```

### **Step 2: Transfer Files**

Copy the `packages/` folder to your offline computer.

### **Step 3: Install Offline**

```bash
pip install --no-index --find-links=packages/ -r requirements.txt
```

---

## 🔄 **Uninstall & Clean Reinstall**

If you need to start fresh:

```bash
# Uninstall specific package
pip uninstall dash

# Uninstall all packages from requirements
pip uninstall -r requirements.txt -y

# Clean pip cache
pip cache purge

# Reinstall everything
pip install -r requirements.txt
```

---

## 📞 **Getting Help**

### **Check Package Documentation**

- **Dash:** https://dash.plotly.com/
- **Pandas:** https://pandas.pydata.org/
- **yfinance:** https://github.com/ranaroussi/yfinance
- **pytz:** https://pypi.org/project/pytz/

### **Common Commands**

```bash
# Check Python version
python --version

# Check pip version
pip --version

# Get help on a package
pip show dash
pip help install

# List outdated packages
pip list --outdated

# Search for a package
pip search pandas
```

---

## ✅ **Installation Complete Checklist**

After installation, verify:

- [ ] All packages installed without errors
- [ ] `python -c "import dash"` works
- [ ] `python -c "import pytz"` works
- [ ] `python -c "import pandas"` works
- [ ] Market calendar test passes
- [ ] Dashboard starts without errors
- [ ] Browser can open http://localhost:8050
- [ ] No red error messages in terminal

---

## 🎊 **You're Ready!**

Once all packages are installed:

```bash
# Start the unified dashboard
cd C:\Users\david\Trading\phase3_intraday_deployment
START_UNIFIED_DASHBOARD.bat

# Or manually:
python unified_trading_dashboard.py
```

Then open: **http://localhost:8050**

---

## 📦 **Quick Reference**

**Minimum packages (audit only):**
```bash
pip install pandas numpy pytz
```

**Core packages (dashboard):**
```bash
pip install pandas numpy dash plotly pytz yfinance yahooquery flask requests beautifulsoup4 scikit-learn
```

**Full system (everything):**
```bash
pip install -r requirements.txt
```

---

**Happy Trading! 🚀📊💰**
