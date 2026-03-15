#!/usr/bin/env python3
"""
Regime Dashboard Launcher - Fixed for Windows encoding issues
Bypasses .env file loading to avoid UTF-8 decode errors
"""

import os
import sys

# Set environment variable to skip .env loading
os.environ['FLASK_SKIP_DOTENV'] = '1'

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print(" Regime Intelligence Dashboard - Starting...")
print(" Version: v1.3.13 - Windows Compatible")
print("=" * 80)
print()
print("Note: .env file loading is disabled to avoid encoding issues")
print("Dashboard will use default settings:")
print("  - Host: 0.0.0.0")
print("  - Port: 5002")
print("  - Debug: False")
print()
print("=" * 80)
print()

# Import and run the dashboard
try:
    # Import the dashboard module
    import regime_dashboard
    
    # Override the main function to skip .env loading
    from flask import Flask
    from regime_dashboard import app
    
    print("Starting dashboard server...")
    print()
    print("Dashboard will be available at:")
    print("  http://localhost:5002")
    print("  http://127.0.0.1:5002")
    print()
    print("Features:")
    print("  - Live market regime detection")
    print("  - Real-time market data")
    print("  - Sector impact visualization")
    print("  - Cross-market features")
    print("  - Auto-refresh every 5 minutes")
    print()
    print("=" * 80)
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Run the app without loading .env
    app.run(host='0.0.0.0', port=5002, debug=False, load_dotenv=False)
    
except ImportError as e:
    print(f"Error: Could not import regime_dashboard module")
    print(f"Details: {e}")
    print()
    print("Please ensure you are in the correct directory:")
    print("  cd complete_backend_clean_install_v1.3.13")
    print()
    print("And that all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
    
except KeyboardInterrupt:
    print()
    print("=" * 80)
    print(" Dashboard stopped by user")
    print("=" * 80)
    sys.exit(0)
    
except Exception as e:
    print(f"Error starting dashboard: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
