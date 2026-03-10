#!/usr/bin/env python3
"""
FIX_THRESHOLD_AND_CACHE.py
Complete fix for v188 confidence threshold issue

This script:
1. Deletes ALL Python bytecode cache files (__pycache__ and .pyc)
2. Creates missing live_trading_config.json with 48% threshold
3. Verifies all v188 patches are correctly applied
4. Lists all changes made

Author: GenSpark AI Developer
Version: 1.3.15.189
Date: 2026-02-26
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import List, Tuple

def print_banner(message: str):
    """Print formatted banner"""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80 + "\n")

def delete_python_cache(base_path: Path) -> List[Path]:
    """
    Delete all Python bytecode cache files and directories
    
    Returns:
        List of deleted paths
    """
    deleted = []
    
    # Find and delete __pycache__ directories
    for pycache_dir in base_path.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache_dir)
            deleted.append(pycache_dir)
            print(f"[OK] Deleted {pycache_dir.relative_to(base_path)}")
        except Exception as e:
            print(f"[X] Failed to delete {pycache_dir}: {e}")
    
    # Find and delete .pyc files
    for pyc_file in base_path.rglob('*.pyc'):
        try:
            pyc_file.unlink()
            deleted.append(pyc_file)
            print(f"[OK] Deleted {pyc_file.relative_to(base_path)}")
        except Exception as e:
            print(f"[X] Failed to delete {pyc_file}: {e}")
    
    return deleted

def create_live_trading_config(config_path: Path) -> bool:
    """
    Create live_trading_config.json with v188 settings (48% threshold)
    
    Returns:
        True if successful, False otherwise
    """
    config = {
        "swing_trading": {
            "holding_period_days": 15,
            "stop_loss_percent": 5.0,
            "confidence_threshold": 48.0,
            "max_position_size": 0.25,
            "use_trailing_stop": True,
            "use_profit_targets": True,
            "disable_time_exit_for_winners": True,
            "min_profit_to_hold": 5.0,
            "use_ml_exits": True,
            "ml_exit_confidence_threshold": 0.60,
            "ml_exit_weight": 0.70,
            "use_multi_timeframe": True,
            "use_volatility_sizing": True
        },
        "risk_management": {
            "max_total_positions": 3,
            "max_portfolio_heat": 0.06,
            "max_single_trade_risk": 0.02
        },
        "cross_timeframe": {
            "use_intraday_for_entries": True,
            "use_intraday_for_exits": True,
            "sentiment_boost_threshold": 70,
            "sentiment_block_threshold": 30,
            "early_exit_threshold": 80
        },
        "intraday_monitoring": {
            "scan_interval_minutes": 15,
            "breakout_threshold": 70.0
        }
    }
    
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"[OK] Created {config_path}")
        return True
    except Exception as e:
        print(f"[X] Failed to create config: {e}")
        return False

def verify_patches(base_path: Path) -> List[Tuple[str, str, bool]]:
    """
    Verify all v188 patches are correctly applied
    
    Returns:
        List of (file, expected_value, is_correct) tuples
    """
    results = []
    
    # Check config.json
    config_json = base_path / 'config' / 'config.json'
    if config_json.exists():
        try:
            with open(config_json) as f:
                data = json.load(f)
                threshold = data.get('opportunity_monitoring', {}).get('confidence_threshold')
                is_correct = (threshold == 45.0)
                results.append((str(config_json.relative_to(base_path)), f"45.0 (found: {threshold})", is_correct))
        except Exception as e:
            results.append((str(config_json.relative_to(base_path)), f"ERROR: {e}", False))
    
    # Check swing_signal_generator.py
    swing_gen = base_path / 'ml_pipeline' / 'swing_signal_generator.py'
    if swing_gen.exists():
        try:
            content = swing_gen.read_text()
            # Look for the default parameter line
            has_048 = 'confidence_threshold: float = 0.48' in content
            results.append((str(swing_gen.relative_to(base_path)), "0.48", has_048))
        except Exception as e:
            results.append((str(swing_gen.relative_to(base_path)), f"ERROR: {e}", False))
    
    # Check opportunity_monitor.py
    opp_mon = base_path / 'core' / 'opportunity_monitor.py'
    if opp_mon.exists():
        try:
            content = opp_mon.read_text()
            has_48 = 'confidence_threshold: float = 48.0' in content
            results.append((str(opp_mon.relative_to(base_path)), "48.0", has_48))
        except Exception as e:
            results.append((str(opp_mon.relative_to(base_path)), f"ERROR: {e}", False))
    
    # Check paper_trading_coordinator.py
    paper_coord = base_path / 'core' / 'paper_trading_coordinator.py'
    if paper_coord.exists():
        try:
            content = paper_coord.read_text()
            # Check for the UI min_confidence default
            has_48 = 'min_confidence = self.ui_min_confidence if self.ui_min_confidence is not None else 48.0' in content
            results.append((str(paper_coord.relative_to(base_path)), "48.0 default", has_48))
        except Exception as e:
            results.append((str(paper_coord.relative_to(base_path)), f"ERROR: {e}", False))
    
    return results

def main():
    """Main execution"""
    print_banner("v188 Cache & Configuration Fix")
    
    # Get base path
    base_path = Path(__file__).parent
    print(f"Working directory: {base_path}\n")
    
    # Step 1: Delete Python cache
    print_banner("Step 1: Deleting Python bytecode cache")
    deleted_paths = delete_python_cache(base_path)
    print(f"\n[OK] Deleted {len(deleted_paths)} cache files/directories\n")
    
    # Step 2: Create live_trading_config.json
    print_banner("Step 2: Creating live_trading_config.json")
    config_path = base_path / 'config' / 'live_trading_config.json'
    
    if config_path.exists():
        print(f"[!] File already exists: {config_path}")
        print("  Creating backup...")
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)
        print(f"[OK] Backup created: {backup_path}")
    
    success = create_live_trading_config(config_path)
    
    if success:
        print(f"\n[OK] Configuration file created with 48% threshold\n")
    else:
        print(f"\n[X] Failed to create configuration file\n")
        return 1
    
    # Step 3: Verify patches
    print_banner("Step 3: Verifying v188 patches")
    patch_results = verify_patches(base_path)
    
    all_correct = True
    for file_path, expected, is_correct in patch_results:
        status = "[OK]" if is_correct else "[X]"
        print(f"{status} {file_path}: {expected}")
        if not is_correct:
            all_correct = False
    
    # Summary
    print_banner("Summary")
    print(f"Cache cleanup: {len(deleted_paths)} files/directories deleted")
    print(f"Configuration: {'Created' if success else 'Failed'} live_trading_config.json")
    print(f"Patch verification: {'All patches correct' if all_correct else 'Some patches incorrect'}")
    
    if all_correct and success and deleted_paths:
        print("\n[OK] Fix completed successfully!")
        print("\nNext steps:")
        print("1. Stop the dashboard (Ctrl+C)")
        print("2. Restart: python core/unified_trading_dashboard.py")
        print("3. Verify trades now pass at 48%+ confidence")
        print("\nExpected results:")
        print("  - BP.L: 52.1% >= 48% -> PASS (was blocked at 65%)")
        print("  - HSBA.L: 53.0% >= 48% -> PASS (was blocked at 65%)")
        print("  - RIO.AX: 54.4% >= 48% -> PASS (was blocked at 52%)")
        return 0
    else:
        print("\n[!] Fix completed with warnings - please review above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
