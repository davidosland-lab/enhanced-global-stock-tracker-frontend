# 🚀 START_UNIFIED_DASHBOARD.bat - Quick Guide

**File:** `START_UNIFIED_DASHBOARD.bat`  
**Purpose:** Simple one-click launcher for the unified trading dashboard  
**Size:** 2.0KB

---

## ✅ **WHAT IT DOES**

1. ✅ Changes to the correct directory
2. ✅ Checks if virtual environment exists
3. ✅ Activates the virtual environment
4. ✅ Sets `KERAS_BACKEND=torch`
5. ✅ Starts `unified_trading_dashboard.py`
6. ✅ Opens dashboard at `http://localhost:8050`

---

## 🚀 **HOW TO USE**

### **Step 1: Copy File**

Copy `START_UNIFIED_DASHBOARD.bat` to:
```
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\
```

### **Step 2: Double-Click**

Just double-click `START_UNIFIED_DASHBOARD.bat`

### **Step 3: Wait for Dashboard**

You'll see:
```
═══════════════════════════════════════════════════════════
  STARTING UNIFIED TRADING DASHBOARD
═══════════════════════════════════════════════════════════

[1/3] Activating virtual environment...
[OK] Virtual environment activated

[2/3] Setting environment variables...
[OK] KERAS_BACKEND=torch

[3/3] Starting unified trading dashboard...

───────────────────────────────────────────────────────────
  Dashboard will open at: http://localhost:8050
  Press Ctrl+C to stop the dashboard
───────────────────────────────────────────────────────────

Starting Unified Paper Trading Dashboard...
[OK] FinBERT model loaded successfully
[OK] Keras LSTM available (PyTorch backend)
Dash is running on http://0.0.0.0:8050/
```

### **Step 4: Open Browser**

Open: `http://localhost:8050`

---

## ⏱️ **TIMING**

- **Startup time:** 10-15 seconds
- **No installation:** Uses existing packages
- **Just launches:** The dashboard directly

---

## 🎯 **WHEN TO USE THIS**

### **Use START_UNIFIED_DASHBOARD.bat when:**
- ✅ Dependencies are already installed
- ✅ You just want to start trading quickly
- ✅ You don't need the full menu system
- ✅ You want the fastest startup

### **Use START_SYSTEM.bat (with launcher.py) when:**
- ✅ First-time setup (installs dependencies)
- ✅ You want the full menu with all options
- ✅ You need to run pipelines or other features
- ✅ You want dependency checking

---

## 📋 **COMPARISON OF LAUNCHERS**

| File | Purpose | First Run | Subsequent | Features |
|------|---------|-----------|------------|----------|
| **START_UNIFIED_DASHBOARD.bat** | **Quick dashboard start** | **10 sec** | **10 sec** | **Dashboard only** |
| START_SYSTEM.bat + launcher.py | Full system with menu | 5-10 min | 5 sec | All features |
| LAUNCH_COMPLETE_SYSTEM_v1.3.15.60.bat | Auto-install (crashes) | ✗ Crashes | - | - |
| LAUNCH_COMPLETE_SYSTEM_v1.3.15.62.bat | Manual install | 2 sec | 2 sec | Full menu |

---

## ✅ **ADVANTAGES**

### **Simple & Fast:**
- ✅ No dependency checking (assumes installed)
- ✅ No complex logic (cannot crash)
- ✅ Direct to dashboard (10 seconds)
- ✅ Clean code (easy to read/modify)

### **Reliable:**
- ✅ Checks virtual environment exists
- ✅ Shows clear error messages
- ✅ Sets required environment variables
- ✅ Handles errors gracefully

---

## 🔧 **TROUBLESHOOTING**

### **If you see: "Virtual environment not found"**

**Problem:** Running from wrong directory or venv doesn't exist

**Solution:**
```batch
1. Make sure you're in: C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\
2. Check that venv\ folder exists
3. If not, create it: python -m venv venv
```

### **If you see: "No module named 'dash'"**

**Problem:** Dependencies not installed in venv

**Solution:**
```batch
1. Use START_SYSTEM.bat first (installs dependencies)
   OR
2. Install manually:
   venv\Scripts\pip install dash plotly transformers keras torch
```

### **If dashboard doesn't open:**

**Problem:** Port 8050 already in use

**Solution:**
```batch
1. Close other dashboard windows
2. Check Task Manager for python.exe processes
3. Kill them and try again
```

---

## 📁 **FILE LOCATION**

**Copy this file to:**
```
C:\Users\david\Regime_trading\COMPLETE_SYSTEM_v1.3.15.45_FINAL\START_UNIFIED_DASHBOARD.bat
```

**Must be in the SAME folder as:**
- unified_trading_dashboard.py
- venv\ (virtual environment folder)

---

## 🎯 **QUICK REFERENCE**

```
╔═══════════════════════════════════════════════════════╗
║  START_UNIFIED_DASHBOARD.bat                         ║
╠═══════════════════════════════════════════════════════╣
║  What:   Quick launcher for trading dashboard        ║
║  Where:  COMPLETE_SYSTEM_v1.3.15.45_FINAL folder     ║
║  How:    Double-click the file                       ║
║  Time:   10 seconds                                   ║
║  URL:    http://localhost:8050                       ║
║  Stop:   Press Ctrl+C                                ║
╚═══════════════════════════════════════════════════════╝
```

---

## ✅ **SUMMARY**

**File:** START_UNIFIED_DASHBOARD.bat  
**Purpose:** Quick one-click dashboard launcher  
**Requirements:** Virtual environment must exist with dependencies installed  
**Time:** 10 seconds  
**Result:** Dashboard opens at http://localhost:8050  

**This is the SIMPLEST way to start the dashboard once everything is set up!** 🚀

---

## 📦 **ALL AVAILABLE LAUNCHERS**

**Now you have:**

1. **START_UNIFIED_DASHBOARD.bat** ⭐ **NEW - SIMPLEST**
   - Quick dashboard start
   - 10 seconds
   - No dependency checking
   - Use this for daily trading

2. **START_SYSTEM.bat + launcher.py**
   - Full system with menu
   - Auto-installs dependencies
   - All features (pipelines, trading, status)
   - Use this for first-time setup

3. **Direct command:**
   ```batch
   python unified_trading_dashboard.py
   ```
   - Fastest (if you're comfortable with command line)

---

**Version:** v1.3.15.64 SIMPLE DASHBOARD LAUNCHER  
**Date:** 2026-02-01  
**Status:** ✅ Production Ready

**Ready to use! Just copy START_UNIFIED_DASHBOARD.bat to your folder and double-click it!** 🚀
