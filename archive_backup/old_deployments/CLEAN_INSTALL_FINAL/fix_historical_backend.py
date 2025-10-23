#!/usr/bin/env python3
"""
Fix Historical Data Manager Backend Endpoints
Adds all missing endpoints for historical data functionality
"""

import os
import sys

def add_historical_endpoints():
    """Add missing historical endpoints to backend.py"""
    
    # Check if backend.py exists
    if not os.path.exists('backend.py'):
        print("ERROR: backend.py not found!")
        return False
    
    print("Reading backend.py...")
    with open('backend.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if we need to add imports
    if 'from typing import' not in content:
        # Add after other imports
        import_pos = content.find('import uvicorn')
        if import_pos > 0:
            content = content[:import_pos] + 'from typing import Dict, Any, List, Optional\n' + content[import_pos:]
    
    # Find where to insert endpoints (before if __name__)
    insert_pos = content.find('if __name__')
    if insert_pos == -1:
        insert_pos = len(content)
    
    # Check if endpoints already exist
    if '/api/historical/batch-download' in content and '@app.post' in content:
        print("Historical endpoints already exist and are POST methods!")
        return True
    
    # If they exist but are GET, we need to fix them
    if '/api/historical/batch-download' in content:
        print("Found endpoints but they might be GET instead of POST. Fixing...")
        # Remove old endpoints
        content = remove_old_endpoints(content)
        insert_pos = content.find('if __name__')
        if insert_pos == -1:
            insert_pos = len(content)
    
    # Add the complete historical endpoints
    historical_endpoints = '''
# ============= HISTORICAL DATA MANAGER ENDPOINTS =============

@app.post("/api/historical/batch-download")
async def batch_download_historical(request: Dict[str, Any] = {}):
    """Batch download historical data for multiple symbols"""
    try:
        # Get symbols from request or use defaults
        symbols = request.get('symbols', ['AAPL', 'GOOGL', 'MSFT', 'CBA.AX', 'BHP.AX'])
        period = request.get('period', '1mo')
        interval = request.get('interval', '1d')
        
        results = []
        errors = []
        
        logger.info(f"Batch downloading {len(symbols)} symbols")
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, interval=interval)
                
                if not hist.empty:
                    # Store the data (you can implement actual storage here)
                    results.append({
                        "symbol": symbol,
                        "records": len(hist),
                        "start": hist.index[0].strftime('%Y-%m-%d'),
                        "end": hist.index[-1].strftime('%Y-%m-%d'),
                        "status": "success"
                    })
                    logger.info(f"Downloaded {symbol}: {len(hist)} records")
                else:
                    errors.append({
                        "symbol": symbol,
                        "error": "No data available"
                    })
            except Exception as e:
                logger.error(f"Error downloading {symbol}: {str(e)}")
                errors.append({
                    "symbol": symbol,
                    "error": str(e)
                })
        
        return JSONResponse({
            "success": len(results),
            "failed": len(errors),
            "results": results,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch download error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/historical/download")
async def download_single_historical(request: Dict[str, Any] = {}):
    """Download historical data for a single symbol"""
    try:
        symbol = request.get('symbol', 'AAPL')
        period = request.get('period', '1mo')
        interval = request.get('interval', '1d')
        
        logger.info(f"Downloading historical data for {symbol}")
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return JSONResponse(
                status_code=404,
                content={"error": f"No data available for {symbol}"}
            )
        
        # Convert to list of records
        data = []
        for idx, row in hist.iterrows():
            data.append({
                "date": idx.strftime('%Y-%m-%d %H:%M:%S'),
                "timestamp": int(idx.timestamp() * 1000),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        # You can save to file/database here
        csv_data = hist.to_csv()
        
        return JSONResponse({
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "records": len(hist),
            "start": hist.index[0].strftime('%Y-%m-%d'),
            "end": hist.index[-1].strftime('%Y-%m-%d'),
            "data": data[:100],  # Limit to first 100 records for response
            "csv_preview": csv_data[:500],  # First 500 chars of CSV
            "status": "success",
            "message": f"Downloaded {len(hist)} records for {symbol}"
        })
        
    except Exception as e:
        logger.error(f"Download error for {symbol}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/historical/statistics")
async def get_historical_statistics():
    """Get statistics about stored historical data"""
    try:
        # This would normally check your database/storage
        # For now, return mock statistics
        stats = {
            "total_symbols": 0,
            "total_records": 0,
            "last_updated": datetime.now().isoformat(),
            "storage_size_mb": 0,
            "cached_symbols": [],
            "available_periods": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
            "available_intervals": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        }
        
        # Check if historical_data directory exists
        if os.path.exists('historical_data'):
            import glob
            csv_files = glob.glob('historical_data/*.csv')
            stats['total_symbols'] = len(csv_files)
            stats['cached_symbols'] = [os.path.basename(f).replace('.csv', '') for f in csv_files]
            
            # Calculate total size
            total_size = sum(os.path.getsize(f) for f in csv_files) / (1024 * 1024)
            stats['storage_size_mb'] = round(total_size, 2)
        
        return JSONResponse(stats)
        
    except Exception as e:
        logger.error(f"Statistics error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/api/historical/clear-cache")
async def clear_historical_cache():
    """Clear cached historical data"""
    try:
        import shutil
        if os.path.exists('historical_data'):
            shutil.rmtree('historical_data')
            os.makedirs('historical_data')
        
        return JSONResponse({
            "status": "success",
            "message": "Historical data cache cleared",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ============= END HISTORICAL DATA ENDPOINTS =============

'''
    
    # Insert the endpoints
    new_content = content[:insert_pos] + historical_endpoints + '\n' + content[insert_pos:]
    
    # Backup original
    backup_name = f'backend_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
    with open(backup_name, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Backed up original to {backup_name}")
    
    # Write updated version
    with open('backend.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ Added historical data endpoints to backend.py")
    print("\nEndpoints added:")
    print("  POST /api/historical/batch-download")
    print("  POST /api/historical/download")
    print("  GET  /api/historical/statistics")
    print("  GET  /api/historical/clear-cache")
    
    return True

def remove_old_endpoints(content):
    """Remove old GET endpoints if they exist"""
    import re
    
    # Remove old batch-download endpoint
    pattern1 = r'@app\.get\("/api/historical/batch-download"\).*?(?=@app\.|if __name__|$)'
    content = re.sub(pattern1, '', content, flags=re.DOTALL)
    
    # Remove old download endpoint
    pattern2 = r'@app\.get\("/api/historical/download"\).*?(?=@app\.|if __name__|$)'
    content = re.sub(pattern2, '', content, flags=re.DOTALL)
    
    return content

if __name__ == "__main__":
    from datetime import datetime
    
    print("="*60)
    print("FIXING HISTORICAL DATA MANAGER BACKEND")
    print("="*60)
    print()
    
    if add_historical_endpoints():
        print("\n" + "="*60)
        print("FIX COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Restart your backend:")
        print("   - Press Ctrl+C in the backend window")
        print("   - Run: python backend.py")
        print("2. Refresh your browser")
        print("3. Try the Historical Data Manager again")
    else:
        print("\nFix failed. Please check the error messages above.")