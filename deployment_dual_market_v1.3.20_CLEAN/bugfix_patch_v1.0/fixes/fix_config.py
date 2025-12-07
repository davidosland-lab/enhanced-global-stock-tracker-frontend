#!/usr/bin/env python3
"""
Bug Fix Patch v1.0 - Config Fixer
Updates config_dev.py to disable broken LSTM temporarily

This does NOT add fake data - it simply disables the broken feature
until it can be properly retrained.
"""

import os
import sys
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create timestamped backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"✓ Backup created: {backup_path}")
    return backup_path

def find_config_file(base_path):
    """Find the config file"""
    config_file = os.path.join(base_path, 'finbert_v4.4.4', 'config_dev.py')
    if os.path.exists(config_file):
        return config_file
    return None

def update_config(content):
    """Update config to disable broken LSTM"""
    
    # Check if FEATURES dict exists
    if 'FEATURES' in content and 'USE_LSTM' in content:
        # Update existing USE_LSTM
        import re
        pattern = r"['\"]USE_LSTM['\"]:\s*(True|False)"
        replacement = "'USE_LSTM': False  # Disabled by Bug Fix Patch v1.0 - retrain needed"
        content = re.sub(pattern, replacement, content)
        print("  ✓ Updated USE_LSTM to False")
    else:
        # Add FEATURES config
        addition = """

# ========================================
# BUG FIX PATCH v1.0
# Temporarily disable broken features
# ========================================
FEATURES = {
    'USE_LSTM': False,  # Disabled - model expects 8 features, code provides 5
    # To fix: Retrain LSTM model with current feature set
    # Command: python models/lstm_predictor.py --retrain
}
"""
        content += addition
        print("  ✓ Added FEATURES config with USE_LSTM disabled")
    
    return content

def main():
    print("=" * 60)
    print("Bug Fix Patch v1.0 - Config Fixer")
    print("=" * 60)
    print()
    
    # Get base path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = input("Enter FinBERT installation path: ").strip()
    
    # Find config file
    config_file = find_config_file(base_path)
    if not config_file:
        print(f"✗ ERROR: Could not find config_dev.py in {base_path}")
        print("  This is optional - app will work without this fix")
        return 0
    
    print(f"✓ Found config file: {config_file}")
    
    # Read content
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup
    backup_path = backup_file(config_file)
    print()
    
    # Update config
    print("Updating config...")
    content = update_config(content)
    
    # Write back
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("✓ Config updated successfully")
    print()
    print("Changes:")
    print("  - USE_LSTM set to False (prevents feature mismatch error)")
    print("  - App will use real technical analysis without LSTM")
    print("  - Swing trading backtest still works (has its own LSTM)")
    print()
    print(f"Backup saved at: {backup_path}")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
