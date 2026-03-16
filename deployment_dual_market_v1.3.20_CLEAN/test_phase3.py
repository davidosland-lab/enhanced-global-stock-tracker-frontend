#!/usr/bin/env python3
"""
Quick test script for Phase 3 implementation
"""
import sys
sys.path.insert(0, 'finbert_v4.4.4')

from models.backtesting.swing_trader_engine import SwingTraderEngine
import inspect

print("="*70)
print("PHASE 3 VERIFICATION SCRIPT")
print("="*70)

# Create engine instance with Phase 3 enabled
engine = SwingTraderEngine(
    use_multi_timeframe=True,
    use_volatility_sizing=True,
    use_ml_optimization=True,
    use_correlation_hedge=True,
    use_earnings_filter=True
)

# Check 1: Verify Phase 3 parameters exist
print("\n✓ Checking Phase 3 Parameters...")
phase3_params = [
    'use_multi_timeframe',
    'use_volatility_sizing',
    'use_ml_optimization',
    'use_correlation_hedge',
    'use_earnings_filter',
    'atr_period',
    'min_position_size',
    'max_volatility_multiplier'
]

all_params_found = True
for param in phase3_params:
    if hasattr(engine, param):
        value = getattr(engine, param)
        print(f"  ✅ {param} = {value}")
    else:
        print(f"  ❌ {param} NOT FOUND!")
        all_params_found = False

# Check 2: Verify Phase 3 methods exist
print("\n✓ Checking Phase 3 Methods...")
phase3_methods = [
    '_calculate_atr',
    '_calculate_volatility_position_size',
    '_get_multi_timeframe_signal',
    '_optimize_parameters_ml',
    '_calculate_market_correlation',
    '_check_earnings_calendar'
]

all_methods_found = True
for method in phase3_methods:
    if hasattr(engine, method):
        sig = inspect.signature(getattr(engine, method))
        print(f"  ✅ {method}{sig}")
    else:
        print(f"  ❌ {method}() NOT FOUND!")
        all_methods_found = False

# Check 3: Verify ML params cache exists
print("\n✓ Checking Phase 3 State Variables...")
state_vars = ['ml_params_cache', 'correlation_tracker', 'market_beta']
for var in state_vars:
    if hasattr(engine, var):
        value = getattr(engine, var)
        print(f"  ✅ {var} = {value}")
    else:
        print(f"  ❌ {var} NOT FOUND!")
        all_methods_found = False

# Final verdict
print("\n" + "="*70)
if all_params_found and all_methods_found:
    print("✅ ✅ ✅  PHASE 3 IS FULLY LOADED AND READY! ✅ ✅ ✅")
    print("\nPhase 3 Features:")
    print("  1. Multi-Timeframe Analysis (Daily + Short-term)")
    print("  2. Volatility-Based Position Sizing (ATR)")
    print("  3. ML Parameter Optimization (per stock)")
    print("  4. Correlation Hedging (market beta tracking)")
    print("  5. Earnings Calendar Filter")
else:
    print("❌ ❌ ❌  PHASE 3 NOT LOADED - MISSING COMPONENTS! ❌ ❌ ❌")
print("="*70)
