# 🚀 Quick Start Instructions

## Fix for your current issue:

You need to change to the correct directory first:

```cmd
cd C:\StockTrack\Complete_Stock_Tracker_Windows11
python backend.py
```

## 📌 Creating Desktop Shortcut (3 Options):

### Option 1: Automatic PowerShell Method
1. Open PowerShell as Administrator
2. Run these commands:
```powershell
cd C:\StockTrack\Complete_Stock_Tracker_Windows11
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Bypass -Force
.\Create_Desktop_Shortcut.ps1
```

### Option 2: Manual Shortcut Creation
1. Right-click on your Desktop
2. Select "New" → "Shortcut"
3. Enter location: `C:\StockTrack\Complete_Stock_Tracker_Windows11\START_STOCK_TRACKER.bat`
4. Click "Next"
5. Name it: "Stock Tracker"
6. Click "Finish"

### Option 3: Copy Batch File to Desktop
Simply copy `START_STOCK_TRACKER.bat` to your Desktop and double-click it to run.

## 🎯 Running the Application:

### From Command Line:
```cmd
cd C:\StockTrack\Complete_Stock_Tracker_Windows11
python backend.py
```

### From Desktop Shortcut:
Double-click the "Stock Tracker" shortcut

### Using VBScript (Silent Launch):
Double-click `StockTracker.vbs` for a cleaner startup

## 🌐 Accessing the Application:

Once the server starts, it will:
1. Show "Server starting on http://localhost:8002" 
2. Automatically open your browser
3. Display the landing page with all 5 modules

If browser doesn't open automatically:
- Open any browser
- Go to: `http://localhost:8002`

## 🔧 Troubleshooting:

### If you get "Module not found" errors:
Some ML libraries might fail, but core functionality will still work.

### If port 8002 is busy:
1. Close any other Python processes
2. Or edit `backend.py` line ~10480 to change port:
```python
port = 8003  # Change to different port
```

### If browser shows "Cannot connect":
1. Check the command window for errors
2. Ensure the server shows "Starting server on http://localhost:8002"
3. Wait 5-10 seconds for server to fully start

## ✅ Quick Test:

After starting, verify these modules work:
1. **CBA Enhanced** - Should show ~$170 price
2. **Global Indices** - Should show ^AORD, ^FTSE, ^GSPC
3. **Stock Tracker** - Should display candlestick charts
4. **Phase 4 Predictor** - Should connect to real data
5. **Historical Data Manager** - Should allow data downloads

---

**Support Files:**
- `START_STOCK_TRACKER.bat` - Main launcher
- `StockTracker.vbs` - Silent launcher
- `Create_Desktop_Shortcut.ps1` - Creates desktop shortcut
- `backend.py` - Main server (port 8002)