#!/usr/bin/env python3
"""
FinBERT v4.4.4 - System File Diagnostic Tool
============================================

Checks if files are latest version and in correct locations.

This tool runs on your local system to verify:
- All required files exist
- Files are in correct locations  
- Files have correct sizes (latest versions)
- Configuration is correct

Usage:
    cd C:\\Users\\david\\AATelS
    python CHECK_SYSTEM.py
"""

import os
import sys
from pathlib import Path

# Color codes for terminal (works on Windows 10+)
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_ok(text):
    """Print OK status"""
    print(f"  {GREEN}[OK]{RESET} {text}")

def print_warn(text):
    """Print warning"""
    print(f"  {YELLOW}[WARN]{RESET} {text}")

def print_error(text):
    """Print error"""
    print(f"  {RED}[ERROR]{RESET} {text}")

def print_issue(text):
    """Print issue"""
    print(f"  {RED}[ISSUE]{RESET} {text}")

def print_info(text):
    """Print info"""
    print(f"  {BLUE}[INFO]{RESET} {text}")

def check_file(path, min_size=None, required=True):
    """
    Check if a file exists and optionally verify size
    
    Returns: (exists, size, status)
    """
    if not os.path.exists(path):
        if required:
            print_error(f"{path} - NOT FOUND")
            return False, 0, 'missing'
        else:
            print_warn(f"{path} - NOT FOUND")
            return False, 0, 'missing_optional'
    
    size = os.path.getsize(path)
    
    if min_size and size < min_size:
        print_warn(f"{path} ({size:,} bytes) - Too small, might be outdated")
        return True, size, 'too_small'
    
    print_ok(f"{path} ({size:,} bytes)")
    return True, size, 'ok'

def check_string_in_file(filepath, search_string, label):
    """Check if a string exists in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_string in content:
                print_ok(f"{label} found")
                return True
            else:
                print_error(f"{label} NOT FOUND")
                return False
    except Exception as e:
        print_error(f"Cannot read {filepath}: {e}")
        return False

def check_config_value(filepath, search_string, expected_value, label):
    """Check if a configuration has the expected value"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if search_string + expected_value in content:
                print_ok(f"{label} = {expected_value}")
                return True, 'correct'
            elif search_string in content:
                # Found the parameter but wrong value
                # Try to extract the actual value
                lines = content.split('\n')
                for line in lines:
                    if search_string in line and 'def __init__' not in line:
                        print_issue(f"{label} - Wrong value (should be {expected_value})")
                        print(f"         Found: {line.strip()}")
                        return False, 'wrong_value'
                
                print_warn(f"{label} - Found but value unclear")
                return False, 'unclear'
            else:
                print_error(f"{label} - Parameter not found")
                return False, 'missing'
    except Exception as e:
        print_error(f"Cannot read {filepath}: {e}")
        return False, 'error'

