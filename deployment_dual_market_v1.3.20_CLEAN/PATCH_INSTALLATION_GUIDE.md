# 🔧 PLOTTING DEBUG PATCH INSTALLATION GUIDE

## Overview
This patch adds comprehensive debug logging to diagnose why 3M and 6M period buttons are not displaying the correct time range in FinBERT 4.4.4.

## Package Contents
- `PLOTTING_DEBUG_v2.0.patch` - Git patch file with all changes
- `PATCH_INSTALLATION_GUIDE.md` - This file
- `PLOTTING_DEBUG_INSTRUCTIONS.md` - Testing instructions

## What This Patch Does

### Visual Changes
- Adds yellow **"DEBUG v2.0"** badge next to "FinBERT v4.0" header
- No other visual changes

### Debug Logging Added
1. **Page Load Logging**: Confirms script version loaded with timestamp
2. **Period Change Logging**: Logs when you click 3M, 6M, or any period button
3. **API Request Logging**: Logs the exact URL and parameters being sent
4. **API Response Logging**: Logs how many data points were received
5. **Chart Data Logging**: Logs date range and data points being displayed

## Installation Methods

### Method 1: Git Apply (Recommended if you have Git)

1. **Navigate to your FinBERT directory**:
   ```bash
   cd C:\Users\david\AATelS
   ```

2. **Make sure you're on the correct branch**:
   ```bash
   git checkout finbert-v4.0-development
   ```

3. **Apply the patch**:
   ```bash
   git apply PLOTTING_DEBUG_v2.0.patch
   ```

4. **Verify changes**:
   ```bash
   git status
   ```
   You should see:
   - Modified: `finbert_v4.4.4/templates/finbert_v4_enhanced_ui.html`
   - New file: `PLOTTING_DEBUG_INSTRUCTIONS.md`

5. **Commit the changes** (optional):
   ```bash
   git add .
   git commit -m "Apply plotting debug patch v2.0"
   ```

### Method 2: Manual File Replacement (If Git fails)

1. **Backup your current file**:
   ```bash
   cd C:\Users\david\AATelS\finbert_v4.4.4\templates
   copy finbert_v4_enhanced_ui.html finbert_v4_enhanced_ui.html.backup
   ```

2. **Download the updated file from GitHub**:
   - Go to: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
   - Switch to branch: `finbert-v4.0-development`
   - Navigate to: `finbert_v4.4.4/templates/finbert_v4_enhanced_ui.html`
   - Click "Raw" button
   - Save the file (Ctrl+S)
   - Replace your local file

3. **Download the instructions file**:
   - Navigate to: `PLOTTING_DEBUG_INSTRUCTIONS.md` in the same repo/branch
   - Click "Raw" and save

### Method 3: Direct Git Pull (Simplest)

1. **Navigate to directory**:
   ```bash
   cd C:\Users\david\AATelS
   ```

2. **Pull latest changes**:
   ```bash
   git fetch origin
   git pull origin finbert-v4.0-development
   ```

This automatically gets all changes!

## Post-Installation Steps

### 1. Restart Flask Application ⚠️ CRITICAL
The Flask app caches the HTML file. You MUST restart it!

```bash
# Stop the current Flask app
# Press Ctrl+C in the terminal where it's running

# Then restart
python app_finbert_v4_dev.py
```

### 2. Clear Browser Cache ⚠️ CRITICAL
Your browser caches HTML and JavaScript files!

**Option A - Hard Refresh** (Easiest):
```
Chrome/Edge: Ctrl + Shift + R (Windows)
Chrome/Edge: Cmd + Shift + R (Mac)
```

**Option B - Developer Tools**:
1. Press F12 to open DevTools
2. Go to "Network" tab
3. Check "Disable cache" checkbox
4. Keep DevTools open
5. Refresh the page (F5 or Ctrl+R)

**Option C - Incognito Window** (Most Reliable):
1. Close all FinBERT windows
2. Open a new incognito/private window
3. Navigate to http://localhost:5000

### 3. Verify Installation

**Visual Confirmation**:
- You should see a yellow **"DEBUG v2.0"** badge in the header
- Located next to "FinBERT v4.0 LSTM ENHANCED"

**Console Confirmation**:
1. Press F12 to open console
2. Look for these messages immediately:
   ```
   ==================================================
   FinBERT v4.4.4 UI - DEBUG VERSION 2.0 LOADED
   Timestamp: 2025-11-29T...
   Initial Period: 1mo
   Initial Interval: 1d
   ==================================================
   DOM Content Loaded - Ready for interactions
   ```

