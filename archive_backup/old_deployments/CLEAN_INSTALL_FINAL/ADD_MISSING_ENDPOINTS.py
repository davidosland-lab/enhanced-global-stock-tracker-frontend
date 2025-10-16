#!/usr/bin/env python3
"""
Quick patch to add missing endpoints to your backend
Run this to update your backend.py with missing endpoints
"""

import os
import sys

def add_missing_endpoints():
    """Add the missing endpoints to backend.py"""
    
    # Read current backend
    if not os.path.exists('backend.py'):
        print("ERROR: backend.py not found!")
        return False
    
    with open('backend.py', 'r') as f:
        content = f.read()
    
    # Check if endpoints already exist
    if '/api/historical/statistics' in content:
        print("Endpoints already exist!")
        return True
    
    # Find where to insert (before the main block)
    insert_pos = content.find('if __name__')
    if insert_pos == -1:
        insert_pos = len(content)
    
    # Missing endpoints code
    missing_endpoints = '''
# Additional endpoints for Historical Data Manager
@app.get("/api/historical/statistics")
async def get_historical_statistics():
    """Get statistics about stored historical data"""
    return {
        "total_symbols": 0,
        "total_records": 0,
        "last_updated": datetime.now().isoformat(),
        "storage_size_mb": 0,
        "cached_symbols": []
    }

@app.post("/api/historical/batch-download")
async def batch_download_historical():
    """Batch download historical data"""
    try:
        # Download popular stocks
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'CBA.AX', 'BHP.AX']
        results = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1mo")
                if not hist.empty:
                    results.append({
                        "symbol": symbol,
                        "records": len(hist),
                        "status": "success"
                    })
            except:
                pass
        
        return {
            "success": len(results),
            "failed": len(symbols) - len(results),
            "results": results
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/historical/download")
async def download_single_historical(data: dict = {}):
    """Download historical data for a single symbol"""
    try:
        symbol = data.get("symbol", "AAPL")
        period = data.get("period", "1mo")
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {"error": "No data available"}
        
        return {
            "symbol": symbol,
            "records": len(hist),
            "start": hist.index[0].strftime("%Y-%m-%d"),
            "end": hist.index[-1].strftime("%Y-%m-%d"),
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e)}

'''
    
    # Insert the endpoints
    new_content = content[:insert_pos] + missing_endpoints + '\n' + content[insert_pos:]
    
    # Backup original
    with open('backend_original.py', 'w') as f:
        f.write(content)
    print("Backed up original to backend_original.py")
    
    # Write updated version
    with open('backend.py', 'w') as f:
        f.write(new_content)
    
    print("Added missing endpoints to backend.py")
    print("\nPlease restart your backend for changes to take effect:")
    print("1. Press Ctrl+C in the backend window")
    print("2. Run: python backend.py")
    
    return True

if __name__ == "__main__":
    add_missing_endpoints()