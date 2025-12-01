"""
Fix Keras 3 Model Format
=========================

Keras 3 uses .keras format instead of .h5
This script updates lstm_trainer.py to use the new format.
"""

from pathlib import Path
import shutil
from datetime import datetime

print("\n" + "="*80)
print("FIX KERAS 3 MODEL FORMAT")
print("="*80)

lstm_trainer_file = Path("models/screening/lstm_trainer.py")

if not lstm_trainer_file.exists():
    print("\n❌ lstm_trainer.py not found!")
    input("Press Enter...")
    exit(1)

print(f"\n✓ Found: {lstm_trainer_file}")

# Backup
print("\n[1/3] Creating backup...")
backup = lstm_trainer_file.parent / f"lstm_trainer.py.backup_keras3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(lstm_trainer_file, backup)
print(f"✓ Backup: {backup.name}")

# Read
print("\n[2/3] Updating file...")
try:
    content = lstm_trainer_file.read_text(encoding='utf-8')
except:
    content = lstm_trainer_file.read_text(encoding='latin-1')

# Replace all .h5 references with .keras
changes_made = 0

# Change 1: model file extension in path construction
old1 = "model_path = self.models_dir / f'{symbol}_lstm_model.h5'"
new1 = "model_path = self.models_dir / f'{symbol}_lstm_model.keras'"
if old1 in content:
    content = content.replace(old1, new1)
    print("  ✓ Updated model_path construction")
    changes_made += 1

# Change 2: glob pattern for finding models
old2 = "model_files = list(self.models_dir.glob('*_lstm_model.h5'))"
new2 = "model_files = list(self.models_dir.glob('*_lstm_model.keras'))"
if old2 in content:
    content = content.replace(old2, new2)
    print("  ✓ Updated glob pattern")
    changes_made += 1

# Also check for .keras files as fallback
old3 = "model_files = list(self.models_dir.glob('*_lstm_model.keras'))"
new3 = """model_files = list(self.models_dir.glob('*_lstm_model.keras'))
        # Also check for legacy .h5 files
        if not model_files:
            model_files = list(self.models_dir.glob('*_lstm_model.h5'))"""
if old3 in content:
    content = content.replace(old3, new3)
    print("  ✓ Added .h5 fallback check")
    changes_made += 1

if changes_made == 0:
    print("  ⚠️  No exact patterns found, trying general replacement...")
    # General replacement
    content = content.replace('_lstm_model.h5', '_lstm_model.keras')
    content = content.replace("'*.h5'", "'*.keras'")
    content = content.replace('"*.h5"', '"*.keras"')
    print(f"  ✓ Replaced .h5 with .keras ({content.count('.keras')} occurrences)")

# Write
print("\n[3/3] Writing file...")
try:
    lstm_trainer_file.write_text(content, encoding='utf-8')
except:
    lstm_trainer_file.write_text(content, encoding='utf-8', errors='ignore')

print("✓ File updated")

# Summary
print("\n" + "="*80)
print("FIX APPLIED!")
print("="*80)
print("\nChanges made:")
print("  - Model files now use .keras format (Keras 3 native)")
print("  - Trainer will save/load .keras files")
print("  - Compatible with your installed Keras 3.11.3")
print("\nNext:")
print("  1. Check for existing .keras models:")
print("     dir models\\screening\\models\\*.keras")
print("\n  2. If .keras files exist, rename them to match pattern:")
print("     {SYMBOL}_lstm_model.keras")
print("\n  3. Or run pipeline to train new models in correct format")
print("\n" + "="*80)

input("\nPress Enter...")
