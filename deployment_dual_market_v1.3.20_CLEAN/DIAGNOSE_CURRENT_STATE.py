#!/usr/bin/env python3
"""
Diagnose Current Backtest State
================================

Checks what configuration is ACTUALLY being used by the backtest engine.

Run this to see:
1. What confidence threshold is active
2. Whether take-profit is enabled
3. What allocation strategy is being used
4. All Phase 2 parameters

Author: FinBERT v4.4.4 Diagnostic Team
Date: December 2025
"""

import os
import sys


def check_backtest_engine_defaults():
    """Check what defaults are set in backtest_engine.py"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    engine_file = os.path.join(
        script_dir,
        'finbert_v4.4.4',
        'models',
        'backtesting',
        'backtest_engine.py'
    )
    
    if not os.path.exists(engine_file):
        print(f"❌ File not found: {engine_file}")
        return None
    
    print("=" * 70)
    print("BACKTEST ENGINE DEFAULTS")
    print("=" * 70)
    print(f"\nFile: {engine_file}\n")
    
    with open(engine_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find __init__ method
    in_init = False
    params = {}
    
    for i, line in enumerate(lines, 1):
        if 'def __init__' in line and 'PortfolioBacktestEngine' in ''.join(lines[max(0, i-10):i]):
            in_init = True
            print(f"Found __init__ at line {i}\n")
            continue
        
        if in_init:
            if line.strip().startswith(')'):
                break
            
            # Extract parameter defaults
            if '=' in line and ':' in line:
                param_line = line.strip()
                if param_line.startswith('#'):
                    continue
                
                # Parse parameter
                parts = param_line.split(':')
                if len(parts) >= 2:
                    param_name = parts[0].strip()
                    rest = ':'.join(parts[1:])
                    
                    if '=' in rest:
                        type_and_default = rest.split('=')
                        default_value = type_and_default[1].strip().rstrip(',')
                        params[param_name] = default_value
    
    # Print key parameters
    critical_params = [
        'allocation_strategy',
        'stop_loss_percent',
        'enable_stop_loss',
        'enable_take_profit',
        'risk_reward_ratio',
        'risk_per_trade_percent',
        'max_position_size_percent',
        'max_portfolio_heat'
    ]
    
    print("CRITICAL PARAMETERS:\n")
    for param in critical_params:
        if param in params:
            value = params[param]
            # Check if value is correct
            if param == 'allocation_strategy' and value == "'equal'":
                print(f"  ❌ {param}: {value}  ← WRONG! Should be 'risk_based'")
            elif param == 'enable_take_profit' and value == 'False':
                print(f"  ❌ {param}: {value}  ← WRONG! Should be True")
            elif param == 'enable_stop_loss' and value == 'False':
                print(f"  ❌ {param}: {value}  ← WRONG! Should be True")
            else:
                print(f"  ✅ {param}: {value}")
        else:
            print(f"  ⚠️  {param}: NOT FOUND")
    
    return params


def check_api_endpoint_parameters():
    """Check what parameters API endpoint is passing"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    api_file = os.path.join(script_dir, 'finbert_v4.4.4', 'app_finbert_v4_dev.py')
    
    if not os.path.exists(api_file):
        print(f"❌ API file not found: {api_file}")
        return False
    
    print("\n" + "=" * 70)
    print("API ENDPOINT CONFIGURATION")
    print("=" * 70)
    print(f"\nFile: {api_file}\n")
    
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check single stock endpoint
    print("1. SINGLE STOCK ENDPOINT (/api/backtest/run):\n")
    
    if "confidence_threshold=data.get('confidence_threshold'" in content:
        print("  ✅ Confidence threshold uses UI input")
    elif 'confidence_threshold=0.6' in content:
        print("  ❌ Confidence threshold HARDCODED to 0.6")
    else:
        print("  ⚠️  Confidence threshold: Unknown state")
    
    # Check portfolio endpoint
    print("\n2. PORTFOLIO ENDPOINT (/api/backtest/portfolio):\n")
    
    checks = {
        "stop_loss_percent = data.get('stop_loss_percent'": "Phase 2 param extraction",
        "enable_take_profit = data.get('enable_take_profit'": "Enable take-profit extraction",
        "stop_loss_percent=stop_loss_percent": "stop_loss_percent passed to engine",
        "enable_take_profit=enable_take_profit": "enable_take_profit passed to engine"
    }
    
    for pattern, description in checks.items():
        if pattern in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description}")
    
    return True


