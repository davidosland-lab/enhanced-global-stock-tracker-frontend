#!/usr/bin/env python3
"""
Start the server with proper error handling
"""

import os
import sys
import time

# Set environment
os.environ['FLASK_SKIP_DOTENV'] = '1'
os.environ['YFINANCE_CACHE_DISABLE'] = '1'

print("="*60)
print("STARTING FINBERT SERVER WITH ERROR HANDLING")
print("="*60)

try:
    # Import the app
    print("\nImporting app...")
    import app_finbert_ultimate_original_with_key as app_module
    print("✓ App imported successfully")
    
    # Get the Flask app object
    print("\nGetting Flask app...")
    app = app_module.app
    print("✓ Flask app obtained")
    
    # Try to start the server
    print("\nStarting server on http://localhost:5000...")
    print("="*60)
    print()
    
    # Run with explicit settings
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,  # Disable reloader
        use_debugger=False   # Disable debugger
    )
    
except KeyboardInterrupt:
    print("\n\nServer stopped by user (Ctrl+C)")
    
except Exception as e:
    print(f"\n\n❌ ERROR: {e}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
    
    print("\n" + "="*60)
    print("Server failed to start. Check the error above.")
    print("="*60)
    
    # Keep window open
    input("\nPress Enter to exit...")
    sys.exit(1)

# If we get here, server stopped normally
print("\nServer stopped.")
input("Press Enter to exit...")