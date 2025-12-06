#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test if backtest parameters are actually being used
===================================================

This script runs backtests with DIFFERENT parameters and checks
if results actually change.
"""

import sys
import os

# Add path
sys.path.insert(0, os.path.join(os.getcwd(), 'finbert_v4.4.4'))

print("\n" + "="*70)
print("  BACKTEST PARAMETER TEST")
print("="*70)

try:
    from models.backtesting.backtest_engine import PortfolioBacktestEngine
    print("\n✓ Successfully imported PortfolioBacktestEngine")
except ImportError as e:
    print(f"\n✗ Import failed: {e}")
    print("\nMake sure you're running from: C:\\Users\\david\\AATelS")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("\n" + "="*70)
print("  TEST 1: Different Stop-Loss Percentages")
print("="*70)

# Test 1: 1% stop-loss
print("\n[1/3] Testing with 1% stop-loss...")
engine1 = PortfolioBacktestEngine(
    initial_capital=100000,
    allocation_strategy='equal',
    enable_stop_loss=True,
    stop_loss_percent=1.0,
    enable_take_profit=False
)

print(f"  Engine 1 created:")
print(f"    allocation_strategy: {engine1.allocation_strategy}")
print(f"    stop_loss_percent: {engine1.stop_loss_percent}")
print(f"    enable_take_profit: {engine1.enable_take_profit}")

# Test 2: 5% stop-loss
print("\n[2/3] Testing with 5% stop-loss...")
engine2 = PortfolioBacktestEngine(
    initial_capital=100000,
    allocation_strategy='equal',
    enable_stop_loss=True,
    stop_loss_percent=5.0,
    enable_take_profit=False
)

print(f"  Engine 2 created:")
print(f"    allocation_strategy: {engine2.allocation_strategy}")
print(f"    stop_loss_percent: {engine2.stop_loss_percent}")
print(f"    enable_take_profit: {engine2.enable_take_profit}")

# Test 3: 10% stop-loss
print("\n[3/3] Testing with 10% stop-loss...")
engine3 = PortfolioBacktestEngine(
    initial_capital=100000,
    allocation_strategy='equal',
    enable_stop_loss=True,
    stop_loss_percent=10.0,
    enable_take_profit=False
)

print(f"  Engine 3 created:")
print(f"    allocation_strategy: {engine3.allocation_strategy}")
print(f"    stop_loss_percent: {engine3.stop_loss_percent}")
print(f"    enable_take_profit: {engine3.enable_take_profit}")

print("\n" + "="*70)
print("  TEST 2: Check Default Values")
print("="*70)

engine_default = PortfolioBacktestEngine(initial_capital=100000)

print(f"\nDefault engine parameters:")
print(f"  allocation_strategy:    {engine_default.allocation_strategy}")
print(f"  stop_loss_percent:      {engine_default.stop_loss_percent}")
print(f"  enable_stop_loss:       {engine_default.enable_stop_loss}")
print(f"  enable_take_profit:     {engine_default.enable_take_profit}")
print(f"  risk_reward_ratio:      {engine_default.risk_reward_ratio}")
print(f"  risk_per_trade_percent: {engine_default.risk_per_trade_percent}")
print(f"  max_portfolio_heat:     {engine_default.max_portfolio_heat}")
print(f"  max_position_size_percent: {engine_default.max_position_size_percent}")

print("\n" + "="*70)
print("  ANALYSIS")
print("="*70)

# Check if parameters are actually different
if engine1.stop_loss_percent == engine2.stop_loss_percent == engine3.stop_loss_percent:
    print("\n✗ PROBLEM: All engines have SAME stop-loss despite different settings!")
    print("  This means parameters are being IGNORED!")
else:
    print("\n✓ GOOD: Engines have different stop-loss percentages")
    print(f"  Engine 1: {engine1.stop_loss_percent}%")
    print(f"  Engine 2: {engine2.stop_loss_percent}%")
    print(f"  Engine 3: {engine3.stop_loss_percent}%")

# Check if defaults are correct
print("\n" + "-"*70)
print("  DEFAULT CONFIGURATION CHECK:")
print("-"*70)

issues = []

if engine_default.allocation_strategy != 'risk_based':
    issues.append(f"allocation_strategy is '{engine_default.allocation_strategy}' (should be 'risk_based')")

if engine_default.stop_loss_percent != 2.0:
    issues.append(f"stop_loss_percent is {engine_default.stop_loss_percent} (should be 2.0)")

if engine_default.enable_take_profit != True:
    issues.append(f"enable_take_profit is {engine_default.enable_take_profit} (should be True)")

if issues:
    print("\n✗ ISSUES FOUND:")
    for issue in issues:
        print(f"  - {issue}")
    print("\n  FIX: Run python FIX_BACKTEST_ENGINE_DEFAULTS_v2.py")
else:
    print("\n✓ All defaults are correct!")

print("\n" + "="*70)
print("  NEXT STEPS")
print("="*70)

print("\nIf parameters ARE being respected in the engine:")
print("  → The problem is in the UI or API layer")
print("  → The frontend might not be sending parameters")
print("  → Or the backend might be caching results")

print("\nIf parameters are NOT being respected:")
print("  → The backtest engine has a bug")
print("  → Parameters need to be fixed")

print("\n" + "="*70)

# Check for cache
print("\n  CHECKING FOR CACHE FILES:")
print("-"*70)

cache_locations = [
    'cache',
    'finbert_v4.4.4/cache',
    'finbert_v4.4.4/models/backtesting/cache',
    '__pycache__',
    'finbert_v4.4.4/__pycache__',
    'finbert_v4.4.4/models/__pycache__',
    'finbert_v4.4.4/models/backtesting/__pycache__',
]

found_cache = False
for cache_dir in cache_locations:
    if os.path.exists(cache_dir):
        files = os.listdir(cache_dir)
        if files:
            print(f"\n✓ Found cache: {cache_dir}")
            print(f"  Files: {len(files)}")
            found_cache = True

if found_cache:
    print("\n⚠ CACHE FOUND!")
    print("  This might be causing identical results")
    print("  Solution: Delete cache folders or restart FinBERT")
else:
    print("\n✓ No cache folders found")

print("\n" + "="*70)
input("\nPress Enter to exit...")