def check_prediction_engine_confidence():
    """Check BacktestPredictionEngine confidence threshold"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pred_engine_file = os.path.join(
        script_dir,
        'finbert_v4.4.4',
        'models',
        'backtesting',
        'prediction_engine.py'
    )
    
    if not os.path.exists(pred_engine_file):
        print(f"⚠️  Prediction engine file not found (might be normal)")
        return None
    
    print("\n" + "=" * 70)
    print("PREDICTION ENGINE CONFIDENCE FILTER")
    print("=" * 70)
    print(f"\nFile: {pred_engine_file}\n")
    
    with open(pred_engine_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for confidence filtering logic
    if 'confidence_threshold' in content:
        print("  ✅ Found confidence_threshold references")
        
        # Check for hardcoded thresholds
        import re
        hardcoded = re.findall(r'confidence[_\s]*>=?[_\s]*0\.\d+', content)
        if hardcoded:
            print(f"  ⚠️  Found hardcoded confidence checks: {hardcoded}")
    else:
        print("  ⚠️  No confidence_threshold found")
    
    return True


def main():
    print("\n")
    print("=" * 70)
    print("BACKTEST DIAGNOSTIC - Current Configuration")
    print("=" * 70)
    print("\nChecking what configuration is ACTUALLY being used...\n")
    
    # Check backtest engine defaults
    params = check_backtest_engine_defaults()
    
    # Check API endpoint
    check_api_endpoint_parameters()
    
    # Check prediction engine
    check_prediction_engine_confidence()
    
    # Summary
    print("\n" + "=" * 70)
    print("DIAGNOSIS SUMMARY")
    print("=" * 70)
    
    if params:
        allocation = params.get('allocation_strategy', '?')
        take_profit = params.get('enable_take_profit', '?')
        stop_loss_pct = params.get('stop_loss_percent', '?')
        
        print(f"\nBacktest Engine Defaults:")
        print(f"  • Allocation Strategy: {allocation}")
        print(f"  • Enable Take-Profit: {take_profit}")
        print(f"  • Stop Loss Percent: {stop_loss_pct}")
        
        # Diagnosis
        print(f"\n🔍 LIKELY ISSUES:\n")
        
        if allocation == "'equal'":
            print("  ❌ 1. Allocation is 'equal' (should be 'risk_based')")
            print("       → This causes inconsistent position sizing")
            print("       → Run: FIX_BACKTEST_ENGINE_DEFAULTS.py")
        
        if take_profit == 'False' or take_profit == '?':
            print("  ❌ 2. Take-profit might not be enabled")
            print("       → This lets losses grow larger than wins")
            print("       → Need to enable take-profit in defaults")
        
        print("\n  ⚠️  3. High confidence thresholds (70-80%) return 0 trades")
        print("       → This means prediction confidence is too low")
        print("       → Recommended: Use 60% confidence or lower")
        
        print("\n  ⚠️  4. Lower confidence (40%) gives MORE trades but WORSE results")
        print("       → This means strategy needs better signal quality")
        print("       → Consider using 60% as sweet spot")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("""
1. If allocation_strategy = 'equal':
   Run: python FIX_BACKTEST_ENGINE_DEFAULTS.py
   
2. If enable_take_profit = False:
   Manually edit backtest_engine.py line ~69
   Change: enable_take_profit: bool = False
   To:     enable_take_profit: bool = True
   
3. For best results:
   • Use Confidence Threshold: 60%
   • Use Stop Loss: 2%
   • Position Size: 20%
   
4. Restart FinBERT v4.4.4 after any changes
""")
    
    print("=" * 70)


if __name__ == '__main__':
    main()
