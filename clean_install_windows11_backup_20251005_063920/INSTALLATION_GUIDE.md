# 📦 Windows 11 Installation Guide

## Stock Tracker Pro v7.0 - Clean Installation

### Prerequisites

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, CHECK "Add Python to PATH"
   - Verify: Open CMD and type `python --version`

2. **Modern Web Browser**
   - Chrome (recommended)
   - Edge
   - Firefox

3. **System Requirements**
   - Windows 11 (64-bit)
   - 4GB RAM minimum (8GB for ML features)
   - 2GB free disk space

### Step-by-Step Installation

#### Step 1: Extract Package
1. Download the `clean_install_windows11.zip`
2. Extract to your desired location:
   - Recommended: `C:\StockTracker`
   - Or: `C:\Users\[YourName]\Documents\StockTracker`
3. Navigate to the extracted folder

#### Step 2: Open Terminal
1. Open Windows Terminal or Command Prompt
2. Navigate to the installation folder:
   ```cmd
   cd C:\StockTracker
   ```

#### Step 3: Install Dependencies
```cmd
pip install -r requirements.txt
```

If you encounter permission errors:
```cmd
pip install --user -r requirements.txt
```

#### Step 4: Launch Application

##### Option A: One-Click Launch (Recommended)
Double-click `START_WINDOWS.bat` in the installation folder

##### Option B: PowerShell Launch
1. Right-click on PowerShell → Run as Administrator
2. Navigate to folder: `cd C:\StockTracker`
3. Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
4. Run: `.\START_WINDOWS.ps1`

##### Option C: Manual Launch
1. Open two terminal windows
2. In first terminal:
   ```cmd
   python backend.py
   ```
3. In second terminal:
   ```cmd
   python backend_ml_enhanced.py
   ```
4. Open browser: http://localhost:8002

### Troubleshooting

#### Python Not Found
- Ensure Python is installed
- Add Python to PATH manually:
  1. Search "Environment Variables" in Windows
  2. Edit System Environment Variables
  3. Add Python installation path (usually `C:\Users\[YourName]\AppData\Local\Programs\Python\Python3X\`)

#### Port Already in Use
```cmd
# Find process using port
netstat -ano | findstr :8002

# Kill process (replace PID with actual number)
taskkill /PID [PID] /F
```

#### Module Import Errors
```cmd
# Upgrade pip
python -m pip install --upgrade pip

# Reinstall requirements
pip install --force-reinstall -r requirements.txt
```

#### Windows Defender/Firewall Blocking
1. Windows Security → Firewall & network protection
2. Allow an app → Python.exe
3. Check both Private and Public networks

#### Browser Issues
- Clear cache: Ctrl + Shift + Delete
- Hard refresh: Ctrl + Shift + R
- Try incognito/private mode
- Disable browser extensions

### Verification

1. **Check Backend Status:**
   - Main: http://localhost:8002/
   - ML: http://localhost:8004/health

2. **Run Diagnostic Tool:**
   - http://localhost:8002/diagnostic_tool.html

3. **Test API Endpoints:**
   - http://localhost:8002/test_api.html

### Quick Commands Reference

| Action | Command |
|--------|---------|
| Start servers | `START_WINDOWS.bat` |
| Stop servers | `Ctrl + C` in terminal |
| Update packages | `pip install --upgrade -r requirements.txt` |
| Check Python | `python --version` |
| Check pip | `pip --version` |
| List packages | `pip list` |

### Features Overview

✅ **Working Modules:**
- Technical Analysis with candlestick charts
- Market Tracker (ASX, FTSE, S&P 500)
- ML Prediction Centre (8 models)
- CBA Analysis Module

✅ **Data Sources:**
- Real Yahoo Finance data
- No synthetic/mock data
- High-frequency intervals (1m-1mo)

✅ **ML Models:**
- LSTM, GRU, Random Forest
- XGBoost, Transformer, GNN
- TFT, Ensemble
- Real backtesting

### Support Resources

1. **Diagnostic Tool:** Check system status
2. **API Tester:** Verify endpoints
3. **Console Logs:** Press F12 in browser
4. **Error Logs:** Check terminal output

### Performance Tips

1. **Close unnecessary apps** to free RAM
2. **Use Chrome** for best performance
3. **Keep only needed tabs open**
4. **Regular cache clearing** monthly
5. **Update Python packages** quarterly

### Security Notes

- Application runs locally only
- No external data sharing
- Yahoo Finance API is read-only
- All processing on your machine

---

## Quick Start Summary

1. Extract package → `C:\StockTracker`
2. Install dependencies → `pip install -r requirements.txt`
3. Launch → Double-click `START_WINDOWS.bat`
4. Open browser → http://localhost:8002

**That's it! You're ready to use Stock Tracker Pro!**