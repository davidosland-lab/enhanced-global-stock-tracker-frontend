#!/usr/bin/env python3
"""
Fix Training Hang Issues - v1.3.15.87
Reduces batch size from 32 to 16 for better stability
"""
import os
import sys
import shutil
from datetime import datetime

def print_header(msg):
    print(f"\n{'='*80}")
    print(f"  {msg}")
    print(f"{'='*80}\n")

def fix_batch_size():
    """Reduce batch size in train_lstm.py"""
    
    file_path = os.path.join('finbert_v4.4.4', 'models', 'train_lstm.py')
    
    if not os.path.exists(file_path):
        print(f"❌ ERROR: File not found: {file_path}")
        print("   Make sure you're running this from: unified_trading_dashboard_v1.3.15.87_ULTIMATE/")
        return False
    
    print(f"[OK] Found: {file_path}")
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    try:
        shutil.copy2(file_path, backup_path)
        print(f"[OK] Backup created: {backup_path}")
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False
    
    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return False
    
    # Check current batch size
    if 'batch_size=16' in content:
        print("[OK] Already fixed: batch_size=16")
        return True
    elif 'batch_size=8' in content:
        print("[OK] Already fixed: batch_size=8")
        return True
    elif 'batch_size=32' not in content:
        print("⚠ WARNING: batch_size=32 not found in file")
        print("   File may have been modified or have different format")
        return False
    
    # Apply fix
    content = content.replace('batch_size=32', 'batch_size=16')
    
    # Write fixed file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Fixed: {file_path}")
        print(f"  Changed: batch_size=32 → batch_size=16")
        return True
    except Exception as e:
        print(f"❌ Failed to write file: {e}")
        # Restore backup
        shutil.copy2(backup_path, file_path)
        print(f"[OK] Restored from backup")
        return False

def main():
    print_header("TRAINING HANG FIX v1.3.15.87")
    
    print("This fix reduces batch size from 32 to 16")
    print("This helps prevent:")
    print("  • Memory exhaustion")
    print("  • Training hangs at later epochs")
    print("  • System freezing\n")
    
    # Check current directory
    if not os.path.exists('finbert_v4.4.4'):
        print("❌ ERROR: finbert_v4.4.4 directory not found")
        print("   Please run this script from: unified_trading_dashboard_v1.3.15.87_ULTIMATE/")
        sys.exit(1)
    
    print("[OK] Found finbert_v4.4.4 directory")
    
    # Apply fix
    print("\nApplying fix...")
    success = fix_batch_size()
    
    if success:
        print_header("FIX APPLIED SUCCESSFULLY!")
        print("[OK] Batch size reduced from 32 to 16")
        print("\nNext steps:")
        print("  1. Restart Flask server (CTRL+C then restart)")
        print("  2. Use curl to train (not web interface):")
        print()
        print("     curl -X POST http://localhost:5001/api/train/AAPL \\")
        print('       -H "Content-Type: application/json" \\')
        print('       -d "{\\"epochs\\": 20, \\"sequence_length\\": 60}"')
        print()
        print("  3. Watch Flask console for progress")
        print("  4. Training should complete without hanging")
        print()
        print("💡 TIP: Start with 20 epochs to test, then try 50 epochs")
    else:
        print_header("FIX FAILED")
        print("Please check the error messages above")
        print("\nManual fix:")
        print("  1. Open: finbert_v4.4.4/models/train_lstm.py")
        print("  2. Find: batch_size=32")
        print("  3. Change to: batch_size=16")
        print("  4. Save and restart Flask")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Fix interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