**If you DON'T see the badge or messages**:
- The patch wasn't applied correctly, OR
- Flask wasn't restarted, OR
- Browser cache wasn't cleared

## Testing the Patch

### Quick Test

1. **Open the FinBERT app** in your browser
2. **Open console** (F12 → Console tab)
3. **Enter a stock symbol** (e.g., GOOGL)
4. **Click "Analyze"**
5. **Click the "3M" button**

**Expected Console Output**:
```
=== PERIOD CHANGE ===
Changing to: period=3mo, interval=1d
Current symbol: GOOGL
=====================

=== API REQUEST ===
URL: http://localhost:5000/api/stock/GOOGL?period=3mo&interval=1d
Period: 3mo, Interval: 1d
===================

=== API RESPONSE ===
Response period: 3mo, interval: 1d
Chart data points: 64
====================

=== CHART DATA DEBUG ===
Total data points: 64
Period: 3mo, Interval: 1d
First date: 2025-08-29T...
Last date: 2025-11-28T...
Days span: 91 days (~3.0 months)
========================
```

### What to Report

Once you see the debug messages, please share:

1. **Screenshot** showing:
   - The yellow "DEBUG v2.0" badge
   - The chart with issue
   - The console with debug messages

2. **Console Output** for:
   - Clicking the 3M button
   - Clicking the 6M button

3. **Observations**:
   - How many data points does it say are received?
   - What date range does it show?
   - Does the chart match the logged date range?

## Troubleshooting

### Patch Apply Failed

**Error**: "patch does not apply"

**Solutions**:
1. Make sure you're in the correct directory (`C:\Users\david\AATelS`)
2. Make sure your working tree is clean: `git status`
3. If you have uncommitted changes, stash them: `git stash`
4. Try applying again: `git apply PLOTTING_DEBUG_v2.0.patch`
5. If still fails, use Method 2 (Manual Replacement) or Method 3 (Git Pull)

### No Debug Messages in Console

**Possible Causes**:
1. **Console is filtering messages**
   - Click the filter dropdown (says "Default levels")
   - Make sure all message types are enabled
   - Try clicking "Clear console" and test again

2. **Browser cache not cleared**
   - Try opening in incognito window
   - Or use the hard refresh: Ctrl+Shift+R

3. **Flask not restarted**
   - Stop Flask completely (Ctrl+C)
   - Start again: `python app_finbert_v4_dev.py`
   - Hard refresh browser

4. **JavaScript error preventing execution**
   - Check console for any red error messages
   - Share screenshot if you see errors

### Still Shows Old Version

**If no "DEBUG v2.0" badge visible**:

1. **Verify file was actually changed**:
   ```bash
   cd C:\Users\david\AATelS\finbert_v4.4.4\templates
   findstr /C:"DEBUG v2.0" finbert_v4_enhanced_ui.html
   ```
   Should show a line with "DEBUG v2.0" in it

2. **Check Flask is serving the correct file**:
   - Stop Flask
   - Delete any `.pyc` files or `__pycache__` folders
   - Restart Flask
   - Hard refresh browser

3. **Nuclear option** - Clear everything:
   ```bash
   # Stop Flask
   # Close all browser windows with FinBERT
   # Restart Flask
   # Open browser in incognito mode
   # Navigate to http://localhost:5000
   ```

## Files Modified by This Patch

```
finbert_v4.4.4/templates/finbert_v4_enhanced_ui.html
  - Added version badge in header (line ~332)
  - Added initialization logging (lines ~689-696)
  - Added changePeriod() logging (lines ~719-731)
  - Added API request logging (lines ~764-771)
  - Added API response logging (lines ~776-780)
  - Added chart data logging (lines ~997-1017)

PLOTTING_DEBUG_INSTRUCTIONS.md (new file)
  - Comprehensive testing instructions
```

## Need Help?

If you encounter issues:
1. Take screenshots of any error messages
2. Copy the full console output
3. Note which installation method you used
4. Report back with all the above information

## Success Criteria

✅ Yellow "DEBUG v2.0" badge visible in header  
✅ Console shows initialization messages on page load  
✅ Console shows debug messages when clicking period buttons  
✅ Can see exact API URLs and data points being logged  

Once you see all debug messages, we can identify exactly where the 3M/6M data is being lost!

---

**Patch Version**: 2.0  
**Git Commits**: a80a1be → c905fbf → 69f7744 → f2dcf4e  
**Branch**: finbert-v4.0-development  
**Date**: 2025-11-29
