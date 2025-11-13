#!/usr/bin/env python3
"""
Debug: Check what's actually being used when screener runs
"""

import sys
import os

# Add paths
sys.path.insert(0, '/home/user/webapp/complete_deployment')
sys.path.insert(0, '/home/user/webapp/complete_deployment/models')

print("="*70)
print("IMPORT DEBUG CHECK")
print("="*70)

# Try importing the modules
print("\n1. Importing stock_scanner...")
try:
    from models.screening.stock_scanner import StockScanner
    print("   ✓ Imported successfully")
    
    # Check the actual file being used
    import inspect
    source_file = inspect.getfile(StockScanner)
    print(f"   Source: {source_file}")
    
    # Check for .info usage in the loaded module
    import re
    with open(source_file, 'r') as f:
        content = f.read()
        info_calls = re.findall(r'(stock\.info|ticker\.info|info\.get)', content)
        if info_calls:
            print(f"   ⚠️  FOUND .info CALLS: {len(info_calls)}")
            # Find line numbers
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'stock.info' in line or 'ticker.info' in line:
                    if 'logger.info' not in line and '#' not in line:
                        print(f"      Line {i}: {line.strip()[:80]}")
        else:
            print(f"   ✓ NO .info calls found")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n2. Checking if data_fetcher gets imported...")
try:
    # Check if it's imported anywhere
    if 'data_fetcher' in sys.modules:
        print("   ⚠️  data_fetcher IS in sys.modules")
        import inspect
        source = inspect.getfile(sys.modules['data_fetcher'])
        print(f"   Source: {source}")
    else:
        print("   ✓ data_fetcher NOT in sys.modules")
except Exception as e:
    print(f"   Error checking: {e}")

print("\n3. Testing stock_scanner directly...")
try:
    scanner = StockScanner()
    print("   ✓ Scanner created")
    
    # Check what methods it has
    if hasattr(scanner, 'data_fetcher'):
        print("   ⚠️  Scanner HAS data_fetcher attribute")
    else:
        print("   ✓ Scanner has NO data_fetcher attribute")
    
    # Try validating a stock
    print("\n4. Testing validate_stock (CBA.AX)...")
    result = scanner.validate_stock('CBA.AX')
    print(f"   Result: {result}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("CHECK COMPLETE")
print("="*70)
