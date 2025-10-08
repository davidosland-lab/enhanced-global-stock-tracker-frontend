#!/usr/bin/env python3
"""
DIRECT FIX - Adds missing endpoints to backend.py
This will definitely fix the 404 errors
"""

import os
import shutil
from datetime import datetime

print("=" * 60)
print("DIRECT BACKEND FIX - ADDING MISSING ENDPOINTS")
print("=" * 60)
print()

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Backup current backend
backup_name = f"backend_before_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy('backend.py', backup_name)
print(f"✓ Created backup: {backup_name}")

# Read the current backend.py
with open('backend.py', 'r') as f:
    lines = f.readlines()

print("\nChecking for missing endpoints...")

# Check if /api/health exists
has_health = any('/api/health' in line for line in lines)
has_market_summary = any('/api/market-summary' in line for line in lines)

print(f"  /api/health exists: {has_health}")
print(f"  /api/market-summary exists: {has_market_summary}")

if has_health and has_market_summary:
    print("\n✓ Both endpoints already exist!")
else:
    print("\nAdding missing endpoints...")
    
    # Find where to insert the endpoints (after the root endpoint)
    insert_index = -1
    for i, line in enumerate(lines):
        if '@app.get("/")' in line:
            # Find the end of the root function
            brace_count = 0
            for j in range(i, len(lines)):
                if '{' in lines[j]:
                    brace_count += lines[j].count('{')
                if '}' in lines[j]:
                    brace_count -= lines[j].count('}')
                # Look for the closing of the root function
                if j > i and brace_count == 0 and (lines[j].strip() == '}' or 'def ' in lines[j] or '@app.' in lines[j]):
                    insert_index = j
                    break
            break
    
    if insert_index == -1:
        # Alternative: find get_stock_info function
        for i, line in enumerate(lines):
            if 'def get_stock_info' in line:
                insert_index = i
                break
    
    if insert_index > 0:
        new_endpoints = []
        
        if not has_health:
            new_endpoints.append('''
@app.get("/api/health")
async def health_check():
    """Health check endpoint for frontend connectivity"""
    return {
        "status": "healthy",
        "service": "Stock Tracker Backend",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0"
    }
''')
        
        if not has_market_summary:
            new_endpoints.append('''
@app.get("/api/market-summary")
async def get_market_summary():
    """Get market summary including major indices and stats"""
    try:
        summary = {
            "indices": [],
            "stats": {
                "advancing": 0,
                "declining": 0,
                "unchanged": 0,
                "total_volume": 0
            },
            "last_updated": datetime.now().isoformat()
        }
        
        # Get major indices
        for symbol, info in INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current = float(hist['Close'].iloc[-1])
                    hist_prev = ticker.history(period="2d")
                    if len(hist_prev) >= 2:
                        prev_close = float(hist_prev['Close'].iloc[-2])
                        change = current - prev_close
                        change_pct = (change / prev_close) * 100
                    else:
                        change = 0
                        change_pct = 0
                    
                    summary["indices"].append({
                        "symbol": symbol,
                        "name": info["name"],
                        "region": info["region"],
                        "value": current,
                        "change": change,
                        "changePercent": change_pct
                    })
                    
                    # Update stats
                    if change > 0:
                        summary["stats"]["advancing"] += 1
                    elif change < 0:
                        summary["stats"]["declining"] += 1
                    else:
                        summary["stats"]["unchanged"] += 1
            except Exception as e:
                logger.error(f"Error fetching index {symbol}: {e}")
                continue
        
        # Calculate some ASX stocks for volume
        for symbol in POPULAR_STOCKS['ASX'][:5]:
            try:
                data = get_stock_info(symbol)
                summary["stats"]["total_volume"] += data.get("volume", 0)
            except:
                continue
        
        return summary
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "indices": [],
            "stats": {
                "advancing": 0,
                "declining": 0,
                "unchanged": 0,
                "total_volume": 0
            },
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }
''')
        
        # Insert the new endpoints
        for endpoint_code in new_endpoints:
            lines.insert(insert_index, endpoint_code)
        
        # Write the updated file
        with open('backend.py', 'w') as f:
            f.writelines(lines)
        
        print("✓ Added missing endpoints to backend.py")
    else:
        print("⚠ Could not find insertion point. Manual fix may be needed.")

print("\n" + "=" * 60)
print("FIX COMPLETED")
print("=" * 60)
print("\nNEXT STEPS:")
print("1. Stop the current backend (Ctrl+C in the backend window)")
print("2. Start it again: python backend.py")
print("3. The endpoints should now work!")
print("\nTest URLs:")
print("  http://localhost:8002/api/health")
print("  http://localhost:8002/api/market-summary")