def main():
    print_header("FINBERT v4.4.4 - SYSTEM FILE DIAGNOSTIC")
    
    print("\nThis tool checks:")
    print("  1. All required files exist")
    print("  2. Files are in correct locations")
    print("  3. Files have correct sizes (latest versions)")
    print("  4. Configuration is correct")
    print("\nPress Enter to continue...")
    input()
    
    error_count = 0
    warning_count = 0
    
    # Check working directory
    print_header("CHECK 1/6: Directory Structure")
    
    base_path = Path('finbert_v4.4.4/models/backtesting')
    
    if not base_path.exists():
        print_error(f"Directory not found: {base_path}")
        print("\nERROR: Wrong Directory!")
        print(f"\nCurrent directory: {os.getcwd()}")
        print("Expected: C:\\Users\\david\\AATelS")
        print("\nPlease:")
        print("  1. Open Command Prompt or Terminal")
        print("  2. Run: cd C:\\Users\\david\\AATelS")
        print("  3. Run: python CHECK_SYSTEM.py")
        return 1
    
    print_ok(f"Directory exists: {base_path}")
    
    # Check required files
    print_header("CHECK 2/6: Required Files")
    
    files_to_check = [
        ('finbert_v4.4.4/models/backtesting/backtest_engine.py', 40000, True),
        ('finbert_v4.4.4/models/backtesting/portfolio_backtester.py', 25000, True),
        ('finbert_v4.4.4/models/backtesting/improved_backtest_config.py', 8000, False),
        ('finbert_v4.4.4/models/backtesting/phase1_phase2_example.py', 5000, False),
    ]
    
    for filepath, min_size, required in files_to_check:
        exists, size, status = check_file(filepath, min_size, required)
        if status == 'missing' and required:
            error_count += 1
        elif status in ['missing_optional', 'too_small']:
            warning_count += 1
    
    # Check Phase 2 features in code
    print_header("CHECK 3/6: Phase 2 Features in Code")
    
    engine_path = 'finbert_v4.4.4/models/backtesting/backtest_engine.py'
    
    if os.path.exists(engine_path):
        features = [
            ('enable_take_profit', 'enable_take_profit parameter'),
            ('risk_reward_ratio', 'risk_reward_ratio parameter'),
            ('_check_take_profits', '_check_take_profits method'),
            ('_check_stop_losses', '_check_stop_losses method'),
        ]
        
        for search_str, label in features:
            if not check_string_in_file(engine_path, search_str, label):
                error_count += 1
    else:
        print_error("Cannot check features - backtest_engine.py not found")
        error_count += 1
    
    # Check configuration defaults
    print_header("CHECK 4/6: Configuration Defaults")
    
    if os.path.exists(engine_path):
        configs = [
            ("allocation_strategy: str = ", "'risk_based'", "allocation_strategy"),
            ("enable_take_profit: bool = ", "True", "enable_take_profit"),
            ("stop_loss_percent: float = ", "2.0", "stop_loss_percent"),
        ]
        
        for search_str, expected, label in configs:
            correct, status = check_config_value(engine_path, search_str, expected, label)
            if not correct and status == 'wrong_value':
                error_count += 1
            elif not correct:
                warning_count += 1
    
    # Check diagnostic tools
    print_header("CHECK 5/6: Diagnostic Tools Available")
    
    tools = [
        'FIX_BACKTEST_ENGINE_DEFAULTS.py',
        'DIAGNOSTIC_BACKTEST_ISSUE.py',
        'VERIFY_PHASE2_INSTALLATION.py',
        'CHECK_SYSTEM.py',
        'CHECK_SYSTEM.bat',
    ]
    
    for tool in tools:
        if os.path.exists(tool):
            print_ok(tool)
        else:
            print_warn(f"{tool} - NOT FOUND (download from GitHub)")
            warning_count += 1
    
    # Check patch folders
    print_header("CHECK 6/6: Patch Folders")
    
    patches = [
        ('PHASE1_PHASE2_PATCH', 'Phase 1 & 2 patch'),
        ('IMPROVED_CONFIG_PATCH', 'Improved config patch'),
    ]
    
    for folder, description in patches:
        if os.path.exists(folder):
            print_ok(f"{folder} folder exists")
        else:
            print_info(f"{folder} folder not found (already installed?)")
    
    # Results summary
    print_header("DIAGNOSTIC RESULTS")
    
    if error_count == 0 and warning_count == 0:
        print(f"\n  {GREEN}STATUS: [OK] No issues found{RESET}")
        print("\n  Your system appears to be configured correctly.")
        print("\n  If backtest still shows poor results:")
        print("    1. Make sure FinBERT was restarted after patches")
        print("    2. Set Confidence Threshold to 60% (not 65%)")
        print("    3. Run a fresh backtest")
    elif error_count == 0:
        print(f"\n  {YELLOW}STATUS: [WARNINGS] {warning_count} warning(s) detected{RESET}")
        print("\n  Your system should work, but some optional files are missing.")
    else:
        print(f"\n  {RED}STATUS: [ISSUES FOUND] {error_count} issue(s) and {warning_count} warning(s){RESET}")
        print("\n  Common issues and fixes:")
        
        # Check for specific issues
        if os.path.exists(engine_path):
            with open(engine_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if "allocation_strategy: str = 'equal'" in content:
                    print(f"\n  {RED}ISSUE 1:{RESET} allocation_strategy = 'equal'")
                    print(f"  {GREEN}FIX:{RESET}     python FIX_BACKTEST_ENGINE_DEFAULTS.py")
                
                if 'enable_take_profit' not in content:
                    print(f"\n  {RED}ISSUE 2:{RESET} Phase 2 code missing")
                    print(f"  {GREEN}FIX:{RESET}     Re-install PHASE1_PHASE2_PATCH.zip")
                    print("           1. Download from GitHub")
                    print("           2. Extract and run INSTALL.bat")
    
    # Expected values
    print("\n" + "="*70)
    print("\nEXPECTED FILE SIZES (Latest Versions):")
    print("  backtest_engine.py:              ~42,000 bytes")
    print("  portfolio_backtester.py:         ~30,000 bytes")
    print("  improved_backtest_config.py:     ~11,000 bytes")
    print("  phase1_phase2_example.py:        ~8,000 bytes")
    
    print("\nEXPECTED CONFIGURATION:")
    print("  allocation_strategy:    'risk_based'")
    print("  enable_take_profit:     True")
    print("  stop_loss_percent:      2.0")
    print("  risk_reward_ratio:      2.0")
    print("  risk_per_trade_percent: 1.0")
    print("  max_portfolio_heat:     6.0")
    
    print("\nQUICK FIXES:")
    print("  1. Fix defaults:        python FIX_BACKTEST_ENGINE_DEFAULTS.py")
    print("  2. Verify Phase 2:      python VERIFY_PHASE2_INSTALLATION.py")
    print("  3. Full diagnostic:     python DIAGNOSTIC_BACKTEST_ISSUE.py")
    
    print("\n" + "="*70)
    
    if error_count > 0:
        print(f"\n{RED}RECOMMENDATION:{RESET} Run the fix script to resolve issues")
        print("\nCommand: python FIX_BACKTEST_ENGINE_DEFAULTS.py")
    
    print()
    
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}ERROR:{RESET} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
