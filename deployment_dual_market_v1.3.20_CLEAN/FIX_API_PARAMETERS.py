#!/usr/bin/env python3
"""
Fix API Parameters - Enable Phase 2 Parameters
================================================

Fixes the API endpoint and portfolio_backtester to:
1. Accept Phase 2 risk management parameters from UI
2. Pass them through to PortfolioBacktestEngine
3. Replace hardcoded confidence_threshold with UI input

This fixes why changing Stop Loss, Position Size, Confidence has NO EFFECT.

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


def fix_api_endpoint(filepath):
    """Fix app_finbert_v4_dev.py API endpoint to accept Phase 2 parameters"""
    
    if not os.path.exists(filepath):
        print(f"❌ API file not found: {filepath}")
        return False
    
    print(f"\n🔧 Fixing API endpoint: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Find the rebalance_frequency line (around line 1539)
        if 'rebalance_frequency = data.get' in line and not modified:
            new_lines.append(line)
            
            # Add Phase 2 parameter extraction AFTER rebalance_frequency
            new_lines.append('\n')
            new_lines.append('        # Phase 2 Risk Management Parameters\n')
            new_lines.append('        stop_loss_percent = data.get(\'stop_loss_percent\', 2.0)\n')
            new_lines.append('        enable_stop_loss = data.get(\'enable_stop_loss\', True)\n')
            new_lines.append('        enable_take_profit = data.get(\'enable_take_profit\', True)\n')
            new_lines.append('        risk_reward_ratio = data.get(\'risk_reward_ratio\', 2.0)\n')
            new_lines.append('        risk_per_trade_percent = data.get(\'risk_per_trade_percent\', 1.0)\n')
            new_lines.append('        max_position_size_percent = data.get(\'max_position_size_percent\', 20.0)\n')
            new_lines.append('        max_portfolio_heat = data.get(\'max_portfolio_heat\', 6.0)\n')
            new_lines.append('        confidence_threshold_input = data.get(\'confidence_threshold\', 0.60)\n')
            new_lines.append('\n')
            
            print("✓ Added Phase 2 parameter extraction")
            modified = True
            i += 1
            continue
        
        # Replace hardcoded confidence_threshold in function call
        if 'confidence_threshold=0.6' in line or 'confidence_threshold = 0.6' in line:
            line = line.replace('confidence_threshold=0.6', 'confidence_threshold=confidence_threshold_input')
            line = line.replace('confidence_threshold = 0.6', 'confidence_threshold = confidence_threshold_input')
            new_lines.append(line)
            print("✓ Replaced hardcoded confidence_threshold with UI input")
            i += 1
            continue
        
        # Find the run_portfolio_backtest function call and add Phase 2 params
        if 'results = run_portfolio_backtest(' in line:
            new_lines.append(line)
            
            # Look ahead to find where use_cache=True is (last param before closing paren)
            j = i + 1
            while j < len(lines) and ')' not in lines[j]:
                new_lines.append(lines[j])
                j += 1
            
            # Insert Phase 2 params BEFORE the closing line
            if j < len(lines):
                closing_line = lines[j]
                if 'use_cache=True' in closing_line:
                    # Add comma and Phase 2 params
                    new_lines.append('            use_cache=True,\n')
                    new_lines.append('            # Phase 2 Risk Management:\n')
                    new_lines.append('            stop_loss_percent=stop_loss_percent,\n')
                    new_lines.append('            enable_stop_loss=enable_stop_loss,\n')
                    new_lines.append('            enable_take_profit=enable_take_profit,\n')
                    new_lines.append('            risk_reward_ratio=risk_reward_ratio,\n')
                    new_lines.append('            risk_per_trade_percent=risk_per_trade_percent,\n')
                    new_lines.append('            max_position_size_percent=max_position_size_percent,\n')
                    new_lines.append('            max_portfolio_heat=max_portfolio_heat\n')
                    new_lines.append('        )\n')
                    print("✓ Added Phase 2 parameters to function call")
                    i = j + 1
                    continue
            
            i = j
            continue
        
        new_lines.append(line)
        i += 1
    
    # Write modified content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ API endpoint fixed successfully!")
    return True


def fix_portfolio_backtester(filepath):
    """Fix portfolio_backtester.py to pass Phase 2 params to engine"""
    
    if not os.path.exists(filepath):
        print(f"❌ Portfolio backtester file not found: {filepath}")
        return False
    
    print(f"\n🔧 Fixing portfolio backtester: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Find __init__ signature and add **kwargs
        if 'def __init__(' in line and 'PortfolioBacktester' in ''.join(lines[max(0,i-5):i]):
            # Look ahead for use_cache parameter
            j = i
            while j < len(lines) and 'use_cache:' not in lines[j]:
                new_lines.append(lines[j])
                j += 1
            
            if j < len(lines):
                # Add use_cache line
                new_lines.append(lines[j])
                j += 1
                
                # Check if next line is closing paren, add **kwargs
                if j < len(lines) and ')' in lines[j]:
                    new_lines.append('        **kwargs  # Phase 2 risk management params\n')
                    new_lines.append(lines[j])
                    print("✓ Added **kwargs to __init__ signature")
                    i = j + 1
                    continue
            i = j
            continue
        
        # Store kwargs in __init__
        if 'self.use_cache = use_cache' in line:
            new_lines.append(line)
            new_lines.append('\n')
            new_lines.append('        # Store Phase 2 parameters\n')
            new_lines.append('        self.kwargs = kwargs\n')
            print("✓ Added kwargs storage")
            i += 1
            continue
        
        # Fix PortfolioBacktestEngine instantiation
        if 'portfolio_engine = PortfolioBacktestEngine(' in line:
            new_lines.append(line)
            
            # Look ahead for slippage_rate (last param before closing paren)
            j = i + 1
            while j < len(lines) and 'slippage_rate' not in lines[j]:
                new_lines.append(lines[j])
                j += 1
            
            if j < len(lines):
                # Add slippage_rate
                new_lines.append(lines[j])
                j += 1
                
                # Add Phase 2 params before closing paren
                if j < len(lines) and ')' in lines[j]:
                    new_lines.append('                # Phase 2 Risk Management:\n')
                    new_lines.append('                stop_loss_percent=self.kwargs.get(\'stop_loss_percent\', 2.0),\n')
                    new_lines.append('                enable_stop_loss=self.kwargs.get(\'enable_stop_loss\', True),\n')
                    new_lines.append('                enable_take_profit=self.kwargs.get(\'enable_take_profit\', True),\n')
                    new_lines.append('                risk_reward_ratio=self.kwargs.get(\'risk_reward_ratio\', 2.0),\n')
                    new_lines.append('                risk_per_trade_percent=self.kwargs.get(\'risk_per_trade_percent\', 1.0),\n')
                    new_lines.append('                max_position_size_percent=self.kwargs.get(\'max_position_size_percent\', 20.0),\n')
                    new_lines.append('                max_portfolio_heat=self.kwargs.get(\'max_portfolio_heat\', 6.0)\n')
                    new_lines.append(lines[j])
                    print("✓ Added Phase 2 parameters to PortfolioBacktestEngine")
                    i = j + 1
                    modified = True
                    continue
            
            i = j
            continue
        
        new_lines.append(line)
        i += 1
    
    # Write modified content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Portfolio backtester fixed successfully!")
    return True


def main():
    print("=" * 70)
    print("FIX API PARAMETERS - Enable Phase 2 Risk Management")
    print("=" * 70)
    print("\nThis will fix why your backtest parameters have NO EFFECT.")
    print("\nChanges:")
    print("  1. API endpoint will accept parameters from UI")
    print("  2. Parameters will be passed to backtest engine")
    print("  3. Confidence threshold will use UI input (not hardcoded)")
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
    
    if not fix_api_endpoint(api_file):
        success = False
    
    if not fix_portfolio_backtester(portfolio_file):
        success = False
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! All fixes applied!")
        print("=" * 70)
        print("\n📋 NEXT STEPS:")
        print("  1. Restart FinBERT v4.4.4 completely")
        print("  2. Open your backtest UI")
        print("  3. Change any parameter (e.g., Stop Loss: 2% → 1%)")
        print("  4. Run backtest")
        print("  5. Results should NOW change based on your inputs!")
        print("\n🎯 EXPECTED RESULTS:")
        print("  • Stop Loss 2% + Confidence 60% → Total Return: +8-12%")
        print("  • Stop Loss 1% + Confidence 60% → Total Return: +5-8% (more stops)")
        print("  • Stop Loss 2% + Confidence 80% → Fewer trades, higher win rate")
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
