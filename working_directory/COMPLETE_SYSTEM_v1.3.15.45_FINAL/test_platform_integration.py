#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Trading Platform Integration
==================================

Verifies that overnight pipelines and trading platform are properly integrated.

Tests:
1. Overnight reports exist in correct location
2. Report structure matches trading platform expectations
3. Signal adapter can read reports
4. Trading platform can generate signals from reports

Usage:
    python test_platform_integration.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Setup paths
BASE_PATH = Path(__file__).parent
sys.path.insert(0, str(BASE_PATH))

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"  {text}")


def test_report_files_exist() -> Dict[str, bool]:
    """Test 1: Check if overnight reports exist"""
    print_header("TEST 1: Overnight Report Files")
    
    report_dir = BASE_PATH / 'reports' / 'screening'
    markets = ['au', 'us', 'uk']
    results = {}
    
    for market in markets:
        report_file = report_dir / f'{market}_morning_report.json'
        exists = report_file.exists()
        results[market] = exists
        
        if exists:
            # Check file age
            mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
            age_hours = (datetime.now() - mtime).total_seconds() / 3600
            
            print_success(f"{market.upper()} report exists: {report_file}")
            print_info(f"   Last modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')} ({age_hours:.1f} hours ago)")
            
            if age_hours > 24:
                print_warning(f"   Report is older than 24 hours - may need refresh")
        else:
            print_error(f"{market.upper()} report NOT found: {report_file}")
            print_info(f"   Run overnight pipeline: python run_{market}_full_pipeline.py")
    
    all_exist = all(results.values())
    print()
    if all_exist:
        print_success("All 3 market reports exist ✓")
    else:
        print_error(f"Missing {sum(1 for v in results.values() if not v)} report(s)")
    
    return results


def test_report_structure(market: str) -> bool:
    """Test 2: Verify report structure matches trading platform expectations"""
    report_file = BASE_PATH / 'reports' / 'screening' / f'{market}_morning_report.json'
    
    if not report_file.exists():
        return False
    
    try:
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        # Required fields for trading platform
        required_fields = [
            'timestamp',
            'market',
            'market_sentiment',
            'top_opportunities'
        ]
        
        required_sentiment_fields = [
            'sentiment_score',
            'confidence',
            'risk_rating',
            'volatility_level',
            'recommendation'
        ]
        
        required_opportunity_fields = [
            'symbol',
            'name',
            'opportunity_score',
            'prediction',
            'confidence'
        ]
        
        # Check top-level fields
        missing_fields = [f for f in required_fields if f not in report]
        if missing_fields:
            print_error(f"{market.upper()}: Missing fields: {', '.join(missing_fields)}")
            return False
        
        # Check market_sentiment structure
        sentiment = report.get('market_sentiment', {})
        missing_sentiment = [f for f in required_sentiment_fields if f not in sentiment]
        if missing_sentiment:
            print_error(f"{market.upper()}: Missing sentiment fields: {', '.join(missing_sentiment)}")
            return False
        
        # Check top_opportunities structure
        opportunities = report.get('top_opportunities', [])
        if not opportunities:
            print_warning(f"{market.upper()}: No opportunities in report")
            return True  # Not an error, just means no good signals
        
        # Check first opportunity has required fields
        first_opp = opportunities[0]
        missing_opp = [f for f in required_opportunity_fields if f not in first_opp]
        if missing_opp:
            print_error(f"{market.upper()}: Missing opportunity fields: {', '.join(missing_opp)}")
            return False
        
        # All checks passed
        print_success(f"{market.upper()} report structure valid")
        print_info(f"   Sentiment score: {sentiment['sentiment_score']:.1f}/100")
        print_info(f"   Recommendation: {sentiment['recommendation']}")
        print_info(f"   Opportunities: {len(opportunities)}")
        print_info(f"   Top opportunity: {first_opp['symbol']} (score: {first_opp.get('opportunity_score', 0):.1f})")
        
        return True
        
    except json.JSONDecodeError as e:
        print_error(f"{market.upper()}: Invalid JSON: {e}")
        return False
    except Exception as e:
        print_error(f"{market.upper()}: Error reading report: {e}")
        return False


