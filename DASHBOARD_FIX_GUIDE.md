# Dashboard Dependency Fix - Quick Guide

## 🔧 The Problem

When you select **Option 7 (Unified Trading Dashboard)** from the launcher, you see:

```
ModuleNotFoundError: No module named 'dash'
```

This means the dashboard dependencies (`dash` and `plotly`) aren't installed yet.

---

## ✅ The Solution (2 minutes)

### **Option 1: Automatic Install (Recommended)**

1. Extract the updated ZIP package
2. Open the folder: `complete_backend_clean_install_v1.3.15\`
3. **Run**: `INSTALL_DASHBOARD_DEPS.bat`
4. Wait ~2-3 minutes for installation
5. Done! Dashboard ready to use

### **Option 2: Manual Install**

Open Command Prompt in the project folder and run:

```batch
pip install dash plotly
```

---

## 🎯 What Gets Installed

- **dash** (>=2.14.0) - Interactive dashboard framework
- **plotly** (>=5.14.0) - Interactive charts and graphs

Total size: ~50 MB  
Install time: 2-3 minutes

---

## 🚀 After Installation

Now you can use **Option 7** from the launcher:

```batch
1. Run LAUNCH_COMPLETE_SYSTEM.bat
2. Select Option 7
3. Dashboard opens at http://localhost:8050
4. Select stocks and start trading!
```

### Dashboard Features:
- ✅ Stock presets (ASX Blue Chips, US Tech Giants, etc.)
- ✅ Custom symbol input
- ✅ Real-time ML signal generation
- ✅ Live portfolio tracking
- ✅ 24-hour performance charts

---

## 📦 Updated Package

**File**: `complete_backend_clean_install_v1.3.15.10_FINAL.zip` (857 KB)  
**What's New**:
- ✅ Added `INSTALL_DASHBOARD_DEPS.bat` (auto-installer)
- ✅ Launcher now checks for dependencies before starting
- ✅ Clear error messages with fix instructions

---

## 🔍 Verification

To check if dash is installed:

```batch
python -c "import dash; print('Dash installed successfully!')"
```

If you see "Dash installed successfully!" → You're ready to go!

---

## 💡 Why This Happens

The dashboard requires `dash` and `plotly`, but they're not in the base requirements. 

**Why?** They're ~50 MB and not everyone needs the dashboard. We keep the base package lean (857 KB) and let you install the dashboard when you need it.

---

## 🎯 Quick Reference

| Step | Action | Time |
|------|--------|------|
| 1 | Extract updated ZIP | 30 sec |
| 2 | Run INSTALL_DASHBOARD_DEPS.bat | 2-3 min |
| 3 | Launch dashboard (Option 7) | Instant |

**Total time**: ~3 minutes to dashboard-ready!

---

## 📝 Notes

- **First-time setup**: FIRST_TIME_SETUP.bat installs core dependencies, but NOT dash/plotly
- **Requirements.txt**: Contains dash/plotly, but commented as optional
- **Best practice**: Install dash when you need the dashboard features
- **Alternative**: Use Option 5 (Paper Trading) without the dashboard

---

## ✨ What You Get

### Before Installing Dash:
- ✅ Overnight pipelines (AU/US/UK)
- ✅ Paper trading platform (Option 5)
- ✅ ML signal generation
- ❌ Unified dashboard (Option 7)

### After Installing Dash:
- ✅ Overnight pipelines (AU/US/UK)
- ✅ Paper trading platform (Option 5)
- ✅ ML signal generation
- ✅ **Unified dashboard (Option 7)** ← NEW!

---

## 🎉 Ready to Use!

Download the updated package (857 KB) and run `INSTALL_DASHBOARD_DEPS.bat` to unlock the full trading dashboard experience!

**Version**: v1.3.15.17  
**Date**: January 16, 2026  
**Status**: Dashboard dependency issue fixed ✅
