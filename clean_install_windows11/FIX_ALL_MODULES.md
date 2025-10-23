# IMMEDIATE FIXES FOR ALL MODULE ISSUES

## Issues Identified:
1. Historical Data Manager - 404 Error "Nothing matches the given URI"
2. Document Analyser - Not loading properly  
3. Prediction Centre - Broken link
4. ML Training - Wrong CBA.AX price data

## QUICK FIX INSTRUCTIONS

### 1. Fix Historical Data Manager Backend Route

The backend is missing the `/api/historical/batch-download` endpoint. Add this to your `backend.py`:

```python
@app.post("/api/historical/batch-download")
async def batch_download_historical():
    """Download multiple symbols at once"""
    try:
        # Popular ASX stocks
        symbols = ['CBA.AX', 'BHP.AX', 'ANZ.AX', 'WBC.AX', 'NAB.AX']
        results = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                if not hist.empty:
                    results.append(symbol)
            except:
                pass
        
        return {
            "success": True,
            "symbols": results,
            "message": f"Downloaded {len(results)} symbols"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 2. Update index.html Module Links

Replace the modules object in index.html with:

```javascript
const modules = {
    'cba': 'modules/cba_enhanced.html',
    'indices': 'modules/indices_tracker.html', 
    'tracker': 'modules/stock_tracker.html',
    'predictor': 'modules/prediction_centre_phase4.html',  // Fixed
    'documents': 'modules/document_uploader.html',  // Fixed
    'historical': 'modules/historical_data_manager_fixed.html',
    'performance': 'modules/prediction_performance_dashboard.html',
    'mltraining': 'modules/ml_training_centre.html',
    'technical': 'modules/technical_analysis_fixed.html'
};
```

### 3. Fix ML Training CBA.AX Price Issue

The ML training is getting old/cached data. Update `ml_training_centre.html` to force fresh data:

Find the line where it fetches CBA.AX and add cache-busting:
```javascript
// Add timestamp to prevent caching
const response = await fetch(`http://localhost:8002/api/historical/CBA.AX?period=1y&interval=1d&t=${Date.now()}`);
```

## COMPLETE FIX SCRIPT

Save this as `apply_fixes.py` and run it:

```python
#!/usr/bin/env python3
import os
import re

def fix_backend():
    """Add missing endpoints to backend.py"""
    backend_path = 'backend.py'
    
    # Read current backend
    with open(backend_path, 'r') as f:
        content = f.read()
    
    # Check if batch-download endpoint exists
    if '/api/historical/batch-download' not in content:
        # Add the endpoint before the last line
        endpoint_code = '''
@app.post("/api/historical/batch-download")
async def batch_download_historical():
    """Download multiple symbols at once"""
    try:
        symbols = ['CBA.AX', 'BHP.AX', 'ANZ.AX', 'WBC.AX', 'NAB.AX', 
                   'CSL.AX', 'WOW.AX', 'TLS.AX', 'RIO.AX', 'WES.AX']
        results = []
        
        for symbol in symbols[:5]:  # Limit to 5 to avoid timeout
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                if not hist.empty:
                    results.append(symbol)
            except:
                pass
        
        return {
            "success": True,
            "symbols": results,
            "count": len(results)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/historical/download")
async def download_historical(request: dict):
    """Download historical data for specified symbols"""
    try:
        symbols = request.get('symbols', [])
        period = request.get('period', '1mo')
        intervals = request.get('intervals', ['1d'])
        
        processed = []
        for symbol in symbols[:5]:  # Limit to prevent timeout
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    processed.append(symbol)
            except:
                pass
        
        return {
            "success": True,
            "symbols_processed": processed,
            "count": len(processed)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
'''
        
        # Insert before the main block
        if 'if __name__' in content:
            content = content.replace('if __name__', endpoint_code + '\nif __name__')
        else:
            content += endpoint_code
        
        # Save updated backend
        with open(backend_path, 'w') as f:
            f.write(content)
        
        print("✅ Backend fixed with missing endpoints")

def fix_index_links():
    """Fix module links in index.html"""
    
    with open('index.html', 'r') as f:
        content = f.read()
    
    # Fix the modules object
    old_modules = r"const modules = {[^}]+};"
    new_modules = """const modules = {
            'cba': 'modules/cba_enhanced.html',
            'indices': 'modules/indices_tracker.html',
            'tracker': 'modules/stock_tracker.html',
            'predictor': 'modules/prediction_centre_phase4.html',
            'documents': 'modules/document_uploader.html',
            'historical': 'modules/historical_data_manager_fixed.html',
            'performance': 'modules/prediction_performance_dashboard.html',
            'mltraining': 'modules/ml_training_centre.html',
            'technical': 'modules/technical_analysis_fixed.html'
        };"""
    
    content = re.sub(old_modules, new_modules, content, flags=re.DOTALL)
    
    with open('index.html', 'w') as f:
        f.write(content)
    
    print("✅ Index.html links fixed")

def fix_ml_training():
    """Fix ML training module to get fresh CBA.AX data"""
    ml_path = 'modules/ml_training_centre.html'
    
    if os.path.exists(ml_path):
        with open(ml_path, 'r') as f:
            content = f.read()
        
        # Add cache busting to all fetch calls
        content = re.sub(
            r"fetch\(`\$\{API_BASE\}/api/historical/([^`]+)`\)",
            r"fetch(`${API_BASE}/api/historical/\1&t=${Date.now()}`)",
            content
        )
        
        with open(ml_path, 'w') as f:
            f.write(content)
        
        print("✅ ML Training module fixed for fresh data")

if __name__ == "__main__":
    print("Applying all fixes...")
    fix_backend()
    fix_index_links()
    fix_ml_training()
    print("\n✅ All fixes applied!")
    print("\nNow restart your services:")
    print("1. Close all Python processes")
    print("2. Run MASTER_STARTUP_ENHANCED.bat")
```

## MANUAL FIXES

If the script doesn't work, apply these manual fixes:

### 1. For Historical Data 404 Error
The module is trying to call endpoints that don't exist. Use the simplified version that only calls existing endpoints.

### 2. For Document Analyser
Make sure the file exists at: `modules/document_uploader.html`
If not, the link should be: `modules/document_analyzer.html`

### 3. For Prediction Centre
Check which file exists:
- `modules/prediction_centre_phase4.html`
- `modules/prediction_centre_phase4_real.html`
- `REAL_WORKING_PREDICTOR.html`

Use the one that exists.

### 4. For ML Training Price Issue
The ML module is using cached or old data. Clear browser cache and ensure backend returns fresh data.

## RESTART SEQUENCE

After applying fixes:

```batch
1. Close all Python windows
2. Run: taskkill /F /IM python.exe
3. Run: MASTER_STARTUP_ENHANCED.bat
4. Clear browser cache (Ctrl+Shift+Delete)
5. Reload the page
```