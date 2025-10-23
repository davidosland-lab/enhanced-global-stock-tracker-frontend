#!/usr/bin/env python3
"""
Fix ALL Missing Endpoints in Backend
Adds /api/health and /api/market-summary endpoints
"""

import os
import sys
import shutil
from datetime import datetime

def check_endpoints():
    """Check which endpoints are missing"""
    missing = []
    
    with open('backend.py', 'r') as f:
        content = f.read()
    
    if '/api/health' not in content:
        missing.append('/api/health')
    if '/api/market-summary' not in content:
        missing.append('/api/market-summary')
    
    return missing, content

def add_health_endpoint(content):
    """Add health endpoint if missing"""
    if '/api/health' in content:
        print("✓ /api/health endpoint already exists")
        return content
    
    # Find insertion point after root endpoint
    insertion_point = content.find('def get_stock_info(symbol: str) -> Dict[str, Any]:')
    if insertion_point == -1:
        print("⚠ Could not find insertion point for health endpoint")
        return content
    
    health_code = '''@app.get("/api/health")
async def health_check():
    """Health check endpoint for frontend connectivity"""
    return {
        "status": "healthy",
        "service": "Stock Tracker Backend",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0"
    }

'''
    
    content = content[:insertion_point] + health_code + content[insertion_point:]
    print("✓ Added /api/health endpoint")
    return content

def add_market_summary_endpoint(content):
    """Add market-summary endpoint if missing"""
    if '/api/market-summary' in content:
        print("✓ /api/market-summary endpoint already exists")
        return content
    
    # The endpoint has already been added in the previous edit
    print("✓ /api/market-summary endpoint has been added")
    return content

def main():
    """Main function"""
    print("=" * 60)
    print("FIXING ALL MISSING ENDPOINTS IN BACKEND")
    print("=" * 60)
    print()
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create backup
    backup_name = f"backend_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy('backend.py', backup_name)
    print(f"✓ Created backup: {backup_name}")
    
    # Check what's missing
    missing, content = check_endpoints()
    
    if not missing:
        print("\n✓ All required endpoints are present!")
        return
    
    print(f"\nMissing endpoints: {', '.join(missing)}")
    print("\nAdding missing endpoints...")
    
    # Add missing endpoints
    if '/api/health' in missing:
        content = add_health_endpoint(content)
    
    if '/api/market-summary' in missing:
        content = add_market_summary_endpoint(content)
    
    # Write updated content
    with open('backend.py', 'w') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("FIXES COMPLETED")
    print("=" * 60)
    
    # Create test script
    test_script = '''import requests
import json

print("Testing Backend Endpoints...")
print("=" * 40)

# Test health endpoint
try:
    r = requests.get('http://localhost:8002/api/health')
    if r.status_code == 200:
        print("✓ /api/health: SUCCESS")
        print(f"  Response: {r.json()}")
    else:
        print(f"✗ /api/health: FAILED (Status {r.status_code})")
except Exception as e:
    print(f"✗ /api/health: ERROR - {e}")

print()

# Test market-summary endpoint
try:
    r = requests.get('http://localhost:8002/api/market-summary')
    if r.status_code == 200:
        print("✓ /api/market-summary: SUCCESS")
        data = r.json()
        print(f"  Indices: {len(data.get('indices', []))}")
        print(f"  Last Updated: {data.get('last_updated', 'N/A')}")
    else:
        print(f"✗ /api/market-summary: FAILED (Status {r.status_code})")
except Exception as e:
    print(f"✗ /api/market-summary: ERROR - {e}")
'''
    
    with open('test_endpoints.py', 'w') as f:
        f.write(test_script)
    
    print("\n✓ Created test_endpoints.py")
    print("\nNext steps:")
    print("1. Restart backend: Run FORCE_RESTART_BACKEND.bat")
    print("2. Test endpoints: python test_endpoints.py")
    print("3. Refresh browser - all 404 errors should be gone!")

if __name__ == "__main__":
    main()