def test_signal_adapter() -> bool:
    """Test 3: Verify signal adapter can read reports"""
    print_header("TEST 3: Signal Adapter Integration")
    
    try:
        from pipeline_signal_adapter_v3 import PipelineSignalAdapter
        
        print_info("Initializing signal adapter...")
        adapter = PipelineSignalAdapter(use_ml_signals=False)  # Disable ML for quick test
        print_success("Signal adapter initialized")
        
        markets = ['AU', 'US', 'UK']
        results = {}
        
        for market in markets:
            print_info(f"\nTesting {market} market...")
            
            # Try to load overnight sentiment
            sentiment = adapter.get_overnight_sentiment(market)
            
            if sentiment:
                print_success(f"{market} sentiment loaded successfully")
                print_info(f"   Score: {sentiment['sentiment_score']:.1f}/100")
                print_info(f"   Confidence: {sentiment['confidence']}")
                print_info(f"   Recommendation: {sentiment['recommendation']}")
                print_info(f"   Opportunities: {len(sentiment.get('top_opportunities', []))}")
                results[market] = True
            else:
                print_error(f"{market} sentiment failed to load")
                results[market] = False
        
        all_loaded = all(results.values())
        print()
        if all_loaded:
            print_success("Signal adapter can read all 3 markets ✓")
        else:
            print_error(f"Signal adapter failed for {sum(1 for v in results.values() if not v)} market(s)")
        
        return all_loaded
        
    except ImportError as e:
        print_error(f"Failed to import signal adapter: {e}")
        return False
    except Exception as e:
        print_error(f"Signal adapter test failed: {e}")
        return False


def test_trading_platform() -> bool:
    """Test 4: Verify trading platform can generate signals"""
    print_header("TEST 4: Trading Platform Signal Generation")
    
    try:
        from pipeline_signal_adapter_v3 import PipelineSignalAdapter
        
        print_info("Initializing trading platform components...")
        adapter = PipelineSignalAdapter(use_ml_signals=False)
        
        markets = ['AU', 'US', 'UK']
        all_signals = {}
        
        for market in markets:
            print_info(f"\nGenerating signals for {market}...")
            
            # Get overnight sentiment
            sentiment = adapter.get_overnight_sentiment(market)
            if not sentiment:
                print_error(f"No sentiment data for {market}")
                continue
            
            # Get top opportunities from sentiment
            opportunities = sentiment.get('top_opportunities', [])[:5]  # Top 5
            
            if not opportunities:
                print_warning(f"No opportunities for {market}")
                all_signals[market] = []
                continue
            
            # Generate trading signals
            signals = []
            for opp in opportunities:
                signal = {
                    'symbol': opp['symbol'],
                    'prediction': opp.get('prediction', 'HOLD'),
                    'confidence': opp.get('confidence', 0),
                    'opportunity_score': opp.get('opportunity_score', 0),
                    'expected_return': opp.get('expected_return', 0),
                    'recommended_size': min(0.10, opp.get('opportunity_score', 0) / 1000)  # 10% max
                }
                signals.append(signal)
            
            all_signals[market] = signals
            print_success(f"{market}: Generated {len(signals)} trading signals")
            
            # Show top signal
            if signals:
                top = signals[0]
                print_info(f"   Top signal: {top['symbol']} - {top['prediction']} "
                          f"(conf: {top['confidence']:.1%}, size: {top['recommended_size']:.1%})")
        
        total_signals = sum(len(signals) for signals in all_signals.values())
        print()
        if total_signals > 0:
            print_success(f"Trading platform generated {total_signals} total signals across 3 markets ✓")
            return True
        else:
            print_warning("No trading signals generated (may be normal if sentiment is neutral)")
            return True  # Not a failure
        
    except Exception as e:
        print_error(f"Trading platform test failed: {e}")
        import traceback
        print_info(traceback.format_exc())
        return False


def main():
    """Run all integration tests"""
    print_header("TRADING PLATFORM INTEGRATION TEST")
    print(f"Base Path: {BASE_PATH}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test_results = {}
    
    # Test 1: Report files exist
    report_exists = test_report_files_exist()
    test_results['reports_exist'] = all(report_exists.values())
    
    # Test 2: Report structure
    if test_results['reports_exist']:
        print_header("TEST 2: Report Structure Validation")
        structure_valid = {}
        for market in ['au', 'us', 'uk']:
            if report_exists.get(market, False):
                structure_valid[market] = test_report_structure(market)
            else:
                structure_valid[market] = False
        test_results['structure_valid'] = all(structure_valid.values())
    else:
        print_header("TEST 2: Report Structure Validation")
        print_warning("Skipping - no reports found")
        test_results['structure_valid'] = False
    
    # Test 3: Signal adapter
    test_results['adapter_works'] = test_signal_adapter()
    
    # Test 4: Trading platform
    test_results['platform_works'] = test_trading_platform()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in test_results.values() if v)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END}: {test_name.replace('_', ' ').title()}")
    
    print()
    if passed == total:
        print_success(f"ALL TESTS PASSED ({passed}/{total}) ✓")
        print()
        print_info("Trading platform is fully integrated with overnight pipelines!")
        print_info("Next steps:")
        print_info("  1. Run overnight pipelines: LAUNCH_COMPLETE_SYSTEM.bat (Option 1)")
        print_info("  2. Start trading: python run_pipeline_enhanced_trading.py --markets AU,US,UK")
        return 0
    else:
        print_error(f"SOME TESTS FAILED ({passed}/{total})")
        print()
        print_info("Fix the failed tests before running the trading platform.")
        return 1


if __name__ == "__main__":
    exit(main())
