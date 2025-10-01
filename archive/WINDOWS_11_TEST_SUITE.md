# Windows 11 Deployment Test Suite
## GSMT - Global Stock Market Tracker

### ✅ Live Test URLs (Available Now)

**Backend API (Real Data)**: https://8002-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev
**Dashboard Frontend**: https://8080-i2ch499gc6d7qpm0yvxy4-6532622b.e2b.dev/simple_working_dashboard.html

### 🔍 Current Live Data Verification
- **All Ordinaries**: 9,135.90 points (-0.14%) ✅ CORRECT
- **Data Source**: Real Yahoo Finance API
- **No synthetic data**: Verified clean

---

## 📋 Windows 11 Test Checklist

### Step 1: Pre-Installation Tests
- [ ] **Python Check**
  ```cmd
  python --version
  ```
  Expected: Python 3.8 or higher

- [ ] **PowerShell Version Check**
  ```powershell
  $PSVersionTable.PSVersion
  ```
  Expected: Version 5.1 or higher

### Step 2: Installation Directory Test
- [ ] **Create GSMT Directory**
  ```cmd
  mkdir C:\GSMT
  cd C:\GSMT
  ```

- [ ] **Extract Package**
  - Extract GSMT_Windows_Fixed_v2.0.zip to C:\GSMT\
  - Verify structure:
    ```
    C:\GSMT\
    ├── backend_fixed.py
    ├── simple_working_dashboard.html
    ├── FIX_WINDOWS_URLS.ps1
    ├── START_GSMT_WINDOWS_FIXED.bat
    ├── requirements.txt
    ├── verify_integrity.py
    ├── RECOVERY_FRAMEWORK.md
    └── modules\
        ├── global_indices_tracker.html
        ├── single_stock_tracker.html
        ├── cba_analysis.html
        ├── technical_analysis.html
        ├── ml_predictions.html
        └── document_center.html
    ```

### Step 3: URL Fix Verification
- [ ] **Run PowerShell Fix Script**
  ```powershell
  cd C:\GSMT
  powershell -ExecutionPolicy Bypass -File FIX_WINDOWS_URLS.ps1
  ```
  Expected output:
  ```
  ✓ Fixed: simple_working_dashboard.html
  ✓ Fixed: modules\global_indices_tracker.html
  ✓ Fixed: modules\single_stock_tracker.html
  ✓ Fixed: modules\cba_analysis.html
  ✓ Fixed: modules\technical_analysis.html
  ✓ Fixed: modules\ml_predictions.html
  Fix Complete! 7 files are using localhost:8002
  ```

- [ ] **Verify URL Changes**
  ```powershell
  Select-String -Path "*.html","modules\*.html" -Pattern "localhost:8002"
  ```
  Should show all HTML files containing 'http://localhost:8002'

### Step 4: Dependencies Installation Test
- [ ] **Install Python Packages**
  ```cmd
  cd C:\GSMT
  pip install -r requirements.txt
  ```
  Required packages:
  - yfinance
  - fastapi
  - uvicorn
  - pytz
  - cachetools
  - pandas
  - numpy

### Step 5: Backend Startup Test
- [ ] **Start Backend Server**
  ```cmd
  cd C:\GSMT
  python backend_fixed.py
  ```
  Expected output:
  ```
  INFO:     Started server process
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:8002
  ```

- [ ] **Test Backend API**
  Open new command prompt:
  ```cmd
  curl http://localhost:8002/
  ```
  Expected response:
  ```json
  {
    "service": "Fixed Market Data API",
    "status": "active",
    "message": "Using correct previous close from history data"
  }
  ```

### Step 6: Frontend Access Test
- [ ] **Open Dashboard in Browser**
  - Method 1: Double-click `simple_working_dashboard.html`
  - Method 2: Navigate to `file:///C:/GSMT/simple_working_dashboard.html`
  - Method 3: Run batch file `START_GSMT_WINDOWS_FIXED.bat`

- [ ] **Verify Dashboard Loads**
  - Should show "Global Stock Market Tracker - Simple Working Version"
  - Status indicators should be visible
  - Time should show AEST

