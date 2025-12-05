#!/usr/bin/env python3
"""
Phase 2 Installation Verification Tool
======================================

This script checks if Phase 1 & 2 patch was installed correctly.

Usage:
    cd C:\Users\david\AATelS
    python VERIFY_PHASE2_INSTALLATION.py
"""

import os
import sys

def main():
    print("\n" + "="*70)
    print("  PHASE 2 INSTALLATION VERIFICATION")
    print("="*70)
    
    engine_path = 'finbert_v4.4.4/models/backtesting/backtest_engine.py'
    
    if not os.path.exists(engine_path):
        print("\n❌ CRITICAL ERROR")
        print(f"   File not found: {engine_path}")
        print("\n   Are you in the correct directory?")
        print(f"   Current directory: {os.getcwd()}")
        return False
    
    # Read the file
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Phase 2 features
    print("\n🔍 Checking for Phase 2 features in backtest_engine.py...")
    print()
    
    features = {
        'enable_take_profit': {
            'name': 'Enable Take-Profit Parameter',
            'pattern': 'enable_take_profit',
            'critical': True
        },
        'risk_reward_ratio': {
            'name': 'Risk:Reward Ratio Parameter',
            'pattern': 'risk_reward_ratio',
            'critical': True
        },
        'take_profit_type': {
            'name': 'Take-Profit Type Parameter',
            'pattern': 'take_profit_type',
            'critical': True
        },
        'calculate_take_profit': {
            'name': 'Calculate Take-Profit Method',
            'pattern': 'def calculate_take_profit_price',
            'critical': True
        },
        'risk_per_trade_percent': {
            'name': 'Risk Per Trade Parameter',
            'pattern': 'risk_per_trade_percent',
            'critical': True
        },
        'max_portfolio_heat': {
            'name': 'Max Portfolio Heat Parameter',
            'pattern': 'max_portfolio_heat',
            'critical': True
        },
        'stop_loss_type': {
            'name': 'Stop-Loss Type Parameter',
            'pattern': 'stop_loss_type',
            'critical': False
        }
    }
    
    results = {}
    critical_missing = []
    
    for key, feature in features.items():
        present = feature['pattern'] in content
        results[key] = present
        
        status = "✅" if present else "❌"
        critical = " [CRITICAL]" if feature['critical'] else ""
        print(f"{status} {feature['name']}{critical}")
        
        if not present and feature['critical']:
            critical_missing.append(feature['name'])
    
    # Overall result
    print("\n" + "="*70)
    
    if all(results.values()):
        print("✅ SUCCESS: All Phase 2 features are present!")
        print()
        print("Your backtest_engine.py has been updated correctly.")
        print()
        print("Next step: Enable these features in the defaults")
        print()
        print("Edit backtest_engine.py and change:")
        print("  allocation_strategy: str = 'risk_based'")
        print("  enable_take_profit: bool = True")
        print("  stop_loss_percent: float = 2.0")
        return True
        
    elif critical_missing:
        print("❌ FAILURE: Critical Phase 2 features are MISSING!")
        print()
        print("Missing critical features:")
        for feature in critical_missing:
            print(f"  - {feature}")
        print()
        print("This means: Phase 1 & 2 patch was NOT installed correctly!")
        print()
        print("SOLUTION:")
        print("1. Re-download PHASE1_PHASE2_PATCH.zip")
        print("2. Extract to Desktop")
        print("3. Copy PHASE1_PHASE2_PATCH folder to C:\\Users\\david\\AATelS\\")
        print("4. Run INSTALL.bat")
        print("5. Make sure you see 'INSTALLATION COMPLETE'")
        print("6. Run this verification script again")
        return False
    else:
        print("⚠️  PARTIAL: Some features missing but not critical")
        print()
        print("Most Phase 2 features are present.")
        print("You should still be able to use take-profit functionality.")
        return True
    
    print("="*70)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
