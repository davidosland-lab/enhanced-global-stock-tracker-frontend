#!/usr/bin/env python3
"""
Installation Verification Script for Swing Trading Backtest
Checks that all components are properly installed
"""

import os
import sys

def check_file_exists(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✓ {description}: {path} ({size:,} bytes)")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {path}")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {description} available")
        return True
    except ImportError:
        print(f"⚠ {description} not available (optional)")
        return False

def check_endpoint_in_file(file_path):
    """Check if swing endpoint exists in app file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "@app.route('/api/backtest/swing'" in content:
                print(f"✓ API endpoint found in {file_path}")
                return True
            else:
                print(f"✗ API endpoint NOT found in {file_path}")
                print(f"  Run: python scripts/add_api_endpoint.py")
                return False
    except Exception as e:
        print(f"✗ Could not read {file_path}: {e}")
        return False

def main():
    print("=" * 60)
    print("Swing Trading Backtest - Installation Verification")
    print("=" * 60)
    print()
    
    # Get base path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = input("Enter the path to your FinBERT installation: ").strip()
    
    if not os.path.exists(base_path):
        print(f"✗ ERROR: Directory not found: {base_path}")
        return 1
    
    print(f"Checking installation in: {base_path}")
    print()
    
    # Check paths
    backtesting_dir = os.path.join(base_path, 'finbert_v4.4.4', 'models', 'backtesting')
    app_file = os.path.join(base_path, 'finbert_v4.4.4', 'app_finbert_v4_dev.py')
    docs_dir = os.path.join(base_path, 'docs', 'swing_trading')
    
    passed = 0
    failed = 0
    warnings = 0
    
    # Check code files
    print("Checking code files...")
    print("-" * 60)
    
    files_to_check = [
        (os.path.join(backtesting_dir, 'swing_trader_engine.py'), 
         "Swing Trader Engine"),
        (os.path.join(backtesting_dir, 'news_sentiment_fetcher.py'), 
         "News Sentiment Fetcher"),
        (os.path.join(backtesting_dir, 'example_swing_backtest.py'), 
         "Example Script"),
    ]
    
    for file_path, description in files_to_check:
        if check_file_exists(file_path, description):
            passed += 1
        else:
            failed += 1
    
    print()
    
    # Check API endpoint
    print("Checking API endpoint...")
    print("-" * 60)
    if check_endpoint_in_file(app_file):
        passed += 1
    else:
        failed += 1
    print()
    
    # Check documentation
    print("Checking documentation...")
    print("-" * 60)
    
    doc_files = [
        'SWING_TRADING_BACKTEST_COMPLETE.md',
        'SWING_TRADING_MODULE_README.md',
        'SECOND_BACKTEST_DELIVERED.md',
        'QUICK_TEST_GUIDE.md'
    ]
    
    doc_found = 0
    for doc_file in doc_files:
        doc_path = os.path.join(docs_dir, doc_file)
        if os.path.exists(doc_path):
            doc_found += 1
    
    if doc_found == len(doc_files):
        print(f"✓ All documentation files found ({doc_found}/{len(doc_files)})")
        passed += 1
    elif doc_found > 0:
        print(f"⚠ Some documentation files missing ({doc_found}/{len(doc_files)})")
        warnings += 1
    else:
        print(f"✗ No documentation files found")
        failed += 1
    
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    print("-" * 60)
    
    # Required
    required_deps = [
        ('flask', "Flask"),
        ('pandas', "Pandas"),
        ('numpy', "NumPy"),
    ]
    
    for module, description in required_deps:
        if check_import(module, description):
            passed += 1
        else:
            print(f"  ERROR: {description} is required!")
            failed += 1
    
    # Optional
    optional_deps = [
        ('tensorflow', "TensorFlow (for LSTM)"),
        ('transformers', "Transformers (for FinBERT)"),
    ]
    
    for module, description in optional_deps:
        if check_import(module, description):
            passed += 1
        else:
            warnings += 1
    
    print()
    
    # Check if modules can be imported
    print("Checking module imports...")
    print("-" * 60)
    
    sys.path.insert(0, backtesting_dir)
    
    try:
        import swing_trader_engine
        print("✓ swing_trader_engine module imports successfully")
        passed += 1
    except Exception as e:
        print(f"✗ swing_trader_engine import failed: {e}")
        failed += 1
    
    try:
        import news_sentiment_fetcher
        print("✓ news_sentiment_fetcher module imports successfully")
        passed += 1
    except Exception as e:
        print(f"✗ news_sentiment_fetcher import failed: {e}")
        failed += 1
    
    print()
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⚠ Warnings: {warnings}")
    print()
    
    if failed == 0:
        print("🎉 Installation verification PASSED!")
        print()
        print("Next steps:")
        print("1. Restart FinBERT v4.4.4 server")
        print("2. Test with:")
        print("   curl -X POST http://localhost:5001/api/backtest/swing \\")
        print("     -H \"Content-Type: application/json\" \\")
        print("     -d '{\"symbol\": \"AAPL\", \"start_date\": \"2024-01-01\", \"end_date\": \"2024-11-01\"}'")
        print()
        return 0
    else:
        print("❌ Installation verification FAILED")
        print()
        print(f"Please fix the {failed} failed check(s) above and try again.")
        print()
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n✗ Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
