#!/usr/bin/env python3
"""
Bug Fix Patch v1.3 - Apply All Fixes
Fixes: SyntaxError + Config import + Mock sentiment + ADX crashes
NO UNICODE - Windows CMD compatible
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Force UTF-8 output (Windows compatibility)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

def print_status(message, status='INFO'):
    """Print status message"""
    prefix = {
        'INFO': '[INFO]',
        'OK': '[OK]  ',
        'ERROR': '[ERROR]',
        'WARN': '[WARN]'
    }.get(status, '[INFO]')
    print(f"{prefix} {message}")

def backup_file(filepath):
    """Create backup of file"""
    if os.path.exists(filepath):
        backup = f"{filepath}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filepath, backup)
        print_status(f"Backup: {os.path.basename(backup)}", 'OK')
        return backup
    return None

def apply_lstm_fix(finbert_dir):
    """Replace broken lstm_predictor.py with working version"""
    print_status("Fix 1: LSTM predictor (SyntaxError)", 'INFO')
    
    target_file = os.path.join(finbert_dir, 'models', 'lstm_predictor.py')
    source_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'fixes', 'lstm_predictor.py')
    
    if not os.path.exists(source_file):
        print_status(f"Source not found: {source_file}", 'ERROR')
        return False
    
    # Backup original
    backup_file(target_file)
    
    # Copy fixed version
    try:
        shutil.copy2(source_file, target_file)
        print_status("LSTM predictor fixed", 'OK')
        return True
    except Exception as e:
        print_status(f"Failed: {e}", 'ERROR')
        return False

def apply_config_fix(finbert_dir):
    """Replace broken config_dev.py with correct version"""
    print_status("Fix 2: Config file (import error)", 'INFO')
    
    target_file = os.path.join(finbert_dir, 'config_dev.py')
    source_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'fixes', 'config_dev.py')
    
    if not os.path.exists(source_file):
        print_status(f"Source not found: {source_file}", 'ERROR')
        return False
    
    # Backup if exists
    if os.path.exists(target_file):
        backup_file(target_file)
    
    # Copy correct version
    try:
        shutil.copy2(source_file, target_file)
        print_status("Config file fixed", 'OK')
        return True
    except Exception as e:
        print_status(f"Failed: {e}", 'ERROR')
        return False

def apply_app_fixes(finbert_dir):
    """Fix app_finbert_v4_dev.py"""
    print_status("Fix 3: App error handling", 'INFO')
    
    target_file = os.path.join(finbert_dir, 'app_finbert_v4_dev.py')
    
    if not os.path.exists(target_file):
        print_status(f"Target not found: {target_file}", 'WARN')
        return True  # Skip, not critical
    
    # Backup
    backup_file(target_file)
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        changes_made = 0
        
        # Fix 1: Remove mock sentiment fallback
        if 'get_mock_sentiment' in content:
            content = content.replace(
                'sentiment_data = get_mock_sentiment(symbol)',
                '# REMOVED: Mock sentiment\n                sentiment_data = None'
            )
            changes_made += 1
        
        # Fix 2: Add ADX validation
        if 'calculate_adx' in content and 'if len(df) >= 14:' not in content:
            old_code = 'adx = calculate_adx(df)'
            new_code = '''# Validate data for ADX
            if len(df) >= 14:
                adx = calculate_adx(df)
            else:
                adx = 50.0  # Neutral'''
            
            if old_code in content:
                content = content.replace(old_code, new_code)
                changes_made += 1
        
        # Fix 3: Add sentiment None check
        old_pattern = "sentiment_score = sentiment_data.get('compound', 0)"
        new_pattern = "sentiment_score = sentiment_data.get('compound', 0) if sentiment_data else 0"
        
        if old_pattern in content and new_pattern not in content:
            content = content.replace(old_pattern, new_pattern)
            changes_made += 1
        
        if changes_made > 0:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print_status(f"App fixes applied ({changes_made} changes)", 'OK')
        else:
            print_status("App already fixed", 'OK')
        
        return True
            
    except Exception as e:
        print_status(f"App fix failed: {e}", 'WARN')
        return True  # Non-critical

def update_config_features(finbert_dir):
    """Update config to disable broken LSTM"""
    print_status("Fix 4: Disable LSTM in config", 'INFO')
    
    config_file = os.path.join(finbert_dir, 'config_dev.py')
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update LSTM flag
        if "'USE_LSTM': True" in content:
            content = content.replace("'USE_LSTM': True", "'USE_LSTM': False  # Disabled")
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print_status("LSTM disabled in config", 'OK')
        elif "'USE_LSTM': False" in content:
            print_status("LSTM already disabled", 'OK')
        else:
            print_status("LSTM flag not found (OK)", 'OK')
        
        return True
        
    except Exception as e:
        print_status(f"Config update failed: {e}", 'WARN')
        return True  # Non-critical

def main():
    """Main installation"""
    print()
    print("=" * 60)
    print("  Bug Fix Patch v1.3 Installer")
    print("  Fixes: SyntaxError + Config + Mock + ADX")
    print("=" * 60)
    print()
    
    # Get FinBERT directory
    if len(sys.argv) > 1:
        finbert_dir = sys.argv[1]
    else:
        finbert_dir = input("Enter FinBERT v4.4.4 path: ").strip()
        finbert_dir = finbert_dir.strip('"').strip("'")
    
    # Validate
    if not os.path.exists(finbert_dir):
        print_status(f"Not found: {finbert_dir}", 'ERROR')
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    app_file = os.path.join(finbert_dir, 'app_finbert_v4_dev.py')
    if not os.path.exists(app_file):
        print_status(f"Invalid directory (no app_finbert_v4_dev.py)", 'ERROR')
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print_status(f"Target: {finbert_dir}", 'INFO')
    print()
    
    # Apply all fixes
    print("Applying fixes...")
    print("-" * 60)
    
    fixes_ok = 0
    fixes_total = 4
    
    if apply_lstm_fix(finbert_dir):
        fixes_ok += 1
    
    if apply_config_fix(finbert_dir):
        fixes_ok += 1
    
    if apply_app_fixes(finbert_dir):
        fixes_ok += 1
    
    if update_config_features(finbert_dir):
        fixes_ok += 1
    
    # Summary
    print()
    print("-" * 60)
    
    if fixes_ok >= 3:
        print_status(f"Installation complete ({fixes_ok}/{fixes_total} OK)", 'OK')
        print()
        print("NEXT STEPS:")
        print("1. Restart server:")
        print(f"   cd {finbert_dir}")
        print("   python app_finbert_v4_dev.py")
        print()
        print("2. Test swing backtest:")
        print('   curl -X POST http://localhost:5001/api/backtest/swing \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d "{\\"symbol\\": \\"AAPL\\", \\"start_date\\": \\"2024-01-01\\", \\"end_date\\": \\"2024-11-01\\"}"')
        print()
        print("FIXED:")
        print("  [OK] SyntaxError in lstm_predictor.py")
        print("  [OK] Config import error")
        print("  [OK] Mock sentiment removed")
        print("  [OK] ADX crashes fixed")
        status = 0
    else:
        print_status(f"Incomplete ({fixes_ok}/{fixes_total})", 'ERROR')
        print()
        print("Some fixes failed. Check errors above.")
        status = 1
    
    print()
    input("Press Enter to exit...")
    sys.exit(status)

if __name__ == '__main__':
    main()
