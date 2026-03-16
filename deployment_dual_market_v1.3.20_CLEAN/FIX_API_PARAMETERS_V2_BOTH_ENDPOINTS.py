#!/usr/bin/env python3
"""
Fix API Parameters V2 - Fix BOTH Backtest Endpoints
====================================================

Fixes BOTH backtest endpoints:
1. /api/backtest/run (single stock backtest)
2. /api/backtest/portfolio (portfolio backtest)

Previous version had a bug - it referenced confidence_threshold_input
in the wrong endpoint, causing NameError.

This version correctly fixes BOTH endpoints.

Author: FinBERT v4.4.4 Diagnostic Team
Date: December 2025
"""

import os
import sys
import shutil
from datetime import datetime


def backup_file(filepath):
    """Create a timestamped backup of a file"""
    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath}")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✓ Backup created: {backup_path}")
    return True


def fix_single_backtest_endpoint(filepath):
    """Fix /api/backtest/run endpoint (single stock backtest)"""
    
    if not os.path.exists(filepath):
        print(f"❌ API file not found: {filepath}")
        return False
    
    print(f"\n🔧 Fixing SINGLE stock backtest endpoint...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Replace hardcoded confidence_threshold=0.6 with data.get()
    # Find line around 1387: confidence_threshold=0.6 or confidence_threshold=confidence_threshold_input
    
    # Pattern 1: confidence_threshold=0.6 in BacktestPredictionEngine
    if 'BacktestPredictionEngine(\n            model_type=model_type,\n            confidence_threshold=0.6' in content:
        content = content.replace(
            'BacktestPredictionEngine(\n            model_type=model_type,\n            confidence_threshold=0.6',
            'BacktestPredictionEngine(\n            model_type=model_type,\n            confidence_threshold=data.get(\'confidence_threshold\', 0.6)'
        )
        print("✓ Fixed hardcoded confidence_threshold in single backtest")
    
    # Pattern 2: Fix if someone already changed it to confidence_threshold_input (wrong variable)
    if 'confidence_threshold=confidence_threshold_input' in content:
        content = content.replace(
            'confidence_threshold=confidence_threshold_input',
            'confidence_threshold=data.get(\'confidence_threshold\', 0.6)'
        )
        print("✓ Fixed confidence_threshold_input NameError in single backtest")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True


def fix_portfolio_endpoint(filepath):
    """Fix /api/backtest/portfolio endpoint"""
    
    if not os.path.exists(filepath):
        print(f"❌ API file not found: {filepath}")
        return False
    
    print(f"\n🔧 Fixing PORTFOLIO backtest endpoint...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    i = 0
    phase2_params_added = False
    
    while i < len(lines):
        line = lines[i]
        
        # Find rebalance_frequency line in portfolio endpoint
        if 'rebalance_frequency = data.get' in line and 'rebalance' in line and not phase2_params_added:
            new_lines.append(line)
            
            # Check if Phase 2 params already added
            if i + 1 < len(lines) and '# Phase 2 Risk Management Parameters' in lines[i + 1]:
                print("✓ Phase 2 parameters already added to portfolio endpoint")
                phase2_params_added = True
                i += 1
                continue
            
            # Add Phase 2 parameter extraction
            new_lines.append('\n')
            new_lines.append('        # Phase 2 Risk Management Parameters\n')
            new_lines.append('        stop_loss_percent = data.get(\'stop_loss_percent\', 2.0)\n')
            new_lines.append('        enable_stop_loss = data.get(\'enable_stop_loss\', True)\n')
            new_lines.append('        enable_take_profit = data.get(\'enable_take_profit\', True)\n')
            new_lines.append('        risk_reward_ratio = data.get(\'risk_reward_ratio\', 2.0)\n')
            new_lines.append('        risk_per_trade_percent = data.get(\'risk_per_trade_percent\', 1.0)\n')
            new_lines.append('        max_position_size_percent = data.get(\'max_position_size_percent\', 20.0)\n')
            new_lines.append('        max_portfolio_heat = data.get(\'max_portfolio_heat\', 6.0)\n')
            new_lines.append('        confidence_threshold_param = data.get(\'confidence_threshold\', 0.60)\n')
            new_lines.append('\n')
            
            print("✓ Added Phase 2 parameter extraction to portfolio endpoint")
            phase2_params_added = True
            modified = True
            i += 1
            continue
        
        # Replace hardcoded confidence_threshold in portfolio function call
        if 'confidence_threshold=0.6' in line and 'run_portfolio_backtest' in ''.join(lines[max(0, i-5):i+5]):
            line = line.replace('confidence_threshold=0.6', 'confidence_threshold=confidence_threshold_param')
            new_lines.append(line)
            print("✓ Replaced hardcoded confidence_threshold in portfolio call")
            i += 1
            continue
        
        # Find run_portfolio_backtest function call and add Phase 2 params
        if 'results = run_portfolio_backtest(' in line:
            new_lines.append(line)
            
            # Look ahead to find use_cache parameter
            j = i + 1
            found_use_cache = False
            while j < len(lines) and ')' not in lines[j]:
                if 'use_cache=' in lines[j]:
                    found_use_cache = True
                    # Check if Phase 2 params already added
                    if j + 1 < len(lines) and '# Phase 2 Risk Management:' in lines[j + 1]:
                        # Already added, just copy lines
                        while j < len(lines) and ')' not in lines[j]:
                            new_lines.append(lines[j])
                            j += 1
                        if j < len(lines):
                            new_lines.append(lines[j])
                        i = j + 1
                        print("✓ Phase 2 parameters already in portfolio call")
                        break
                    else:
                        # Add Phase 2 params
                        new_lines.append(lines[j])  # use_cache line
                        if ',' not in lines[j]:
                            # Add comma if missing
                            new_lines[-1] = new_lines[-1].rstrip() + ',\n'
                        new_lines.append('            # Phase 2 Risk Management:\n')
                        new_lines.append('            stop_loss_percent=stop_loss_percent,\n')
                        new_lines.append('            enable_stop_loss=enable_stop_loss,\n')
                        new_lines.append('            enable_take_profit=enable_take_profit,\n')
                        new_lines.append('            risk_reward_ratio=risk_reward_ratio,\n')
                        new_lines.append('            risk_per_trade_percent=risk_per_trade_percent,\n')
                        new_lines.append('            max_position_size_percent=max_position_size_percent,\n')
                        new_lines.append('            max_portfolio_heat=max_portfolio_heat\n')
                        j += 1
                        # Copy closing paren
                        if j < len(lines):
                            new_lines.append(lines[j])
                        print("✓ Added Phase 2 parameters to portfolio function call")
                        i = j + 1
                        break
                new_lines.append(lines[j])
                j += 1
            
            if not found_use_cache:
                # Couldn't find use_cache, just continue
                i = j
            continue
        
        new_lines.append(line)
        i += 1
    
    # Write modified content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Portfolio endpoint fixed!")
    return True


def fix_portfolio_backtester(filepath):
    """Fix portfolio_backtester.py to pass Phase 2 params to engine"""
    
    if not os.path.exists(filepath):
        print(f"❌ Portfolio backtester file not found: {filepath}")
        return False
    
    print(f"\n🔧 Fixing portfolio backtester to pass params to engine...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if '**kwargs' in content and 'self.kwargs = kwargs' in content:
        print("✓ Portfolio backtester already has **kwargs support")
        return True
    
    # Fix 1: Add **kwargs to __init__
    if 'def __init__(' in content and '**kwargs' not in content:
        # Find use_cache parameter line
        content = content.replace(
            '        use_cache: bool = True\n    ):',
            '        use_cache: bool = True,\n        **kwargs  # Phase 2 risk management params\n    ):'
        )
        print("✓ Added **kwargs to __init__ signature")
    
    # Fix 2: Store kwargs
    if 'self.use_cache = use_cache' in content and 'self.kwargs = kwargs' not in content:
        content = content.replace(
            '        self.use_cache = use_cache',
            '        self.use_cache = use_cache\n        self.kwargs = kwargs  # Store Phase 2 params'
        )
        print("✓ Added kwargs storage")
    
    # Fix 3: Pass Phase 2 params to PortfolioBacktestEngine
    if 'portfolio_engine = PortfolioBacktestEngine(' in content:
        # Check if already has Phase 2 params
        if 'stop_loss_percent=self.kwargs.get' not in content:
            # Find slippage_rate line and add Phase 2 params after it
            content = content.replace(
                '                slippage_rate=self.slippage_rate\n            )',
                '''                slippage_rate=self.slippage_rate,
                # Phase 2 Risk Management:
                stop_loss_percent=self.kwargs.get('stop_loss_percent', 2.0),
                enable_stop_loss=self.kwargs.get('enable_stop_loss', True),
                enable_take_profit=self.kwargs.get('enable_take_profit', True),
                risk_reward_ratio=self.kwargs.get('risk_reward_ratio', 2.0),
                risk_per_trade_percent=self.kwargs.get('risk_per_trade_percent', 1.0),
                max_position_size_percent=self.kwargs.get('max_position_size_percent', 20.0),
                max_portfolio_heat=self.kwargs.get('max_portfolio_heat', 6.0)
            )'''
            )
            print("✓ Added Phase 2 parameters to PortfolioBacktestEngine instantiation")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Portfolio backtester fixed!")
    return True


def main():
    print("=" * 70)
    print("FIX API PARAMETERS V2 - Fix BOTH Endpoints")
    print("=" * 70)
    print("\nThis fixes the NameError: 'confidence_threshold_input' is not defined")
    print("\nChanges:")
    print("  1. Single stock backtest endpoint (/api/backtest/run)")
    print("  2. Portfolio backtest endpoint (/api/backtest/portfolio)")
    print("  3. Portfolio backtester (portfolio_backtester.py)")
    print("\n" + "=" * 70)
    
    # Determine base directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # File paths
    api_file = os.path.join(script_dir, 'finbert_v4.4.4', 'app_finbert_v4_dev.py')
    portfolio_file = os.path.join(script_dir, 'finbert_v4.4.4', 'models', 'backtesting', 'portfolio_backtester.py')
    
    print(f"\n📂 Working directory: {script_dir}")
    print(f"\n📄 Files to modify:")
    print(f"  1. {api_file}")
    print(f"  2. {portfolio_file}")
    
    # Check if files exist
    if not os.path.exists(api_file):
        print(f"\n❌ API file not found: {api_file}")
        print(f"\n💡 Make sure you're running this from: C:\\Users\\david\\AATelS")
        return 1
    
    if not os.path.exists(portfolio_file):
        print(f"\n❌ Portfolio file not found: {portfolio_file}")
        return 1
    
    # Create backups
    print("\n" + "=" * 70)
    print("📦 CREATING BACKUPS")
    print("=" * 70)
    
    if not backup_file(api_file):
        return 1
    if not backup_file(portfolio_file):
        return 1
    
    # Apply fixes
    print("\n" + "=" * 70)
    print("🔧 APPLYING FIXES")
    print("=" * 70)
    
    success = True
    
    if not fix_single_backtest_endpoint(api_file):
        success = False
    
    if not fix_portfolio_endpoint(api_file):
        success = False
    
    if not fix_portfolio_backtester(portfolio_file):
        success = False
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! All fixes applied!")
        print("=" * 70)
        print("\n📋 NEXT STEPS:")
        print("  1. **Restart FinBERT v4.4.4 completely**")
        print("  2. Clear browser cache (Ctrl+Shift+Del)")
        print("  3. Run backtest again")
        print("  4. Should now work without NameError!")
        print("\n🎯 WHAT WAS FIXED:")
        print("  • Single backtest: confidence_threshold now uses UI input")
        print("  • Portfolio backtest: All Phase 2 params wired through")
        print("  • No more NameError: 'confidence_threshold_input'")
        print("\n" + "=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("❌ ERRORS OCCURRED - Check output above")
        print("=" * 70)
        print("\n💡 Your original files are backed up with .backup_TIMESTAMP extension")
        return 1


if __name__ == '__main__':
    sys.exit(main())
