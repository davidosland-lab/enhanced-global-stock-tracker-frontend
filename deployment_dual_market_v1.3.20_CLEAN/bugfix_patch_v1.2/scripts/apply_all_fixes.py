"""
Bug Fix Patch v1.2 - Master Installer
FinBERT v4.4.4 - Windows Compatible
NO MOCK/FAKE/SYNTHETIC DATA
"""

import sys
import os

# Force UTF-8 output for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("\n" + "="*60)
print("FinBERT v4.4.4 - Bug Fix Patch v1.2")
print("NO MOCK/FAKE/SYNTHETIC DATA - REAL DATA ONLY")
print("="*60)

# Get FinBERT path
finbert_path = input("\nEnter path to FinBERT installation (e.g., C:\\Users\\david\\AATelS): ").strip()

if not os.path.exists(finbert_path):
    print(f"\nERROR: Path not found: {finbert_path}")
    sys.exit(1)

# Verify finbert_v4.4.4 exists
finbert_v4_path = os.path.join(finbert_path, 'finbert_v4.4.4')
if not os.path.exists(finbert_v4_path):
    print(f"\nERROR: finbert_v4.4.4 not found in: {finbert_path}")
    print("Make sure you provided the PARENT directory containing finbert_v4.4.4/")
    sys.exit(1)

print(f"\n[OK] Found FinBERT installation at: {finbert_v4_path}")

# Import and run fixes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'fixes'))

fixes_applied = 0
fixes_total = 3

print("\n" + "="*60)
print("Applying Fixes...")
print("="*60)

# Fix 1: app_finbert_v4_dev.py
try:
    from fix_app_errors import apply_fix as fix_app
    if fix_app(finbert_path):
        fixes_applied += 1
        print("\n[1/3] App error fixes: SUCCESS")
    else:
        print("\n[1/3] App error fixes: FAILED")
except Exception as e:
    print(f"\n[1/3] App error fixes: ERROR - {e}")

# Fix 2: config_dev.py
try:
    from fix_config import apply_fix as fix_config
    if fix_config(finbert_path):
        fixes_applied += 1
        print("[2/3] Config updates: SUCCESS")
    else:
        print("[2/3] Config updates: FAILED")
except Exception as e:
    print(f"[2/3] Config updates: ERROR - {e}")

# Fix 3: lstm_predictor.py  
try:
    from fix_lstm_predictor import apply_fix as fix_lstm
    if fix_lstm(finbert_path):
        fixes_applied += 1
        print("[3/3] LSTM predictor fix: SUCCESS")
    else:
        print("[3/3] LSTM predictor fix: FAILED")
except Exception as e:
    print(f"[3/3] LSTM predictor fix: ERROR - {e}")

# Summary
print("\n" + "="*60)
print(f"Patch Installation Complete: {fixes_applied}/{fixes_total} fixes applied")
print("="*60)

if fixes_applied == fixes_total:
    print("\n[SUCCESS] All fixes applied successfully!")
    print("\nNext steps:")
    print("1. Restart FinBERT server:")
    print(f"   cd {finbert_path}")
    print("   python finbert_v4.4.4/app_finbert_v4_dev.py")
    print("\n2. System will now use REAL data only")
    print("3. No more crashes or mock sentiment errors")
else:
    print(f"\n[WARNING] Only {fixes_applied}/{fixes_total} fixes applied")
    print("Some issues may remain. Review errors above.")

print("\nAll backups saved with .backup_TIMESTAMP extension")
print("You can restore from backup if needed")

input("\nPress Enter to exit...")
