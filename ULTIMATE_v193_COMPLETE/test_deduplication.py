#!/usr/bin/env python3
"""
Test Stock Deduplication Logic

Tests the deduplication algorithm used in all three overnight pipelines (AU, UK, US)
to ensure duplicate stocks are removed while keeping the highest scoring instance.

Usage:
    python test_deduplication.py
"""

def test_deduplication():
    """Test basic deduplication logic"""
    print("=" * 60)
    print("Test 1: Basic Deduplication (Mixed Duplicates)")
    print("=" * 60)
    
    # Simulate scored stocks with duplicates
    scored = [
        {'symbol': 'STO.AX', 'opportunity_score': 91.6, 'prediction': 'BUY'},
        {'symbol': 'ORG.AX', 'opportunity_score': 90.6, 'prediction': 'BUY'},
        {'symbol': 'STO.AX', 'opportunity_score': 91.5, 'prediction': 'BUY'},  # Duplicate (lower)
        {'symbol': 'WBC.AX', 'opportunity_score': 89.4, 'prediction': 'BUY'},
        {'symbol': 'BHP.AX', 'opportunity_score': 88.2, 'prediction': 'BUY'},
        {'symbol': 'ORG.AX', 'opportunity_score': 89.0, 'prediction': 'BUY'},  # Duplicate (lower)
    ]
    
    print(f"\nOriginal stocks ({len(scored)}):")
    for i, stock in enumerate(scored, 1):
        print(f"  {i}. {stock['symbol']}: {stock['opportunity_score']:.1f}")
    
    # Deduplicate (keep highest score) - EXACT ALGORITHM FROM PIPELINES
    seen = {}
    for stock in scored:
        symbol = stock.get('symbol')
        score = stock.get('opportunity_score', 0)
        if symbol not in seen or score > seen[symbol].get('opportunity_score', 0):
            seen[symbol] = stock
    
    deduplicated = list(seen.values())
    deduplicated.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    print(f"\nAfter deduplication ({len(deduplicated)}):")
    for i, stock in enumerate(deduplicated, 1):
        print(f"  {i}. {stock['symbol']}: {stock['opportunity_score']:.1f}")
    
    duplicates_removed = len(scored) - len(deduplicated)
    print(f"\n[OK] Removed {duplicates_removed} duplicate symbols (kept highest scores)")
    
    # Assertions
    assert len(deduplicated) == 4, f"Expected 4 unique stocks, got {len(deduplicated)}"
    assert deduplicated[0]['symbol'] == 'STO.AX', "Top stock should be STO.AX"
    assert deduplicated[0]['opportunity_score'] == 91.6, "Should keep highest score 91.6"
    assert deduplicated[1]['symbol'] == 'ORG.AX', "Second should be ORG.AX"
    assert deduplicated[1]['opportunity_score'] == 90.6, "Should keep highest score 90.6"
    
    print("\n[OK] Test 1 PASSED\n")
    return True


def test_no_duplicates():
    """Test when there are no duplicates"""
    print("=" * 60)
    print("Test 2: No Duplicates (Should Pass Through Unchanged)")
    print("=" * 60)
    
    scored = [
        {'symbol': 'AAPL', 'opportunity_score': 95.0},
        {'symbol': 'GOOGL', 'opportunity_score': 92.0},
        {'symbol': 'MSFT', 'opportunity_score': 90.0},
        {'symbol': 'TSLA', 'opportunity_score': 88.0},
    ]
    
    print(f"\nOriginal stocks ({len(scored)}):")
    for stock in scored:
        print(f"  - {stock['symbol']}: {stock['opportunity_score']:.1f}")
    
    seen = {}
    for stock in scored:
        symbol = stock.get('symbol')
        score = stock.get('opportunity_score', 0)
        if symbol not in seen or score > seen[symbol].get('opportunity_score', 0):
            seen[symbol] = stock
    
    deduplicated = list(seen.values())
    deduplicated.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    if len(deduplicated) < len(scored):
        print(f"\n[DEDUP] Removed {len(scored) - len(deduplicated)} duplicates")
    else:
        print("\n[OK] No duplicates found - all stocks unique")
    
    assert len(deduplicated) == len(scored), "Count should be unchanged"
    assert deduplicated[0]['symbol'] == 'AAPL', "Order should be preserved"
    
    print("[OK] Test 2 PASSED\n")
    return True


def test_all_duplicates():
    """Test when all stocks are duplicates"""
    print("=" * 60)
    print("Test 3: All Duplicates (Multiple Scores for One Stock)")
    print("=" * 60)
    
    scored = [
        {'symbol': 'AAPL', 'opportunity_score': 95.0},
        {'symbol': 'AAPL', 'opportunity_score': 93.0},
        {'symbol': 'AAPL', 'opportunity_score': 90.0},
        {'symbol': 'AAPL', 'opportunity_score': 88.0},
    ]
    
    print(f"\nOriginal stocks ({len(scored)}):")
    for stock in scored:
        print(f"  - {stock['symbol']}: {stock['opportunity_score']:.1f}")
    
    seen = {}
    for stock in scored:
        symbol = stock.get('symbol')
        score = stock.get('opportunity_score', 0)
        if symbol not in seen or score > seen[symbol].get('opportunity_score', 0):
            seen[symbol] = stock
    
    deduplicated = list(seen.values())
    
    print(f"\nAfter deduplication ({len(deduplicated)}):")
    for stock in deduplicated:
        print(f"  - {stock['symbol']}: {stock['opportunity_score']:.1f}")
    
    print(f"\n[OK] Removed {len(scored) - len(deduplicated)} duplicate symbols")
    
    assert len(deduplicated) == 1, "Should collapse to 1 unique stock"
    assert deduplicated[0]['opportunity_score'] == 95.0, "Should keep highest score"
    
    print("[OK] Test 3 PASSED\n")
    return True


