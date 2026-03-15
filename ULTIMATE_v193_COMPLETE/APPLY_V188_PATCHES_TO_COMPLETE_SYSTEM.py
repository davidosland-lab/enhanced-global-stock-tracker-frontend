"""
APPLY_V188_PATCHES_TO_COMPLETE_SYSTEM.py

This script applies ONLY the v188 confidence threshold patches to your COMPLETE system.
It does NOT remove any files - it only modifies 4 specific lines in 4 files.

Files to be patched:
1. config/config.json - confidence_threshold: 55.0 -> 45.0
2. ml_pipeline/swing_signal_generator.py - confidence_threshold: float = 0.55 -> 0.48
3. core/paper_trading_coordinator.py - min_confidence fallback: 52.0 -> 48.0
4. core/opportunity_monitor.py - confidence_threshold: float = 65.0 -> 48.0

NO OTHER FILES WILL BE MODIFIED OR REMOVED!
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

def backup_file(file_path):
    """Create a backup of the original file."""
    backup_path = f"{file_path}.v188_backup"
    shutil.copy2(file_path, backup_path)
    print(f"[OK] Backed up: {backup_path}")
    return backup_path

def patch_config_json(base_dir):
    """Patch config/config.json confidence_threshold from 55.0 to 45.0."""
    config_path = os.path.join(base_dir, "config", "config.json")
    
    if not os.path.exists(config_path):
        print(f"[X] File not found: {config_path}")
        return False
    
    # Backup
    backup_file(config_path)
    
    # Read JSON
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Patch
    old_value = config['opportunity_monitoring']['confidence_threshold']
    config['opportunity_monitoring']['confidence_threshold'] = 45.0
    
    # Write
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"[OK] Patched config/config.json: {old_value} -> 45.0")
    return True

def patch_signal_generator(base_dir):
    """Patch ml_pipeline/swing_signal_generator.py confidence_threshold from 0.55 to 0.48."""
    sg_path = os.path.join(base_dir, "ml_pipeline", "swing_signal_generator.py")
    
    if not os.path.exists(sg_path):
        print(f"[X] File not found: {sg_path}")
        return False
    
    # Backup
    backup_file(sg_path)
    
    # Read file
    with open(sg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patch - find the exact line
    old_line = "        confidence_threshold: float = 0.55,  # v185: Lowered from 0.52 to enable trading"
    new_line = "        confidence_threshold: float = 0.48,  # v188: Lowered from 0.55 to enable 48-65% trades"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        # Write
        with open(sg_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Patched ml_pipeline/swing_signal_generator.py: 0.55 -> 0.48")
        return True
    else:
        print(f"[X] Could not find target line in {sg_path}")
        return False

def patch_coordinator(base_dir):
    """Patch core/paper_trading_coordinator.py min_confidence fallback from 52.0 to 48.0."""
    coord_path = os.path.join(base_dir, "core", "paper_trading_coordinator.py")
    
    if not os.path.exists(coord_path):
        print(f"[X] File not found: {coord_path}")
        return False
    
    # Backup
    backup_file(coord_path)
    
    # Read file
    with open(coord_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patch - find the exact line
    old_line = "        min_confidence = self.ui_min_confidence if self.ui_min_confidence is not None else 52.0"
    new_line = "        min_confidence = self.ui_min_confidence if self.ui_min_confidence is not None else 48.0  # v188: Lowered from 52.0"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        # Write
        with open(coord_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Patched core/paper_trading_coordinator.py: 52.0 -> 48.0")
        return True
    else:
        print(f"[X] Could not find target line in {coord_path}")
        return False

def patch_opportunity_monitor(base_dir):
    """Patch core/opportunity_monitor.py confidence_threshold from 65.0 to 48.0."""
    om_path = os.path.join(base_dir, "core", "opportunity_monitor.py")
    
    if not os.path.exists(om_path):
        print(f"[X] File not found: {om_path}")
        return False
    
    # Backup
    backup_file(om_path)
    
    # Read file
    with open(om_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patch - find the exact line
    old_line = "        confidence_threshold: float = 65.0,"
    new_line = "        confidence_threshold: float = 48.0,  # v188: Lowered from 65.0"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        
        # Write
        with open(om_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Patched core/opportunity_monitor.py: 65.0 -> 48.0")
        return True
    else:
        print(f"[X] Could not find target line in {om_path}")
        return False

def main():
    print("=" * 80)
    print("  v188 CONFIDENCE THRESHOLD PATCH - COMPLETE SYSTEM")
    print("=" * 80)
    print()
    print("This script will ONLY modify 4 lines in 4 files:")
    print("  1. config/config.json")
    print("  2. ml_pipeline/swing_signal_generator.py")
    print("  3. core/paper_trading_coordinator.py")
    print("  4. core/opportunity_monitor.py")
    print()
    print("ALL OTHER FILES WILL REMAIN UNTOUCHED!")
    print("Your complete system with finbert_v4.4.4, pipelines, etc. will be preserved.")
    print()
    print("Backups will be created with .v188_backup extension.")
    print("=" * 80)
    print()
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Working directory: {base_dir}")
    print()
    
    # Confirm
    response = input("Proceed with patching? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Aborted.")
        return
    
    print()
    print("Starting patches...")
    print()
    
    # Apply patches
    results = []
    results.append(("Config JSON", patch_config_json(base_dir)))
    results.append(("Signal Generator", patch_signal_generator(base_dir)))
    results.append(("Coordinator", patch_coordinator(base_dir)))
    results.append(("Opportunity Monitor", patch_opportunity_monitor(base_dir)))
    
    # Summary
    print()
    print("=" * 80)
    print("  PATCH SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for _, success in results if success)
    
    for name, success in results:
        status = "[OK] SUCCESS" if success else "[X] FAILED"
        print(f"{name:25s} {status}")
    
    print()
    print(f"Total: {success_count}/4 files patched successfully")
    print("=" * 80)
    print()
    
    if success_count == 4:
        print("[OK] All v188 patches applied successfully!")
        print()
        print("Expected behavior:")
        print("  - BP.L: 52.1% >= 48.0% - PASS [OK] (was BLOCKED at 65%)")
        print("  - HSBA.L: 53.0% >= 48.0% - PASS [OK] (was BLOCKED at 65%)")
        print("  - RIO.AX: 54.4% >= 48.0% - PASS [OK] (was BLOCKED at 52%)")
        print()
        print("Next steps:")
        print("  1. Stop the current dashboard (Ctrl+C)")
        print("  2. Delete __pycache__ folders:")
        print("     - core/__pycache__")
        print("     - ml_pipeline/__pycache__")
        print("  3. Restart dashboard")
        print("  4. Verify trades pass at 48%+")
    else:
        print("[X] Some patches failed. Review errors above.")
        print()
        print("To rollback, restore .v188_backup files:")
        for name, success in results:
            if success:
                print(f"  - Restore corresponding .v188_backup file")
    
    print("=" * 80)

if __name__ == '__main__':
    main()
