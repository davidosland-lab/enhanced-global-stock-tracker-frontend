# 🔧 Fix for "Run Prediction" Button Not Working

## Problem Identified

The "Run Prediction" button in the Prediction Centre isn't working because:

1. **Wrong API Method**: The frontend is trying to POST to `/api/predict` but the backend only accepts GET requests
2. **Wrong Port**: It's trying to POST to port 8004 (ML backend) which may not have the endpoint configured
3. **Missing Error Handling**: When the POST fails, it doesn't properly fall back

## Quick Solutions (Choose One):

### Solution 1: Use the Fixed HTML File (EASIEST)

Save **`PREDICTION_CENTRE_FIX.html`** to your `C:\StockTrack\modules\predictions\` folder and use it instead. This version:
- Uses GET requests instead of POST
- Calls the correct endpoint
- Shows real CBA.AX prices (~$170)

### Solution 2: Test Which Method Works

1. Save **`TEST_PREDICTION_BUTTON.html`** to `C:\StockTrack\`
2. Open it in your browser
3. Click each button to see which method works
4. This will tell you exactly what's failing

### Solution 3: Fix the Original File

Edit your existing `prediction_centre_real_ml.html` file:

Find this section (around line 877):
```javascript
// Call real ML backend
const response = await fetch(`${ML_BACKEND_URL}/api/predict`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        symbol: symbol,
        timeframe: timeframe,
        models: selectedModels,
        use_real_data: true
    })
});
```

Replace with:
```javascript
// Call prediction endpoint with GET
const response = await fetch(`${BACKEND_URL}/api/predict/${symbol}`);
```

### Solution 4: Use the Complete Backend (BEST)

Run **`FINAL_COMPLETE_BACKEND.py`** which:
- Provides both GET and POST endpoints
- Runs both servers (8002 and 8004)
- Returns proper JSON for all requests
- Uses real CBA.AX prices

```cmd
cd C:\StockTrack
python FINAL_COMPLETE_BACKEND.py
```

## Testing the Fix

After applying any solution, test by:

1. Opening the Prediction Centre
2. Enter "CBA.AX" as the symbol
3. Click "Run Prediction"
4. Should show:
   - Current Price: ~$170
   - Predicted Price: ~$171-172
   - NOT $100.10!

## What Each File Does:

| File | Purpose | Location |
|------|---------|----------|
| **PREDICTION_CENTRE_FIX.html** | Fixed prediction centre UI | Replace existing prediction centre |
| **TEST_PREDICTION_BUTTON.html** | Tests which API methods work | Standalone test page |
| **FINAL_COMPLETE_BACKEND.py** | Complete backend with all fixes | Main backend server |

## Verification Steps:

1. **Check Backend is Running:**
   - Open: http://localhost:8002/
   - Should return JSON (not HTML)

2. **Check Prediction Endpoint:**
   - Open: http://localhost:8002/api/predict/CBA.AX
   - Should return predictions based on ~$170

3. **Check Stock Data:**
   - Open: http://localhost:8002/api/stock/CBA.AX
   - Should show current price ~$170

## Common Issues:

### "Unexpected token '<'" Error
- Backend is returning HTML instead of JSON
- Solution: Use FINAL_COMPLETE_BACKEND.py

### "Failed to fetch" Error
- Backend not running or wrong port
- Solution: Start backend on port 8002

### Shows $100.10 for CBA.AX
- Using hardcoded fallback values
- Solution: Ensure prediction endpoint is working

## The Complete Fix Process:

1. **Stop current backends** (Ctrl+C in command windows)
2. **Copy fixed files** to C:\StockTrack
3. **Run new backend**: `python FINAL_COMPLETE_BACKEND.py`
4. **Use fixed prediction centre** or apply the code fix
5. **Test with CBA.AX** - should show ~$170

This will completely fix the "Run Prediction" button issue!