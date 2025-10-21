# TROUBLESHOOTING GUIDE

## If you see "Error: No data found for CBA.AX" in the interface:

### Solution 1: Use the Symbol Without .AX
Instead of typing "CBA.AX", just type **"CBA"**
- The system will auto-detect it's an Australian stock
- It will automatically add .AX for you

### Solution 2: Clear Browser Cache
1. Press Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
2. Or open in Incognito/Private mode
3. Try again

### Solution 3: Test Direct API
Open a new terminal and run:
```bash
curl -X POST http://localhost:8000/api/fetch -H "Content-Type: application/json" -d '{"symbol":"CBA","period":"1mo"}'
```

### Solution 4: Use Command Line Predictions
```bash
python3 universal_predictor.py CBA 2
```

### Solution 5: Check Server is Running
The server console should show:
```
Auto-detected Australian stock: CBA.AX
Fetching CBA.AX from Yahoo Finance...
```

## CONFIRMED WORKING DATA:
- **CBA.AX**: AUD $174.04 ✅
- **BHP.AX**: Working ✅
- **AAPL**: USD $252.29 ✅

## Common Issues:

### Issue: 404 Error
**Fix:** Make sure you're using the yahoo_only_server.py:
```bash
python3 yahoo_only_server.py
```

### Issue: No data returned
**Fix:** Try these symbols that are confirmed working:
- CBA (auto-converts to CBA.AX)
- BHP (auto-converts to BHP.AX)
- AAPL
- MSFT

### Issue: Interface not updating
**Fix:** Hard refresh the browser:
- Windows: Ctrl + F5
- Mac: Cmd + Shift + R

## DIRECT TEST COMMANDS:

Test if Yahoo Finance is working:
```bash
# Test CBA
curl -X POST http://localhost:8000/api/fetch -H "Content-Type: application/json" -d '{"symbol":"CBA","period":"1mo"}'

# Test prediction
curl -X POST http://localhost:8000/api/predict -H "Content-Type: application/json" -d '{"symbol":"CBA","months":2}'
```

## WORKING EXAMPLE OUTPUT:
When working correctly, you should see:
```json
{
  "symbol": "CBA.AX",
  "company": "Commonwealth Bank of Australia",
  "currency": "AUD",
  "latest_price": 174.04,
  "data_points": 22
}
```

## If All Else Fails:
Use the command line tool directly:
```bash
python3 universal_predictor.py CBA.AX 2
```

This will give you the full prediction without using the web interface.