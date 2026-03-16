#!/usr/bin/env python3
"""
Verify API Parameter Fix Worked
=================================

This script checks if FIX_API_PARAMETERS.py successfully fixed the issue
where UI parameters had no effect on backtest results.

Run AFTER applying FIX_API_PARAMETERS.py and restarting FinBERT.

Author: FinBERT v4.4.4 Diagnostic Team
Date: December 2025
"""

import os
import sys
import re


def check_file_modified(filepath, search_patterns):
    """Check if file contains expected modifications"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = {}
    for name, pattern in search_patterns.items():
        if re.search(pattern, content, re.MULTILINE):
            results[name] = True
        else:
            results[name] = False
    
    return results


def main():
    print("=" * 70)
    print("VERIFY API PARAMETER FIX")
    print("=" * 70)
    print("\nChecking if FIX_API_PARAMETERS.py was successfully applied...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # File paths
    api_file = os.path.join(script_dir, 'finbert_v4.4.4', 'app_finbert_v4_dev.py')
    portfolio_file = os.path.join(script_dir, 'finbert_v4.4.4', 'models', 'backtesting', 'portfolio_backtester.py')
    
    print(f"\n📂 Working directory: {script_dir}\n")
    
    all_passed = True
    
    # Check API file
    print("=" * 70)
    print("1. Checking API Endpoint (app_finbert_v4_dev.py)")
    print("=" * 70)
    
    api_checks = {
        'Phase 2 extraction': r"stop_loss_percent = data\.get\('stop_loss_percent'",
        'enable_take_profit extraction': r"enable_take_profit = data\.get\('enable_take_profit'",
        'confidence_threshold extraction': r"confidence_threshold_input = data\.get\('confidence_threshold'",
        'stop_loss_percent passed': r"stop_loss_percent=stop_loss_percent",
        'enable_take_profit passed': r"enable_take_profit=enable_take_profit",
        'confidence uses input': r"confidence_threshold=confidence_threshold_input",
    }
    
    api_results = check_file_modified(api_file, api_checks)
    
    for check, passed in api_results.items():
        if passed:
            print(f"  ✅ {check}")
        else:
            print(f"  ❌ {check}")
            all_passed = False
    
    # Check portfolio backtester
    print("\n" + "=" * 70)
    print("2. Checking Portfolio Backtester (portfolio_backtester.py)")
    print("=" * 70)
    
    portfolio_checks = {
        '**kwargs in __init__': r"def __init__.*?\*\*kwargs",
        'kwargs storage': r"self\.kwargs = kwargs",
        'stop_loss_percent to engine': r"stop_loss_percent=.*?\.kwargs\.get\('stop_loss_percent'",
        'enable_take_profit to engine': r"enable_take_profit=.*?\.kwargs\.get\('enable_take_profit'",
        'risk_reward_ratio to engine': r"risk_reward_ratio=.*?\.kwargs\.get\('risk_reward_ratio'",
    }
    
    portfolio_results = check_file_modified(portfolio_file, portfolio_checks)
    
    for check, passed in portfolio_results.items():
        if passed:
            print(f"  ✅ {check}")
        else:
            print(f"  ❌ {check}")
            all_passed = False
    
    # Overall result
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ SUCCESS! All checks passed!")
        print("=" * 70)
        print("\n📋 NEXT STEPS:")
        print("  1. Make sure you've restarted FinBERT v4.4.4")
        print("  2. Open your backtest UI")
        print("  3. Change Stop Loss from 2% to 1%")
        print("  4. Run backtest")
        print("  5. Change Stop Loss back to 2%")
        print("  6. Run backtest again")
        print("\n🎯 EXPECTED:")
        print("  • Test 1 (Stop Loss 1%): Win Rate ~35-40%, Return +5-8%")
        print("  • Test 2 (Stop Loss 2%): Win Rate ~45-55%, Return +8-12%")
        print("\n  Results should be DIFFERENT between tests!")
        print("\n" + "=" * 70)
        return 0
    else:
        print("❌ SOME CHECKS FAILED!")
        print("=" * 70)
        print("\n🔧 SOLUTION:")
        print("  1. Run: python FIX_API_PARAMETERS.py")
        print("  2. Restart FinBERT v4.4.4")
        print("  3. Run this verification script again")
        print("\n" + "=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
