#!/usr/bin/env python3
"""
Test script to verify backend is working correctly
Run this to check if FastAPI routes are properly configured
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("Testing backend import...")
    from simple_ml_backend import app
    print("✓ Backend imported successfully")
    
    # Check available routes
    print("\nAvailable routes:")
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(f"  {route.methods if hasattr(route, 'methods') else 'GET'} {route.path}")
    
    for route in sorted(set(routes)):
        print(route)
    
    print("\n✓ Backend is properly configured!")
    print("\nTo start the server, run:")
    print("  python backend\\simple_ml_backend.py")
    
except ImportError as e:
    print(f"✗ Failed to import backend: {e}")
    print("\nTrying enhanced backend...")
    
    try:
        from enhanced_ml_backend import app
        print("✓ Enhanced backend imported successfully")
        print("\nTo start the server, run:")
        print("  python backend\\enhanced_ml_backend.py")
    except ImportError as e2:
        print(f"✗ Both backends failed to import: {e2}")
        print("\nPlease check your installation")

except Exception as e:
    print(f"✗ Unexpected error: {e}")

input("\nPress Enter to exit...")