"""
LSTM Feature Mismatch Fix

Resolves the error: "X has 5 features, but MinMaxScaler is expecting 8 features"

This script:
1. Backs up existing LSTM models (if they exist)
2. Clears the mismatched models
3. Allows fresh training with correct features

Run with: python scripts/fix_lstm_feature_mismatch.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("\n" + "="*80)
print("LSTM FEATURE MISMATCH FIX")
print("="*80)
print()

# Find model files
model_dirs = [
    'finbert_v4.4.4/models',
    'models',
    'ml_pipeline/models'
]

model_files_found = []

for model_dir in model_dirs:
    model_path = Path(model_dir)
    if model_path.exists():
        # Look for LSTM model files
        lstm_files = list(model_path.glob('lstm_model*.h5'))
        scaler_files = list(model_path.glob('scaler*.pkl'))
        
        model_files_found.extend(lstm_files)
        model_files_found.extend(scaler_files)

if not model_files_found:
    print("✅ No LSTM model files found - fresh training will work correctly")
    print()
    print("="*80)
    sys.exit(0)

print(f"Found {len(model_files_found)} model files:")
for f in model_files_found:
    print(f"  • {f}")
print()

# Ask for confirmation
print("⚠️  These files have a feature mismatch (expect 8 features, have 5)")
print()
print("Options:")
print("  1. Backup and remove (recommended) - Allows fresh training")
print("  2. Just remove - Deletes old models")
print("  3. Cancel - Keep models (predictions will use fallback)")
print()

choice = input("Choice [1/2/3]: ").strip()

if choice == '3':
    print("\nCancelled - no changes made")
    print("LSTM predictions will continue using fallback method")
    sys.exit(0)

# Create backup if requested
if choice == '1':
    backup_dir = Path('backups') / f'lstm_models_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nBacking up to: {backup_dir}")
    for f in model_files_found:
        dest = backup_dir / f.name
        shutil.copy2(f, dest)
        print(f"  ✓ Backed up: {f.name}")
    print()

# Remove model files
print("Removing model files...")
for f in model_files_found:
    try:
        f.unlink()
        print(f"  ✓ Removed: {f}")
    except Exception as e:
        print(f"  ✗ Failed to remove {f}: {e}")

print()
print("="*80)
print("✅ FIX COMPLETE")
print("="*80)
print()
print("What happens next:")
print("  1. LSTM predictions will use fallback method (technical analysis)")
print("  2. Pipeline will collect data for 3-7 days")
print("  3. After sufficient data, retrain LSTM with correct features")
print("  4. New model will have 5 features (close, volume, high, low, open)")
print()
print("To retrain LSTM after collecting data:")
print("  python scripts/retrain_lstm_models.py --symbols AAPL,MSFT,GOOGL")
print()
print("="*80)
