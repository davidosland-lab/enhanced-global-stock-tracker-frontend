"""
Test Macro News Monitor Installation
Quick verification that the module is installed and working
"""

import sys
import os

print("="*80)
print("MACRO NEWS MONITOR - INSTALLATION TEST")
print("="*80)

# Test 1: Check if file exists
print("\n[TEST 1] Checking if macro_news_monitor.py exists...")
file_path = "models/screening/macro_news_monitor.py"
if os.path.exists(file_path):
    size = os.path.getsize(file_path)
    print(f"   ✓ File exists: {file_path}")
    print(f"   ✓ File size: {size:,} bytes")
    if size < 10000:
        print("   ⚠ Warning: File seems small")
else:
    print(f"   ✗ File NOT found: {file_path}")
    print("\n   Run install.bat to install the file")
    sys.exit(1)

# Test 2: Check dependencies
print("\n[TEST 2] Checking dependencies...")
try:
    import requests
    print("   ✓ requests library available")
except ImportError:
    print("   ✗ requests library missing")
    print("   Install: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    print("   ✓ beautifulsoup4 library available")
except ImportError:
    print("   ✗ beautifulsoup4 library missing")
    print("   Install: pip install beautifulsoup4")
    sys.exit(1)

# Test 3: Try importing the module
print("\n[TEST 3] Importing MacroNewsMonitor...")
try:
    from models.screening.macro_news_monitor import MacroNewsMonitor
    print("   ✓ MacroNewsMonitor imported successfully")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 4: Initialize monitor
print("\n[TEST 4] Initializing monitor...")
try:
    monitor = MacroNewsMonitor(market='US')
    print("   ✓ US MacroNewsMonitor initialized")
except Exception as e:
    print(f"   ✗ Initialization failed: {e}")
    sys.exit(1)

# Test 5: Quick functionality test
print("\n[TEST 5] Testing basic functionality...")
print("   (Checking if scraping methods exist)")
try:
    # Check if key methods exist
    assert hasattr(monitor, 'get_macro_sentiment'), "Missing get_macro_sentiment method"
    assert hasattr(monitor, '_safe_request'), "Missing _safe_request method"
    print("   ✓ All required methods present")
except AssertionError as e:
    print(f"   ✗ {e}")
    sys.exit(1)

# Summary
print("\n" + "="*80)
print("INSTALLATION VERIFIED ✓")
print("="*80)
print("\nMacro News Monitor is properly installed!")
print("\nNext steps:")
print("  1. Test real scraping: python test_macro.py")
print("  2. Run pipeline: python models\\screening\\us_overnight_pipeline.py --stocks-per-sector 5")
print("  3. Look for 'MACRO NEWS ANALYSIS' in output")
print("\n" + "="*80)