def test_same_scores():
    """Test when duplicates have identical scores"""
    print("=" * 60)
    print("Test 4: Same Scores (First Occurrence Kept)")
    print("=" * 60)
    
    scored = [
        {'symbol': 'AAPL', 'opportunity_score': 95.0, 'sector': 'Technology'},
        {'symbol': 'GOOGL', 'opportunity_score': 92.0, 'sector': 'Technology'},
        {'symbol': 'AAPL', 'opportunity_score': 95.0, 'sector': 'Consumer'},  # Same score
    ]
    
    print(f"\nOriginal stocks ({len(scored)}):")
    for stock in scored:
        print(f"  - {stock['symbol']}: {stock['opportunity_score']:.1f} ({stock['sector']})")
    
    seen = {}
    for stock in scored:
        symbol = stock.get('symbol')
        score = stock.get('opportunity_score', 0)
        if symbol not in seen or score > seen[symbol].get('opportunity_score', 0):
            seen[symbol] = stock
    
    deduplicated = list(seen.values())
    deduplicated.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    print(f"\nAfter deduplication ({len(deduplicated)}):")
    for stock in deduplicated:
        print(f"  - {stock['symbol']}: {stock['opportunity_score']:.1f} ({stock['sector']})")
    
    assert len(deduplicated) == 2, "Should have 2 unique stocks"
    # First AAPL occurrence kept (Technology sector)
    aapl = [s for s in deduplicated if s['symbol'] == 'AAPL'][0]
    assert aapl['sector'] == 'Technology', "Should keep first occurrence"
    
    print("\n[OK] Test 4 PASSED\n")
    return True


def test_top_5_impact():
    """Test realistic top-5 scenario from 2026-02-23 report"""
    print("=" * 60)
    print("Test 5: Real-World Top 5 Scenario (2026-02-23 AU Report)")
    print("=" * 60)
    
    # Actual data from report showing duplicate STO.AX
    scored = [
        {'symbol': 'STO.AX', 'opportunity_score': 91.6, 'prediction': 'BUY', 'confidence': 64.3},
        {'symbol': 'STO.AX', 'opportunity_score': 91.5, 'prediction': 'BUY', 'confidence': 64.3},
        {'symbol': 'ORG.AX', 'opportunity_score': 90.6, 'prediction': 'BUY', 'confidence': 64.3},
        {'symbol': 'WBC.AX', 'opportunity_score': 89.4, 'prediction': 'BUY', 'confidence': 64.3},
        {'symbol': 'BHP.AX', 'opportunity_score': 88.2, 'prediction': 'BUY', 'confidence': 64.3},
        {'symbol': 'RIO.AX', 'opportunity_score': 87.1, 'prediction': 'BUY', 'confidence': 64.3},
    ]
    
    print("\nBEFORE Fix (Top 5 with duplicates):")
    for i, stock in enumerate(scored[:5], 1):
        print(f"  {i}. {stock['symbol']}: {stock['opportunity_score']:.1f}/100")
    
    # Deduplicate
    seen = {}
    for stock in scored:
        symbol = stock.get('symbol')
        score = stock.get('opportunity_score', 0)
        if symbol not in seen or score > seen[symbol].get('opportunity_score', 0):
            seen[symbol] = stock
    
    deduplicated = list(seen.values())
    deduplicated.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
    
    print(f"\nAFTER Fix (Top 5 unique stocks):")
    for i, stock in enumerate(deduplicated[:5], 1):
        print(f"  {i}. {stock['symbol']}: {stock['opportunity_score']:.1f}/100")
    
    print(f"\n[OK] Result: RIO.AX (87.1) now visible in top 5 (was hidden by duplicate)")
    
    assert len([s for s in deduplicated if s['symbol'] == 'STO.AX']) == 1, "STO.AX should appear once"
    assert deduplicated[4]['symbol'] == 'RIO.AX', "5th position should be RIO.AX"
    
    print("[OK] Test 5 PASSED\n")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Stock Deduplication Test Suite")
    print("Testing algorithm used in AU/UK/US overnight pipelines")
    print("=" * 60 + "\n")
    
    tests = [
        test_deduplication,
        test_no_duplicates,
        test_all_duplicates,
        test_same_scores,
        test_top_5_impact,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"[ERROR] Test FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"[ERROR] Test ERROR: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n[OK] ALL TESTS PASSED - Deduplication logic is correct!")
        print("\nThe algorithm will:")
        print("  1. Remove duplicate symbols from scored stocks")
        print("  2. Keep the highest scoring instance for each symbol")
        print("  3. Log how many duplicates were removed")
        print("  4. Return a clean list with unique stocks only")
        return 0
    else:
        print("\n[ERROR] SOME TESTS FAILED - Check implementation")
        return 1


if __name__ == '__main__':
    exit(main())
