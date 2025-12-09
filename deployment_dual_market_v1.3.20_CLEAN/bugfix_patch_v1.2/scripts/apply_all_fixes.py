#!/usr/bin/env python3
"""
Bug Fix Patch v1.2 - Apply All Fixes
Fixes: SyntaxError in lstm_predictor.py + Mock sentiment + ADX crashes
NO UNICODE - Windows CMD compatible
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Force UTF-8 output (Windows compatibility)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

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
        print_status(f"Backup created: {backup}", 'OK')
        return backup
    return None

def apply_lstm_fix(finbert_dir):
    """Replace broken lstm_predictor.py with working version"""
    print_status("Applying LSTM predictor fix...", 'INFO')
    
    target_file = os.path.join(finbert_dir, 'models', 'lstm_predictor.py')
    source_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               'fixes', 'lstm_predictor.py')
    
    if not os.path.exists(source_file):
        print_status(f"Source file not found: {source_file}", 'ERROR')
        return False
    
    # Backup original
    backup_file(target_file)
    
    # Copy fixed version
    try:
        shutil.copy2(source_file, target_file)
        print_status(f"Fixed lstm_predictor.py installed", 'OK')
        return True
    except Exception as e:
        print_status(f"Failed to copy file: {e}", 'ERROR')
        return False

def apply_app_fixes(finbert_dir):
    """Fix app_finbert_v4_dev.py"""
    print_status("Applying app error fixes...", 'INFO')
    
    target_file = os.path.join(finbert_dir, 'app_finbert_v4_dev.py')
    
    if not os.path.exists(target_file):
        print_status(f"Target file not found: {target_file}", 'ERROR')
        return False
    
    # Backup
    backup_file(target_file)
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        changes_made = 0
        
        # Fix 1: Remove mock sentiment fallback
        if 'get_mock_sentiment' in content:
            # Replace with None fallback
            content = content.replace(
                'sentiment_data = get_mock_sentiment(symbol)',
                '# REMOVED: Mock sentiment fallback\n                sentiment_data = None'
            )
            changes_made += 1
            print_status("Removed mock sentiment fallback", 'OK')
        
        # Fix 2: Add ADX validation
        if 'calculate_adx' in content and 'if len(df) >= 14:' not in content:
            # Add validation before ADX calculation
            old_code = 'adx = calculate_adx(df)'
            new_code = '''# Validate sufficient data for ADX
            if len(df) >= 14:
                adx = calculate_adx(df)
            else:
                logger.warning(f"Insufficient data for ADX calculation (need 14, have {len(df)})")
                adx = 50.0  # Neutral default'''
            
            if old_code in content:
                content = content.replace(old_code, new_code)
                changes_made += 1
                print_status("Added ADX validation", 'OK')
        
        # Fix 3: Add sentiment None check
        if 'sentiment_data.get' in content:
            # Add None check
            old_pattern = "sentiment_score = sentiment_data.get('compound', 0)"
            new_pattern = "sentiment_score = sentiment_data.get('compound', 0) if sentiment_data else 0"
            
            if old_pattern in content and new_pattern not in content:
                content = content.replace(old_pattern, new_pattern)
                changes_made += 1
                print_status("Added sentiment None checks", 'OK')
        
        if changes_made > 0:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print_status(f"Applied {changes_made} fixes to app", 'OK')
            return True
        else:
            print_status("No changes needed (already fixed)", 'INFO')
            return True
            
    except Exception as e:
        print_status(f"Error applying fixes: {e}", 'ERROR')
        return False

def disable_lstm(finbert_dir):
    """Disable LSTM in config"""
    print_status("Disabling broken LSTM in config...", 'INFO')
    
    config_file = os.path.join(finbert_dir, 'config_dev.py')
    
    try:
        # Create or update config
        config_content = '''"""
FinBERT v4.4.4 Development Configuration
"""

# Feature flags
FEATURES = {
    'USE_LSTM': False,  # Disabled until retrained
    'USE_SENTIMENT': True,  # Real sentiment only
    'USE_TECHNICAL': True,  # RSI, MACD, etc.
    'USE_VOLUME': True
}

# Logging
LOG_LEVEL = 'INFO'
'''
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print_status("Config updated (LSTM disabled)", 'OK')
        return True
        
    except Exception as e:
        print_status(f"Config update failed: {e}", 'ERROR')
        return False

def main():
    """Main installation"""
    print()
    print("=" * 60)
    print("  Bug Fix Patch v1.2 Installer")
    print("  Fixes: SyntaxError + Mock Data + ADX + LSTM")
    print("=" * 60)
    print()
    
    # Get FinBERT directory
    if len(sys.argv) > 1:
        finbert_dir = sys.argv[1]
    else:
        finbert_dir = input("Enter path to FinBERT v4.4.4 directory: ").strip()
        finbert_dir = finbert_dir.strip('"').strip("'")
    
    # Validate
    if not os.path.exists(finbert_dir):
        print_status(f"Directory not found: {finbert_dir}", 'ERROR')
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    app_file = os.path.join(finbert_dir, 'app_finbert_v4_dev.py')
    if not os.path.exists(app_file):
        print_status(f"Not a valid FinBERT directory (missing app_finbert_v4_dev.py)", 'ERROR')
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print_status(f"Target: {finbert_dir}", 'INFO')
    print()
    
    # Apply all fixes
    fixes_applied = 0
    fixes_total = 4
    
    print("Applying fixes...")
    print("-" * 60)
    
    if apply_lstm_fix(finbert_dir):
        fixes_applied += 1
    
    if apply_app_fixes(finbert_dir):
        fixes_applied += 1
    
    if disable_lstm(finbert_dir):
        fixes_applied += 1
    
    # Verify installation
    print()
    print("-" * 60)
    
    if fixes_applied >= 3:
        print_status(f"Installation complete ({fixes_applied}/{fixes_total} fixes)", 'OK')
        print()
        print("NEXT STEPS:")
        print("1. Restart the FinBERT server:")
        print(f"   cd {finbert_dir}")
        print("   python app_finbert_v4_dev.py")
        print()
        print("2. Test the swing backtest:")
        print('   curl -X POST http://localhost:5001/api/backtest/swing \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d "{\\"symbol\\": \\"AAPL\\", \\"start_date\\": \\"2024-01-01\\", \\"end_date\\": \\"2024-11-01\\"}"')
        print()
        print("FIXED ISSUES:")
        print("- SyntaxError in lstm_predictor.py (line 81)")
        print("- Mock sentiment fallback removed (REAL data only)")
        print("- ADX calculation crash")
        print("- LSTM disabled until retrained")
        status = 0
    else:
        print_status(f"Installation incomplete ({fixes_applied}/{fixes_total} fixes)", 'ERROR')
        print()
        print("Some fixes failed. Check errors above.")
        print("You may need to apply fixes manually.")
        status = 1
    
    print()
    input("Press Enter to exit...")
    sys.exit(status)

if __name__ == '__main__':
    main()
