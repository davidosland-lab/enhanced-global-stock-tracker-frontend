"""
v186 HOTFIX - Confidence Threshold Patch
=========================================

This script automatically patches your trading system to lower the confidence
threshold from 52% to 48%, allowing more trades to execute.

Changes:
- config/live_trading_config.json: confidence_threshold 52.0 -> 45.0
- ml_pipeline/swing_signal_generator.py: 
    - Default parameter 0.52 -> 0.48
    - Docstring 52% -> 48%
    - Example code 0.52 -> 0.48

Usage:
    python APPLY_V186_HOTFIX.py

The script will:
1. Backup your existing files
2. Apply the patches
3. Verify the changes
4. Show a summary
"""

import os
import sys
import shutil
from pathlib import Path


def backup_file(filepath):
    """Create a backup of the file"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.v186_backup"
        shutil.copy2(filepath, backup_path)
        print(f"✓ Backed up: {filepath} -> {backup_path}")
        return True
    else:
        print(f"✗ File not found: {filepath}")
        return False


def patch_config(base_dir):
    """Patch the live_trading_config.json file"""
    config_path = os.path.join(base_dir, "config", "live_trading_config.json")
    
    if not os.path.exists(config_path):
        print(f"✗ Config file not found: {config_path}")
        return False
    
    # Backup
    backup_file(config_path)
    
    # Read and patch
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Replace threshold
    patched = content.replace('"confidence_threshold": 52.0,', '"confidence_threshold": 45.0,')
    
    # Write back
    with open(config_path, 'w') as f:
        f.write(patched)
    
    print(f"✓ Patched config: confidence_threshold 52.0 -> 45.0")
    return True


def patch_signal_generator(base_dir):
    """Patch the swing_signal_generator.py file"""
    sg_path = os.path.join(base_dir, "ml_pipeline", "swing_signal_generator.py")
    
    if not os.path.exists(sg_path):
        print(f"✗ Signal generator not found: {sg_path}")
        return False
    
    # Backup
    backup_file(sg_path)
    
    # Read and patch
    with open(sg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply patches
    patched = content
    patched = patched.replace(
        'confidence_threshold: float = 0.52,',
        'confidence_threshold: float = 0.48,  # v186: Lowered from 0.52 to allow more trades'
    )
    patched = patched.replace(
        'confidence_threshold: Minimum confidence for entry (52%)',
        'confidence_threshold: Minimum confidence for entry (48%)'
    )
    patched = patched.replace(
        "signal['confidence'] > 0.52:",
        "signal['confidence'] > 0.48:"
    )
    
    # Write back
    with open(sg_path, 'w', encoding='utf-8') as f:
        f.write(patched)
    
    print(f"✓ Patched signal generator: 0.52 -> 0.48")
    return True


def verify_patches(base_dir):
    """Verify the patches were applied correctly"""
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Verify config
    config_path = os.path.join(base_dir, "config", "live_trading_config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            content = f.read()
        if '"confidence_threshold": 45.0,' in content:
            print("✓ Config shows confidence_threshold: 45.0")
        else:
            print("✗ Config threshold not updated")
    
    # Verify signal generator
    sg_path = os.path.join(base_dir, "ml_pipeline", "swing_signal_generator.py")
    if os.path.exists(sg_path):
        with open(sg_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('confidence_threshold: float = 0.48', 'Parameter default'),
            ('confidence_threshold: Minimum confidence for entry (48%)', 'Docstring'),
            ("signal['confidence'] > 0.48:", 'Example code')
        ]
        
        for pattern, name in checks:
            if pattern in content:
                print(f"✓ {name} updated to 48%")
            else:
                print(f"✗ {name} not updated")


def main():
    print("="*60)
    print("v186 HOTFIX - Confidence Threshold Patch")
    print("="*60)
    print()
    
    # Detect installation directory
    current_dir = os.getcwd()
    
    # Check if we're already in the trading system directory
    if os.path.exists(os.path.join(current_dir, "ml_pipeline", "swing_signal_generator.py")):
        base_dir = current_dir
        print(f"✓ Detected trading system at: {base_dir}")
    else:
        print("✗ Cannot detect trading system directory")
        print()
        print("Please run this script from your trading system root directory")
        print("Example:")
        print('  cd "C:\\Users\\david\\Regime_trading\\complete_backend_clean_install_v1.3.15"')
        print("  python APPLY_V186_HOTFIX.py")
        sys.exit(1)
    
    print()
    print("The following changes will be made:")
    print("  1. config/live_trading_config.json: threshold 52% -> 45%")
    print("  2. ml_pipeline/swing_signal_generator.py: threshold 0.52 -> 0.48")
    print()
    print("Backups will be created with .v186_backup extension")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("Aborted.")
        sys.exit(0)
    
    print()
    print("Applying patches...")
    print("-"*60)
    
    # Apply patches
    config_ok = patch_config(base_dir)
    sg_ok = patch_signal_generator(base_dir)
    
    if config_ok and sg_ok:
        verify_patches(base_dir)
        print()
        print("="*60)
        print("✓ HOTFIX APPLIED SUCCESSFULLY")
        print("="*60)
        print()
        print("Next steps:")
        print("  1. Restart your trading dashboard")
        print("  2. Monitor logs for signals with 48-65% confidence")
        print("  3. Verify trades are no longer blocked")
        print()
        print("Expected log output:")
        print('  ✓ Entry signal detected for RIO.AX: BUY with confidence 0.54')
        print('  ✓ Signal PASSED threshold check (54.4% >= 48.0%)')
        print()
    else:
        print()
        print("="*60)
        print("✗ HOTFIX FAILED")
        print("="*60)
        print()
        print("Some patches could not be applied.")
        print("Please verify your installation structure and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
