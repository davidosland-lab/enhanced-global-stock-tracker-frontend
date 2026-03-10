#!/usr/bin/env python3
"""
Test Enhanced Pipeline Signal Adapter Integration

This script tests:
1. Loading overnight reports (AU/US/UK morning reports)
2. Extracting top stock opportunities
3. Loading overnight sentiment for specific symbols
4. Combining overnight + ML signals (if available)
"""

import sys
import os
from pathlib import Path

# Set offline mode BEFORE imports
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

# Add core directory to path
sys.path.insert(0, str(Path(__file__).parent / 'core'))

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_overnight_reports():
    """Test loading overnight pipeline reports"""
    print("\n" + "=" * 80)
    print("TEST 1: Load Overnight Reports")
    print("=" * 80)
    
    from paper_trading_coordinator import PaperTradingCoordinator
    
    # Create coordinator with minimal symbols
    coordinator = PaperTradingCoordinator(
        symbols=['AAPL', 'MSFT'],  # Just for testing
        initial_capital=100000.0,
        use_real_swing_signals=False,  # Don't need ML for this test
        use_enhanced_adapter=True       # Test the adapter
    )
    
    # Check if reports were loaded
    if hasattr(coordinator, '_overnight_reports_cache'):
        reports = coordinator._overnight_reports_cache
        print(f"\n[OK] Loaded {len(reports)} market reports")
        
        for market, report in reports.items():
            print(f"\n[CHART] {market.upper()} Market:")
            print(f"   Overall Sentiment: {report.get('overall_sentiment', 0):.1f}")
            print(f"   Recommendation: {report.get('recommendation', 'N/A')}")
            print(f"   Risk Rating: {report.get('risk_rating', 'N/A')}")
            print(f"   Report Age: {report.get('age_hours', 0):.1f} hours")
            
            top_stocks = report.get('top_stocks', [])
            print(f"   Top Stocks: {len(top_stocks)}")
            
            for i, stock in enumerate(top_stocks[:3], 1):  # Show first 3
                signals = ', '.join(stock.get('signals', []))
                print(f"     {i}. {stock['symbol']} - Score: {stock.get('sentiment', 0):.1f}, Signals: {signals}")
        
        return True
    else:
        print("\n[ERROR] No overnight reports loaded")
        return False

def test_trading_opportunities():
    """Test getting pre-screened trading opportunities"""
    print("\n" + "=" * 80)
    print("TEST 2: Get Trading Opportunities")
    print("=" * 80)
    
    from paper_trading_coordinator import PaperTradingCoordinator
    
    coordinator = PaperTradingCoordinator(
        symbols=['AAPL', 'MSFT'],
        initial_capital=100000.0,
        use_real_swing_signals=False,
        use_enhanced_adapter=True
    )
    
    # Get opportunities with min score 60
    opportunities = coordinator.get_trading_opportunities(min_score=60.0)
    
    print(f"\n[OK] Found {len(opportunities)} opportunities (score >= 60)")
    
    if opportunities:
        print("\n[TARGET] Top 10 Opportunities:")
        print(f"{'Rank':<5} {'Symbol':<12} {'Score':<8} {'Market':<8} {'Signals'}")
        print("-" * 80)
        
        for i, opp in enumerate(opportunities[:10], 1):
            signals = ', '.join(opp['signals'])
            print(
                f"{i:<5} {opp['symbol']:<12} {opp['opportunity_score']:<8.1f} "
                f"{opp['market'].upper():<8} {signals}"
            )
        
        return True
    else:
        print("\n[!]  No opportunities found (reports may be empty or old)")
        return False

def test_overnight_sentiment():
    """Test loading overnight sentiment for specific symbols"""
    print("\n" + "=" * 80)
    print("TEST 3: Load Overnight Sentiment for Symbols")
    print("=" * 80)
    
    from paper_trading_coordinator import PaperTradingCoordinator
    
    coordinator = PaperTradingCoordinator(
        symbols=['AAPL', 'MSFT'],
        initial_capital=100000.0,
        use_real_swing_signals=False,
        use_enhanced_adapter=True
    )
    
    # Test symbols from different markets
    test_symbols = [
        ('AAPL', 'US Tech'),
        ('BHP.AX', 'AU Mining'),
        ('HSBA.L', 'UK Banking'),
        ('MSFT', 'US Tech'),
        ('RIO.AX', 'AU Mining')
    ]
    
    print("\n[CHART] Overnight Sentiment Lookup:")
    print(f"{'Symbol':<12} {'Market':<15} {'Sentiment':<12} {'Status'}")
    print("-" * 80)
    
    results = []
    for symbol, description in test_symbols:
        sentiment = coordinator._load_overnight_sentiment(symbol)
        
        if sentiment is not None:
            status = "[OK] Found"
            results.append(True)
        else:
            sentiment = 0.0
            status = "[ERROR] Not found"
            results.append(False)
        
        print(f"{symbol:<12} {description:<15} {sentiment:<12.1f} {status}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n[UP] Success Rate: {success_rate:.0f}% ({sum(results)}/{len(results)} symbols found)")
    
    return success_rate > 0

def main():
    """Run all tests"""
    print("\n" + "[U+1F52C]" * 40)
    print("ENHANCED PIPELINE SIGNAL ADAPTER - INTEGRATION TEST")
    print("[U+1F52C]" * 40)
    
    results = {
        'overnight_reports': False,
        'trading_opportunities': False,
        'overnight_sentiment': False
    }
    
    try:
        results['overnight_reports'] = test_overnight_reports()
    except Exception as e:
        print(f"\n[ERROR] TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        results['trading_opportunities'] = test_trading_opportunities()
    except Exception as e:
        print(f"\n[ERROR] TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        results['overnight_sentiment'] = test_overnight_sentiment()
    except Exception as e:
        print(f"\n[ERROR] TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "[OK] PASS" if passed else "[ERROR] FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n[CHART] Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if all(results.values()):
        print("\n[CELEBRATE] ALL TESTS PASSED - Integration working correctly!")
        return 0
    elif any(results.values()):
        print("\n[!]  PARTIAL SUCCESS - Some features working")
        return 1
    else:
        print("\n[ERROR] ALL TESTS FAILED - Check configuration and report files")
        return 2

if __name__ == '__main__':
    sys.exit(main())
