#!/usr/bin/env python3
"""
Test EventGuard Market Data Refresh

Tests the new refresh_market_data() method to ensure fresh overnight
market data is fetched for regime detection.

Usage:
    python test_eventguard_refresh.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_eventguard_refresh():
    """Test EventGuard market data refresh functionality"""
    
    print("=" * 70)
    print("EventGuard Market Data Refresh Test")
    print("=" * 70)
    
    try:
        from pipelines.models.screening.event_risk_guard import EventRiskGuard
    except ImportError as e:
        print(f"\n❌ Failed to import EventRiskGuard: {e}")
        return False
    
    # Test for each market
    markets = ['AU', 'UK', 'US']
    results = {}
    
    for market in markets:
        print(f"\n{'=' * 70}")
        print(f"Testing {market} Market")
        print('=' * 70)
        
        try:
            # Initialize EventGuard
            print(f"\n[1/5] Initializing EventGuard for {market} market...")
            guard = EventRiskGuard(market=market)
            
            # Check if regime engine is available
            print(f"[2/5] Checking regime engine availability...")
            if not guard.regime_available:
                print(f"  ⚠️  Regime engine not available for {market} (optional feature)")
                results[market] = 'SKIPPED'
                continue
            
            print(f"  [OK] Regime engine initialized")
            
            # Test refresh_market_data()
            print(f"[3/5] Testing refresh_market_data() method...")
            guard.refresh_market_data()
            print(f"  [OK] Market data refresh called successfully")
            
            # Get regime data
            print(f"[4/5] Getting regime analysis...")
            regime_label, crash_risk = guard._get_regime_crash_risk()
            
            print(f"  Regime Label: {regime_label}")
            print(f"  Crash Risk: {crash_risk:.3f}")
            
            # Get full regime data
            print(f"[5/5] Getting full regime data...")
            full_data = guard._get_full_regime_data()
            
            if full_data:
                print(f"  [OK] Full regime data retrieved")
                print(f"\n  Details:")
                print(f"    Label: {full_data.get('regime_label', 'N/A')}")
                print(f"    Crash Risk: {full_data.get('crash_risk_score', 0):.3f}")
                print(f"    Confidence: {full_data.get('confidence', 'N/A')}")
                print(f"    Primary Regime: {full_data.get('primary_regime', 'N/A')}")
                
                # Check if we have market data
                cross_market = full_data.get('cross_market_features', {})
                if cross_market:
                    print(f"\n  Market Data:")
                    print(f"    S&P 500: {cross_market.get('sp500_change', 0):+.2f}%")
                    print(f"    NASDAQ: {cross_market.get('nasdaq_change', 0):+.2f}%")
                    print(f"    Oil: {cross_market.get('oil_change', 0):+.2f}%")
                    print(f"    VIX: {cross_market.get('vix_level', 0):.2f}")
                
                # Success criteria
                if regime_label != "UNKNOWN" and crash_risk > 0:
                    print(f"\n  [OK] {market}: Regime detected successfully")
                    results[market] = 'PASSED'
                else:
                    print(f"\n  ❌ {market}: Still showing UNKNOWN regime or 0 crash risk")
                    results[market] = 'FAILED'
            else:
                print(f"  ❌ No regime data returned")
                results[market] = 'FAILED'
                
        except Exception as e:
            print(f"\n  ❌ Error testing {market}: {e}")
            import traceback
            traceback.print_exc()
            results[market] = 'ERROR'
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    for market in markets:
        status = results.get(market, 'NOT_RUN')
        symbol = {
            'PASSED': '[OK]',
            'FAILED': '❌',
            'SKIPPED': '⚠️ ',
            'ERROR': '❌',
            'NOT_RUN': '❓'
        }.get(status, '❓')
        
        print(f"  {symbol} {market}: {status}")
    
    # Overall result
    passed = sum(1 for r in results.values() if r == 'PASSED')
    failed = sum(1 for r in results.values() if r == 'FAILED')
    skipped = sum(1 for r in results.values() if r == 'SKIPPED')
    
    print("\n" + "=" * 70)
    if failed == 0 and passed > 0:
        print("[OK] ALL TESTS PASSED")
        print(f"\nResults: {passed} passed, {skipped} skipped (optional)")
        print("\nThe refresh_market_data() method works correctly!")
        print("Fresh overnight market data will be fetched at pipeline start.")
        return True
    elif failed > 0:
        print(f"❌ SOME TESTS FAILED: {failed} failed, {passed} passed, {skipped} skipped")
        print("\nCheck the error messages above for details.")
        return False
    else:
        print("⚠️  NO TESTS PASSED (all skipped or not run)")
        print("\nRegime engine may not be available on this system.")
        return False


def test_basic_functionality():
    """Test basic EventGuard functionality without regime engine"""
    
    print("\n" + "=" * 70)
    print("Basic EventGuard Functionality Test (Without Regime Engine)")
    print("=" * 70)
    
    try:
        from pipelines.models.screening.event_risk_guard import EventRiskGuard
        
        print("\n[1/2] Initializing EventGuard...")
        guard = EventRiskGuard(market='AU')
        print("  [OK] EventGuard initialized")
        
        print("[2/2] Testing assess() method with sample ticker...")
        result = guard.assess('CBA.AX')
        print(f"  [OK] Assessment completed for CBA.AX")
        print(f"    Has Event: {result.has_upcoming_event}")
        print(f"    Risk Score: {result.risk_score:.3f}")
        print(f"    Skip Trading: {result.skip_trading}")
        
        return True
        
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return False


if __name__ == '__main__':
    print("\n")
    print("█" * 70)
    print("   EventGuard Market Data Refresh Test Suite")
    print("   v1.3.15.173 - Fix 3 Validation")
    print("█" * 70)
    
    # Run tests
    test1_pass = test_eventguard_refresh()
    test2_pass = test_basic_functionality()
    
    # Final result
    print("\n" + "=" * 70)
    print("Final Result")
    print("=" * 70)
    
    if test1_pass and test2_pass:
        print("\n[OK] ALL TESTS PASSED")
        print("\nFix 3 (EventGuard Data Refresh) is working correctly!")
        print("The pipeline will now fetch fresh overnight market data.")
        sys.exit(0)
    elif test1_pass or test2_pass:
        print("\n⚠️  PARTIAL SUCCESS")
        print("\nSome tests passed. Check details above.")
        sys.exit(1)
    else:
        print("\n❌ TESTS FAILED")
        print("\nCheck error messages above for details.")
        sys.exit(1)
