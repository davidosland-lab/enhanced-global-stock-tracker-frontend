# 🔍 PLOTTING ISSUE DEBUG INSTRUCTIONS

## Issue Summary
The 3M and 6M period buttons are showing only ~1 month of data instead of 3 and 6 months respectively.

## Debug Version Deployed
**Version**: DEBUG v2.0  
**Git Commit**: 69f7744  
**Branch**: finbert-v4.0-development

## Testing Instructions

### 1. Update Your Local Files
```bash
cd C:\Users\david\AATelS
git fetch origin
git pull origin finbert-v4.0-development
```

### 2. Restart the Flask Application
**IMPORTANT**: You must restart the Flask app to serve the new HTML file!

```bash
# Stop the current Flask app (Ctrl+C if running in terminal)
# Then restart:
python app_finbert_v4_dev.py
```

### 3. Clear Browser Cache
**CRITICAL**: Old HTML/JS might be cached!

**Option A - Hard Refresh** (Recommended):
- Chrome/Edge: Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- This forces a complete reload

**Option B - Clear Cache Manually**:
- Chrome/Edge: F12 → Network tab → Check "Disable cache" → Refresh
- Or: Settings → Privacy → Clear browsing data → Cached images and files

### 4. Verify Debug Version is Loaded

**Visual Check**:
- You should see a **yellow "DEBUG v2.0" badge** next to "FinBERT v4.0" in the header
- If you don't see this badge, the old version is still cached!

**Console Check**:
- Open browser console (F12 → Console tab)
- You should immediately see:
```
==================================================
FinBERT v4.4.4 UI - DEBUG VERSION 2.0 LOADED
Timestamp: 2025-11-29T...
Initial Period: 1mo
Initial Interval: 1d
==================================================
DOM Content Loaded - Ready for interactions
```

### 5. Test 3M and 6M Buttons

**Steps**:
1. Enter a stock symbol (e.g., `GOOGL`)
2. Click "Analyze" button
3. Watch the console for messages
4. Click the **3M** button
5. Watch the console again - you should see:
   - `=== PERIOD CHANGE ===`
   - `=== API REQUEST ===`
   - `=== API RESPONSE ===`
   - `=== CHART DATA DEBUG ===`

**Expected Console Output for 3M**:
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

### 6. What to Report Back

Please provide:

1. **Version Confirmation**:
   - [ ] Do you see the yellow "DEBUG v2.0" badge in the header?
   - [ ] Do you see the initialization messages in console?

2. **Console Output**:
   - Copy/paste ALL console messages when clicking 3M button
   - Copy/paste ALL console messages when clicking 6M button

3. **Screenshot**:
   - Screenshot of the chart showing the issue
   - Screenshot of the console with debug messages visible

4. **Browser Info**:
   - Browser name and version (e.g., "Chrome 120.0.6099.109")

## Expected Results

When working correctly:

- **3M button**: Should show 91 days (~3.0 months) of data, ~64 data points
- **6M button**: Should show 183 days (~6.1 months) of data, ~128 data points

## Troubleshooting

### If you don't see the DEBUG v2.0 badge:
1. Make sure you pulled the latest code
2. Restart Flask application
3. Hard refresh browser (Ctrl+Shift+R)
4. Try opening in incognito/private window

### If console shows no messages:
1. Check if F12 console is open and showing the "Console" tab (not "Elements")
2. Check if "Default levels" filter is enabled (not filtered)
3. Try clicking "Clear console" button and then click 3M again

### If charts still show wrong data:
- The debug logs will tell us exactly where the problem is!
- Most likely scenarios:
  - API not receiving correct parameters
  - Backend returning wrong data
  - Frontend not passing correct parameters
  - Chart library limiting data display

## Next Steps

Once you provide the console output and screenshots, I can:
1. Identify the exact point of failure
2. Implement a targeted fix
3. Verify the fix resolves the issue

---

**Git Status**:
- Commit: 69f7744
- Branch: finbert-v4.0-development  
- Files Modified: `finbert_v4.4.4/templates/finbert_v4_enhanced_ui.html`
