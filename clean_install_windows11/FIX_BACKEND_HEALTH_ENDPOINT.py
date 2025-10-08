#!/usr/bin/env python3
"""
Fix Backend Health Endpoint Issue
Adds the missing /api/health endpoint that's causing "Backend Status: Disconnected"
"""

import os
import shutil
from datetime import datetime

def fix_backend_health():
    """Add missing health endpoint to backend.py"""
    
    print("=" * 60)
    print("FIXING BACKEND HEALTH ENDPOINT")
    print("=" * 60)
    
    # Backup current backend
    backup_name = f"backend_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy('backend.py', backup_name)
    print(f"✓ Created backup: {backup_name}")
    
    # Read current backend
    with open('backend.py', 'r') as f:
        content = f.read()
    
    # Check if health endpoint already exists
    if '/api/health' in content:
        print("✓ Health endpoint already exists in backend.py")
        return
    
    # Find where to insert the health endpoint (after root endpoint)
    root_endpoint = '''@app.get("/")
async def root():
    """Root endpoint showing API status"""
    return {
        "status": "active",
        "message": "Stock Tracker API v4.0 with Historical Data Manager",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "stock_price": "/api/stock/{symbol}",
            "indices": "/api/indices",
            "market_movers": "/api/market-movers",
            "prediction": "/api/predict",
            "historical": "/api/historical/{symbol}",
            "batch_download": "/api/historical/batch-download",
            "download": "/api/historical/download",
            "statistics": "/api/historical/statistics",
            "best_models": "/api/historical/best-models/{symbol}"
        }
    }'''
    
    # Health endpoint to add
    health_endpoint = '''

@app.get("/api/health")
async def health_check():
    """Health check endpoint for frontend connectivity"""
    return {
        "status": "healthy",
        "service": "Stock Tracker Backend",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0"
    }'''
    
    # Insert health endpoint after root endpoint
    if root_endpoint in content:
        content = content.replace(root_endpoint, root_endpoint + health_endpoint)
        
        # Write fixed content
        with open('backend.py', 'w') as f:
            f.write(content)
        
        print("✓ Added /api/health endpoint to backend.py")
        print("\nThe health endpoint will return:")
        print("  - status: 'healthy'")
        print("  - service: 'Stock Tracker Backend'")
        print("  - timestamp: current ISO timestamp")
        print("  - version: '4.0.0'")
    else:
        print("⚠ Could not find insertion point for health endpoint")
        print("  Attempting alternative insertion...")
        
        # Alternative: Add after imports but before first endpoint
        lines = content.split('\n')
        insert_index = -1
        
        for i, line in enumerate(lines):
            if '@app.get("/")' in line:
                # Find the end of this function
                brace_count = 0
                for j in range(i, len(lines)):
                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')
                    if brace_count == 0 and j > i and lines[j].strip() == '}':
                        insert_index = j + 1
                        break
                break
        
        if insert_index > 0:
            lines.insert(insert_index, health_endpoint)
            content = '\n'.join(lines)
            
            with open('backend.py', 'w') as f:
                f.write(content)
            
            print("✓ Added /api/health endpoint using alternative method")

def create_test_script():
    """Create a script to test the health endpoint"""
    
    test_script = '''@echo off
echo Testing Backend Health Endpoint...
echo.

curl -s http://localhost:8002/api/health
echo.
echo.

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Health endpoint is working!
) else (
    echo ERROR: Health endpoint not responding
    echo Please restart the backend service
)

echo.
pause
'''
    
    with open('TEST_HEALTH_ENDPOINT.bat', 'w') as f:
        f.write(test_script)
    
    print("\n✓ Created TEST_HEALTH_ENDPOINT.bat to verify the fix")

def main():
    """Main function"""
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    fix_backend_health()
    create_test_script()
    
    print("\n" + "=" * 60)
    print("FIX COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Stop the current backend (Ctrl+C in backend window)")
    print("2. Restart backend: python backend.py")
    print("3. Run TEST_HEALTH_ENDPOINT.bat to verify")
    print("4. Refresh your browser - Backend Status should show 'Connected'")
    print("\nThe 404 error for /api/health should now be resolved!")

if __name__ == "__main__":
    main()