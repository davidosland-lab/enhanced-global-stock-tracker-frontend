"""
Test script to verify US Stock Scanner data format fixes

This script tests that the US stock scanner now produces data in the format
expected by batch_predictor, with proper nested technical dict and fundamentals.
"""

import sys
import json
from pathlib import Path

# Add models directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models.screening.us_stock_scanner import USStockScanner

def test_scanner_output_format():
    """Test that scanner output matches expected format"""
    
    print("="*80)
    print("US STOCK SCANNER FORMAT TEST")
    print("="*80)
    
    # Initialize scanner
    scanner = USStockScanner()
    
    # Test with a single stock
    test_symbol = "AAPL"
    print(f"\nTesting scanner with {test_symbol}...")
    
    try:
        result = scanner.analyze_stock(test_symbol, sector_weight=1.4)
        
        if result is None:
            print(f"❌ FAILED: No data returned for {test_symbol}")
            return False
        
        print(f"\n✓ Data received for {test_symbol}")
        print(f"\nChecking required fields...")
        
        # Check required top-level fields
        required_fields = [
            'symbol', 'name', 'price', 'price_change', 'volume', 
            'avg_volume', 'score', 'market_cap', 'beta', 'sector_name', 'technical'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field in result:
                print(f"  ✓ {field}: {result[field] if field != 'technical' else '(nested dict)'}")
            else:
                print(f"  ❌ {field}: MISSING")
                missing_fields.append(field)
        
        # Check technical nested dictionary
        print(f"\nChecking technical dictionary structure...")
        if 'technical' in result:
            technical = result['technical']
            required_technical = ['rsi', 'ma_20', 'ma_50', 'volatility', 'above_ma20', 'above_ma50']
            
            tech_missing = []
            for field in required_technical:
                if field in technical:
                    print(f"  ✓ technical.{field}: {technical[field]}")
                else:
                    print(f"  ❌ technical.{field}: MISSING")
                    tech_missing.append(field)
            
            if tech_missing:
                print(f"\n❌ FAILED: Missing technical fields: {tech_missing}")
                return False
        else:
            print(f"  ❌ technical dictionary: MISSING")
            return False
        
        # Check key naming (underscores in technical dict)
        if 'ma_20' not in result['technical'] or 'ma_50' not in result['technical']:
            print(f"\n❌ FAILED: Technical dict uses wrong key names (should be ma_20, ma_50 with underscores)")
            return False
        
        if missing_fields:
            print(f"\n❌ FAILED: Missing required fields: {missing_fields}")
            return False
        
        # Display full structure
        print(f"\n" + "="*80)
        print("FULL DATA STRUCTURE:")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))
        
        print(f"\n" + "="*80)
        print("✅ TEST PASSED - Data format is correct!")
        print("="*80)
        print("\nKey improvements:")
        print("  1. ✓ Technical data nested in 'technical' dict")
        print("  2. ✓ Keys use underscores (ma_20, ma_50)")
        print("  3. ✓ Fundamental data included (market_cap, beta, name)")
        print("  4. ✓ Compatible with batch_predictor expectations")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR:")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scanner_output_format()
    sys.exit(0 if success else 1)
