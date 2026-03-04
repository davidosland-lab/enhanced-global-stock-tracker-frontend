# Manual Installation Guide - v1.3.11 Patch

**Use this guide if the automated installers hang or fail.**

---

## 🛠️ Manual Installation Steps

### Step 1: Stop the Dashboard

**Close the dashboard window** or press `Ctrl+C` in the command prompt where it's running.

**Alternative - Force kill:**
```batch
REM Open Command Prompt as Administrator
taskkill /F /IM python.exe
```

Wait 5 seconds to ensure the process has stopped.

---

### Step 2: Locate Your Installation

Navigate to your Phase 3 Trading System installation directory.

**Default location:**
```
C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment
```

**Find it:**
1. Open File Explorer
2. Navigate to the folder where you installed the trading system
3. Look for the `phase3_intraday_deployment` folder
4. Inside, you should see `unified_trading_dashboard.py`

---

### Step 3: Backup Current File

**IMPORTANT: Create a backup before making changes!**

1. In File Explorer, navigate to:
   ```
   C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment
   ```

2. Find the file: `unified_trading_dashboard.py`

3. **Right-click** the file → **Copy**

4. **Right-click** in the empty space → **Paste**

5. **Rename** the copy to: `unified_trading_dashboard.py.v1.3.10.backup`

**Now you have a backup!**

---

### Step 4: Extract Patch Package

1. Navigate to where you downloaded: `v1.3.11_calibration_patch.zip`

2. **Right-click** the ZIP file → **Extract All...**

3. Extract to a temporary folder (e.g., `C:\Temp\v1.3.11_patch\`)

4. You should now see:
   ```
   C:\Temp\v1.3.11_patch\
   ├── README.md
   ├── VERSION.md
   ├── PATCH_INSTALLATION_GUIDE.md
   ├── V1.3.11_CALIBRATION_FIX.md
   ├── INSTALL_PATCH.bat
   ├── install_patch.sh
   └── phase3_intraday_deployment\
       └── unified_trading_dashboard.py  ← THIS IS THE NEW FILE
   ```

---

### Step 5: Copy New File

1. Navigate to the extracted patch folder:
   ```
   C:\Temp\v1.3.11_patch\phase3_intraday_deployment\
   ```

2. **Copy** the file: `unified_trading_dashboard.py`

3. Navigate to your installation folder:
   ```
   C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment\
   ```

4. **Paste** the file (this will replace the old one)

5. When prompted **"Replace the file in the destination?"**
   - Click **Yes** or **Replace**

---

### Step 6: Verify File Replacement

1. In your installation folder, **right-click** `unified_trading_dashboard.py`

2. Select **Properties**

3. Check the **Date modified** - it should show **today's date**

4. Check the **Size** - should be around **46-48 KB**

**If the date and size are correct, the patch is installed!**

---

### Step 7: Restart Dashboard

**Option A - Using Batch Script:**
```batch
1. Navigate to: C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment
2. Double-click: START_UNIFIED_DASHBOARD.bat
```

**Option B - Using Command Prompt:**
```batch
cd C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment
python unified_trading_dashboard.py
```

**Wait for startup message:**
```
Dash is running on http://0.0.0.0:8050/
```

---

### Step 8: Verify Installation

1. **Open browser** and go to: `http://localhost:8050`

2. **Look at the Market Performance chart** (top right area)

3. **Hover over any line** on the chart

4. **Check the tooltip** - it should now show:
   ```
   NASDAQ
   Time (GMT): 14:30
   Change from Prev Close: -0.03%  ← NEW TEXT!
   ```

5. **Compare percentages** with Yahoo Finance or Bloomberg:
   - Dashboard should now match official figures ✅

---

## ✅ Verification Checklist

After installation, confirm:

- [ ] Dashboard starts without errors
- [ ] Chart displays 4 indices (ASX, S&P, NASDAQ, FTSE)
- [ ] Hover tooltip shows **"Change from Prev Close"**
- [ ] NASDAQ % matches Yahoo Finance
- [ ] S&P 500 % matches Bloomberg
- [ ] FTSE 100 % matches LSE official figures
- [ ] Chart auto-refreshes every 5 seconds
- [ ] No console errors

**If all checks pass → Installation successful! ✅**

---

## 🔄 Rollback (If Needed)

If something goes wrong, restore your backup:

1. Stop the dashboard (Ctrl+C or close window)

2. Navigate to your installation folder

3. Delete the current `unified_trading_dashboard.py`

4. Rename `unified_trading_dashboard.py.v1.3.10.backup` to `unified_trading_dashboard.py`

5. Restart dashboard

**You're back to v1.3.10!**

---

## 🐛 Troubleshooting

### Issue: Can't find unified_trading_dashboard.py

**Solution:**
```batch
REM Search for the file
dir /s unified_trading_dashboard.py

REM This will show you where it is located
```

### Issue: "Permission denied" when copying

**Solution:**
1. Close the dashboard completely
2. Run Command Prompt as **Administrator**
3. Try the copy again

### Issue: Dashboard won't start after patch

**Solution:**
1. Check for syntax errors:
   ```batch
   python -m py_compile unified_trading_dashboard.py
   ```

2. If errors appear, restore backup:
   ```batch
   copy unified_trading_dashboard.py.v1.3.10.backup unified_trading_dashboard.py
   ```

3. Restart dashboard

### Issue: Chart still shows wrong percentages

**Solution:**
1. **Clear browser cache:** Press `Ctrl+F5` in browser
2. **Verify file date:** Check that unified_trading_dashboard.py was modified today
3. **Restart dashboard:** Close completely and restart
4. **Check file integrity:** Compare file size (should be ~47 KB)

### Issue: "Module not found" errors

**Solution:**
```batch
REM Reinstall dependencies
pip install --upgrade yfinance plotly dash pytz pandas numpy
```

---

## 📞 Still Having Issues?

### Check These:

1. **Python version:** Must be 3.8 or higher
   ```batch
   python --version
   ```

2. **Dependencies installed:**
   ```batch
   pip list | findstr yfinance
   pip list | findstr plotly
   pip list | findstr dash
   ```

3. **File permissions:** Ensure you have write access to installation folder

4. **Antivirus:** Check if antivirus is blocking file replacement

---

## 📋 Quick Reference

### Installation Directory:
```
C:\Users\[YourName]\Trading\phase3_trading_system_v1.3.10\phase3_intraday_deployment
```

### Files to Work With:
- **Original:** `unified_trading_dashboard.py` (keep backup!)
- **Backup:** `unified_trading_dashboard.py.v1.3.10.backup`
- **New:** From patch package `phase3_intraday_deployment\unified_trading_dashboard.py`

### Dashboard Access:
```
http://localhost:8050
```

### Key Check:
Hover tooltip must show: **"Change from Prev Close: X.XX%"**

---

## ✅ Success Criteria

**Installation is successful when:**

1. ✅ File copied without errors
2. ✅ Dashboard starts normally
3. ✅ Hover shows "Change from Prev Close"
4. ✅ Percentages match Yahoo Finance/Bloomberg
5. ✅ No errors in console

---

**If you complete all steps above, your v1.3.11 patch is installed correctly!** 🎉

---

**Created:** January 3, 2026  
**Version:** v1.3.11 Manual Installation Guide  
**For:** v1.3.11 Calibration Patch
