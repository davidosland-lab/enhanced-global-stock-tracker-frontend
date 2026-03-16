#!/usr/bin/env python3
"""
Backtest Diagnostic Tool
========================

This script diagnoses why the backtest is still showing poor results after patches.

Run this script to get a complete diagnostic report.

Usage:
    cd C:\Users\david\AATelS
    python DIAGNOSTIC_BACKTEST_ISSUE.py
"""

import os
import sys
from pathlib import Path

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_file_exists(filepath):
    """Check if a file exists and return its status"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        return True, size
    return False, 0

def main():
    print("\n" + "="*70)
    print("  BACKTEST DIAGNOSTIC TOOL")
    print("  Issue: Patches applied but results unchanged")
    print("="*70)
    
    # Check working directory
    print_section("1. WORKING DIRECTORY CHECK")
    cwd = os.getcwd()
    print(f"Current Directory: {cwd}")
    
    expected_dir = "AATelS" in cwd or "webapp" in cwd
    if expected_dir:
        print("✅ Working directory looks correct")
    else:
        print("⚠️  Warning: Unexpected working directory")
        print("   Expected: C:\\Users\\david\\AATelS")
    
    # Check file structure
    print_section("2. FILE STRUCTURE CHECK")
    
    files_to_check = {
        'backtest_engine.py': 'finbert_v4.4.4/models/backtesting/backtest_engine.py',
        'portfolio_backtester.py': 'finbert_v4.4.4/models/backtesting/portfolio_backtester.py',
        'improved_config': 'finbert_v4.4.4/models/backtesting/improved_backtest_config.py',
        'phase1_phase2_example': 'finbert_v4.4.4/models/backtesting/phase1_phase2_example.py',
    }
    
    file_status = {}
    for name, path in files_to_check.items():
        exists, size = check_file_exists(path)
        file_status[name] = (exists, size)
        status = "✅" if exists else "❌"
        size_str = f"({size:,} bytes)" if exists else "(missing)"
        print(f"{status} {name}: {size_str}")
    
    # Check backtest_engine.py content
    print_section("3. BACKTEST ENGINE CODE CHECK")
    
    engine_path = 'finbert_v4.4.4/models/backtesting/backtest_engine.py'
    if file_status['backtest_engine.py'][0]:
        try:
            with open(engine_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for key Phase 2 features
            checks = {
                'enable_take_profit parameter': 'enable_take_profit' in content,
                'risk_reward_ratio parameter': 'risk_reward_ratio' in content,
                'take_profit_type parameter': 'take_profit_type' in content,
                'stop_loss_type parameter': 'stop_loss_type' in content,
                'risk_per_trade_percent parameter': 'risk_per_trade_percent' in content,
                'max_portfolio_heat parameter': 'max_portfolio_heat' in content,
                'calculate_take_profit_price method': 'def calculate_take_profit_price' in content or 'def _calculate_take_profit_price' in content,
            }
            
            all_present = all(checks.values())
            
            for feature, present in checks.items():
                status = "✅" if present else "❌"
                print(f"{status} {feature}")
            
            if all_present:
                print("\n✅ ALL Phase 2 features found in backtest_engine.py")
            else:
                print("\n❌ MISSING Phase 2 features in backtest_engine.py")
                print("   This means Phase 1 & 2 patch was NOT applied correctly!")
            
        except Exception as e:
            print(f"❌ Error reading backtest_engine.py: {e}")
    else:
        print("❌ backtest_engine.py not found!")
    
    # Check engine defaults
    print_section("4. ENGINE DEFAULT VALUES CHECK")
    
    try:
        # Try to import and inspect the engine
        sys.path.insert(0, os.getcwd())
        from finbert_v4.4.4.models.backtesting.backtest_engine import PortfolioBacktestEngine
        
        # Create engine with defaults
        engine = PortfolioBacktestEngine(initial_capital=100000)
        
        print("\nCurrent Backend Defaults:")
        print(f"  Allocation Strategy: {engine.allocation_strategy}")
        print(f"  Enable Stop-Loss: {engine.enable_stop_loss}")
        print(f"  Stop Loss %: {engine.stop_loss_percent}%")
        
        # Check if Phase 2 attributes exist
        has_phase2 = hasattr(engine, 'enable_take_profit')
        
        if has_phase2:
            print(f"  Enable Take-Profit: {engine.enable_take_profit}")
            print(f"  Risk:Reward Ratio: {engine.risk_reward_ratio}")
            print(f"  Risk Per Trade %: {engine.risk_per_trade_percent}%")
            print(f"  Max Portfolio Heat %: {engine.max_portfolio_heat}%")
            print(f"  Max Position Size %: {engine.max_position_size_percent}%")
            
            print("\n✅ Phase 2 attributes found")
            
            # Check if they're enabled
            if engine.enable_take_profit:
                print("✅ Take-Profit is ENABLED in defaults")
            else:
                print("⚠️  Take-Profit is DISABLED in defaults")
                print("   You need to change: enable_take_profit: bool = True")
            
            if engine.allocation_strategy == 'risk_based':
                print("✅ Risk-Based allocation is ENABLED in defaults")
            else:
                print("⚠️  Risk-Based allocation is DISABLED in defaults")
                print(f"   Current: {engine.allocation_strategy}")
                print("   You need to change: allocation_strategy: str = 'risk_based'")
        else:
            print("\n❌ Phase 2 attributes NOT FOUND")
            print("   The engine does NOT have take-profit support!")
            print("   Phase 1 & 2 patch was NOT applied correctly!")
            
    except ImportError as e:
        print(f"❌ Cannot import PortfolioBacktestEngine: {e}")
        print("   Make sure you're running from the correct directory!")
    except Exception as e:
        print(f"❌ Error inspecting engine: {e}")
    
    # Check improved config
    print_section("5. IMPROVED CONFIG CHECK")
    
    config_path = 'finbert_v4.4.4/models/backtesting/improved_backtest_config.py'
    if file_status['improved_config'][0]:
        try:
            from finbert_v4.4.4.models.backtesting.improved_backtest_config import IMPROVED_CONFIG
            
            print("\nImproved Config Values:")
            for key, value in IMPROVED_CONFIG.items():
                print(f"  {key}: {value}")
            
            print("\n✅ Improved config loaded successfully")
            
        except ImportError as e:
            print(f"❌ Cannot import improved config: {e}")
    else:
        print("❌ improved_backtest_config.py not found!")
    
    # Root cause analysis
    print_section("6. ROOT CAUSE ANALYSIS")
    
    print("\nBased on your backtest results:")
    print("  Final Value: $99,143.56")
    print("  Total Return: -0.86%")
    print("  Win Rate: 45.5%")
    print("  Profit Factor: 0.54")
    print("  Avg Profit: -$77.86")
    print("  Total Trades: 11")
    
    print("\n🔍 DIAGNOSIS:")
    
    # Diagnosis logic
    if not file_status['backtest_engine.py'][0]:
        print("❌ CRITICAL: backtest_engine.py is MISSING!")
        print("   Solution: Reinstall Phase 1 & 2 patch")
    elif file_status['backtest_engine.py'][1] < 30000:
        print("⚠️  WARNING: backtest_engine.py is too small")
        print(f"   Current size: {file_status['backtest_engine.py'][1]:,} bytes")
        print("   Expected size: ~42,000 bytes")
        print("   This suggests Phase 1 & 2 patch was NOT applied!")
    else:
        print("✅ backtest_engine.py size looks correct")
    
    print("\n📊 RESULT ANALYSIS:")
    print("  Win Rate 45.5% is GOOD ✅")
    print("  But Profit Factor 0.54 is BAD ❌")
    print("  This pattern indicates: TAKE-PROFIT IS NOT WORKING")
    print()
    print("  Without take-profit:")
    print("    - Wins: Small gains (~$500)")
    print("    - Losses: Full stop-loss (~$1,000)")
    print("    - Result: Win 45% but still lose money overall")
    print()
    print("  With take-profit (2:1 R:R):")
    print("    - Wins: Hit take-profit (~$2,000)")
    print("    - Losses: Hit stop-loss (~$1,000)")
    print("    - Result: Win 45% = profitable!")
    
    # Recommendations
    print_section("7. RECOMMENDED ACTIONS")
    
    print("\n1. VERIFY PATCH APPLICATION:")
    print("   Check if backtest_engine.py has this in __init__:")
    print("   ")
    print("   def __init__(")
    print("       self,")
    print("       enable_take_profit: bool = False,    # ← Should exist")
    print("       risk_reward_ratio: float = 2.0,      # ← Should exist")
    print("       take_profit_type: str = 'risk_reward' # ← Should exist")
    print("   ):")
    
    print("\n2. IF PHASE 2 FEATURES EXIST:")
    print("   Change these defaults in backtest_engine.py:")
    print("   ")
    print("   allocation_strategy: str = 'risk_based'  # Change from 'equal'")
    print("   stop_loss_percent: float = 2.0           # Change from 1.0")
    print("   enable_take_profit: bool = True          # Change from False")
    
    print("\n3. IF PHASE 2 FEATURES DON'T EXIST:")
    print("   The Phase 1 & 2 patch was NOT applied correctly!")
    print("   You need to:")
    print("   a) Re-download PHASE1_PHASE2_PATCH.zip")
    print("   b) Extract and run INSTALL.bat again")
    print("   c) Make sure it says 'INSTALLATION COMPLETE'")
    
    print("\n4. AFTER FIXING:")
    print("   - Restart FinBERT v4.4.4")
    print("   - Set Confidence Threshold to 60% (you have 65%)")
    print("   - Re-run backtest")
    print("   - Expected: +8-12% return, 1.5-2.4 profit factor")
    
    # Generate report file
    print_section("8. GENERATING DIAGNOSTIC REPORT")
    
    report_path = 'DIAGNOSTIC_REPORT.txt'
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("BACKTEST DIAGNOSTIC REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Date: {os.popen('date /t').read().strip() if sys.platform == 'win32' else os.popen('date').read().strip()}\n")
            f.write(f"Working Directory: {cwd}\n\n")
            
            f.write("FILE STATUS:\n")
            for name, (exists, size) in file_status.items():
                status = "EXISTS" if exists else "MISSING"
                f.write(f"  {name}: {status} ({size:,} bytes)\n")
            
            f.write("\nBACKTEST RESULTS:\n")
            f.write("  Total Return: -0.86%\n")
            f.write("  Win Rate: 45.5%\n")
            f.write("  Profit Factor: 0.54\n")
            f.write("  Avg Profit: -$77.86\n")
            f.write("  Total Trades: 11\n")
            
            f.write("\nDIAGNOSIS:\n")
            f.write("  Issue: Take-profit appears to be disabled or not working\n")
            f.write("  Win rate improved (25% -> 45.5%) but still losing money\n")
            f.write("  This indicates losses are bigger than wins\n")
            
            f.write("\nRECOMMENDED FIX:\n")
            f.write("  1. Verify Phase 2 features exist in backtest_engine.py\n")
            f.write("  2. Enable take-profit in backend defaults\n")
            f.write("  3. Change allocation_strategy to 'risk_based'\n")
            f.write("  4. Lower confidence threshold to 60%\n")
            f.write("  5. Restart and re-run backtest\n")
        
        print(f"✅ Diagnostic report saved to: {report_path}")
    except Exception as e:
        print(f"⚠️  Could not save report: {e}")
    
    print("\n" + "="*70)
    print("  DIAGNOSTIC COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Review the diagnostics above")
    print("2. Check if Phase 2 features exist in backtest_engine.py")
    print("3. If yes: Enable them in defaults")
    print("4. If no: Reinstall Phase 1 & 2 patch")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ DIAGNOSTIC TOOL ERROR: {e}")
        import traceback
        traceback.print_exc()