### Step 7: Data Flow Test
- [ ] **Check Console for Errors**
  Press F12 in browser, check Console tab:
  - Should NOT see "Failed to fetch"
  - Should NOT see CORS errors
  - Should see "Fetching real market data from: http://localhost:8002"

- [ ] **Verify Market Data Display**
  - All Ordinaries: ~9,135 points (-0.14%)
  - ASX 200: ~8,848 points
  - Other indices should populate

### Step 8: Module Testing
Test each module by clicking from dashboard:

- [ ] **Global Indices Tracker**
  - Shows indices grouped by region
  - Data updates every 30 seconds

- [ ] **Single Stock Tracker**
  - Search for "CBA.AX" 
  - Should show Commonwealth Bank data

- [ ] **CBA Analysis**
  - Shows Big 4 banks comparison
  - All data from Yahoo Finance

- [ ] **Technical Analysis**
  - Enter "BHP.AX"
  - Should show RSI, moving averages

- [ ] **ML Predictions**
  - Basic predictions display
  - No complex dependencies

- [ ] **Document Center**
  - Trading guides display
  - Static content works

### Step 9: Integrity Verification
- [ ] **Run Verification Script**
  ```cmd
  cd C:\GSMT
  python verify_integrity.py
  ```
  Expected:
  ```
  ============================================================
  GSMT INTEGRITY VERIFICATION
  ============================================================
  ✅ Calculations verified
  ✅ All using localhost:8002
  ✅ ALL VERIFICATIONS PASSED!
  ```

### Step 10: Batch File Test
- [ ] **Test Automated Startup**
  ```cmd
  cd C:\GSMT
  START_GSMT_WINDOWS_FIXED.bat
  ```
  Should:
  1. Fix URLs automatically
  2. Install dependencies
  3. Start backend
  4. Open browser

---

## 🔧 Troubleshooting Guide

### Issue: "Failed to fetch" in browser
**Solution**: Check backend is running on port 8002
```cmd
netstat -an | findstr :8002
```

### Issue: PowerShell script won't run
**Solution**: Enable script execution
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Issue: Port 8002 already in use
**Solution**: Kill existing process
```cmd
netstat -ano | findstr :8002
taskkill /F /PID [process_id]
```

### Issue: Module not found errors
**Solution**: Reinstall dependencies
```cmd
pip uninstall -y yfinance fastapi uvicorn
pip install -r requirements.txt
```

---

## ✅ Success Criteria

The deployment is successful when:
1. ✅ Backend runs on http://localhost:8002
2. ✅ All Ordinaries shows ~9,135 points (-0.14%)
3. ✅ No "Failed to fetch" errors
4. ✅ All 6 modules accessible and functional
5. ✅ Real Yahoo Finance data displayed
6. ✅ No synthetic/random data
7. ✅ Integrity verification passes

---

## 📊 Expected Test Results

### Backend API Response
```json
{
  "^AORD": {
    "symbol": "^AORD",
    "name": "All Ordinaries",
    "price": 9135.90,
    "change": -12.60,
    "change_percent": -0.14,
    "volume": 123456789,
    "market_state": "CLOSED",
    "region": "Asia"
  }
}
```

### Browser Console (Healthy)
```
Fetching real market data from: http://localhost:8002
Market data loaded successfully
All Ordinaries: 9135.90 (-0.14%)
```

---

## 🚀 Quick Start Commands

For immediate testing on Windows 11:

```powershell
# One-liner setup (run in PowerShell as Administrator)
cd C:\GSMT; ./FIX_WINDOWS_URLS.ps1; pip install -r requirements.txt; python backend_fixed.py

# Separate terminal for frontend
start chrome "file:///C:/GSMT/simple_working_dashboard.html"
```

---

## 📝 Test Report Template

```
Date: _____________
Tester: ___________
Windows Version: 11 (Build _____)
Python Version: _______

Test Results:
[ ] Backend starts successfully
[ ] Frontend loads without errors
[ ] All Ordinaries shows correct value
[ ] All modules functional
[ ] No synthetic data detected
[ ] URLs properly configured

Issues Found:
_________________________________
_________________________________

Resolution:
_________________________________
_________________________________

Status: [ ] PASS [ ] FAIL
```

---

Last Updated: January 2025
Test Version: 2.0-windows-fixed