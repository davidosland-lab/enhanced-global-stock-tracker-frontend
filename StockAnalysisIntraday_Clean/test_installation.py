#!/usr/bin/env python3
"""
Installation Test Script
Verifies all required packages are installed and working
"""

import sys
import importlib
from datetime import datetime

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name:<20} - Installed")
        return True
    except ImportError:
        print(f"❌ {package_name:<20} - Not installed")
        return False

def main():
    print("=" * 60)
    print("Stock Analysis System - Installation Test")
    print("=" * 60)
    print()
    
    # Check Python version
    python_version = sys.version.split()[0]
    major, minor = map(int, python_version.split('.')[:2])
    
    if major >= 3 and minor >= 8:
        print(f"✅ Python {python_version} - Compatible")
    else:
        print(f"⚠️  Python {python_version} - Upgrade recommended (3.8+)")
    
    print()
    print("Checking required packages:")
    print("-" * 40)
    
    # Test required packages
    required = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('yfinance', 'yfinance'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('sklearn', 'scikit-learn'),
        ('requests', 'requests')
    ]
    
    optional = [
        ('ta', 'ta (Technical Analysis)')
    ]
    
    all_installed = True
    for module, name in required:
        if not test_import(module, name):
            all_installed = False
    
    print()
    print("Checking optional packages:")
    print("-" * 40)
    
    for module, name in optional:
        test_import(module, name)
    
    print()
    print("=" * 60)
    
    if all_installed:
        print("✅ All required packages are installed!")
        print("You can start the application with: python app.py")
    else:
        print("❌ Some packages are missing!")
        print("Run: pip install -r requirements.txt")
    
    print("=" * 60)
    
    # Test Yahoo Finance connection
    print()
    print("Testing Yahoo Finance connection...")
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        hist = ticker.history(period="1d")
        if not hist.empty:
            print("✅ Yahoo Finance connection successful!")
            print(f"   AAPL current price: ${hist['Close'].iloc[-1]:.2f}")
        else:
            print("⚠️  Yahoo Finance returned no data")
    except Exception as e:
        print(f"❌ Yahoo Finance test failed: {str(e)}")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()