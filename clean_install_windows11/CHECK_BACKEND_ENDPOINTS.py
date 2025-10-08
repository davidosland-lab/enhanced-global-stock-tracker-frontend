#!/usr/bin/env python3
"""
Check what endpoints are actually in backend.py
"""

import os
import re

print("=" * 60)
print("CHECKING BACKEND.PY FOR ENDPOINTS")
print("=" * 60)
print()

# Read backend.py
try:
    with open('backend.py', 'r') as f:
        content = f.read()
except FileNotFoundError:
    print("ERROR: backend.py not found!")
    exit(1)

# Find all @app.get and @app.post endpoints
endpoints = re.findall(r'@app\.(get|post|put|delete)\("([^"]+)"\)', content)

print(f"Found {len(endpoints)} endpoints in backend.py:")
print("-" * 40)
for method, path in endpoints:
    print(f"  {method.upper():6} {path}")

print()
print("Checking for critical endpoints:")
print("-" * 40)

critical_endpoints = [
    '/api/health',
    '/api/market-summary',
    '/api/stock/{symbol}',
    '/api/indices',
    '/api/market-movers'
]

for endpoint in critical_endpoints:
    # Handle parameterized endpoints
    endpoint_pattern = endpoint.replace('{symbol}', '{[^}]+}')
    if any(path == endpoint or re.match(endpoint_pattern.replace('{[^}]+}', '{[^}]+}'), path) for _, path in endpoints):
        print(f"  ✓ {endpoint} - FOUND")
    else:
        print(f"  ✗ {endpoint} - MISSING!")

print()
print("=" * 60)

# If health endpoint is missing, show where to add it
if not any(path == '/api/health' for _, path in endpoints):
    print("FIX NEEDED!")
    print("-" * 40)
    print("The /api/health endpoint is MISSING.")
    print("This is why you're getting 404 errors.")
    print()
    print("To fix, add this code after line 99 (after the root endpoint):")
    print()
    print('@app.get("/api/health")')
    print('async def health_check():')
    print('    """Health check endpoint for frontend connectivity"""')
    print('    return {')
    print('        "status": "healthy",')
    print('        "service": "Stock Tracker Backend",')
    print('        "timestamp": datetime.now().isoformat(),')
    print('        "version": "4.0.0"')
    print('    }')
    print()

input("\nPress Enter to exit...")