"""
Check LSTM Models Status
========================

This script checks if LSTM models are found and being used by the pipeline.
"""

import sys
from pathlib import Path

print("\n" + "="*80)
print("LSTM MODELS CHECK")
print("="*80)

# Check 1: Where does lstm_trainer.py look for models?
print("\n[CHECK 1] Checking lstm_trainer.py configuration...")
trainer_file = Path("models/screening/lstm_trainer.py")

if trainer_file.exists():
    content = trainer_file.read_text(encoding='utf-8')
    
    # Find models_dir definition
    for line in content.split('\n'):
        if 'self.models_dir' in line and '=' in line:
            print(f"Found: {line.strip()}")
    
    print("\n✓ lstm_trainer.py exists")
else:
    print("✗ lstm_trainer.py not found!")

# Check 2: Do model files exist?
print("\n[CHECK 2] Checking for model files...")

possible_locations = [
    Path("models/screening/models"),
    Path("models/lstm"),
    Path("finbert_v4.4.4/models/trained")
]

total_models = 0
for location in possible_locations:
    if location.exists():
        h5_files = list(location.glob("*.h5"))
        keras_files = list(location.glob("*.keras"))
        all_models = h5_files + keras_files
        
        if all_models:
            print(f"\n✓ Found {len(all_models)} models in: {location}")
            print(f"  .h5 files: {len(h5_files)}")
            print(f"  .keras files: {len(keras_files)}")
            
            # Show first 5 examples
            print(f"  Examples:")
            for model in all_models[:5]:
                print(f"    - {model.name}")
            
            total_models += len(all_models)
        else:
            print(f"⚠️  Directory exists but no models: {location}")
    else:
        print(f"✗ Directory not found: {location}")

print(f"\nTotal models found: {total_models}")

# Check 3: Test lstm_trainer import and initialization
print("\n[CHECK 3] Testing lstm_trainer import...")
try:
    from models.screening.lstm_trainer import LSTMTrainer
    print("✓ LSTMTrainer imported successfully")
    
    # Try to create instance
    trainer = LSTMTrainer()
    print(f"✓ LSTMTrainer instance created")
    print(f"  Models directory: {trainer.models_dir}")
    
    # Check if directory exists
    if trainer.models_dir.exists():
        models_in_dir = list(trainer.models_dir.glob("*.h5")) + list(trainer.models_dir.glob("*.keras"))
        print(f"  Models in configured directory: {len(models_in_dir)}")
        
        if models_in_dir:
            print(f"  ✓ Trainer will find {len(models_in_dir)} models")
        else:
            print(f"  ⚠️  No models in configured directory!")
            print(f"     Models need to be in: {trainer.models_dir}")
    else:
        print(f"  ✗ Configured directory doesn't exist: {trainer.models_dir}")
    
except ImportError as e:
    print(f"✗ Import failed: {e}")
except Exception as e:
    print(f"✗ Error: {e}")

# Check 4: Summary and recommendations
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if total_models > 0:
    print(f"\n✓ Found {total_models} trained LSTM models")
    print("\nRecommendations:")
    
    if total_models < 100:
        print(f"  ⚠️  Expected ~100-140 models (one per stock)")
        print(f"     You may need to train more models")
    else:
        print(f"  ✓ Good number of models ({total_models})")
    
    # Check if models are in the right place
    trainer_models = Path("models/screening/models")
    if trainer_models.exists():
        models_here = len(list(trainer_models.glob("*.h5")) + list(trainer_models.glob("*.keras")))
        if models_here > 0:
            print(f"  ✓ Models are in correct location for trainer")
        else:
            print(f"  ⚠️  Models exist but not in trainer's location")
            print(f"     Trainer looks in: {trainer_models}")
            print(f"     You may need to move models there")
    
    print("\nPipeline behavior:")
    print("  - LSTM predictions will be used")
    print("  - Models won't be retrained unless stale (>7 days)")
    print("  - This saves ~2 hours per pipeline run")
else:
    print("\n⚠️  NO LSTM models found")
    print("\nThis means:")
    print("  - Pipeline will train models from scratch (~2 hours)")
    print("  - Or LSTM predictions will be skipped")
    print("\nTo fix:")
    print("  1. Run pipeline once to train models")
    print("  2. Or copy existing models to: models/screening/models/")

print("\n" + "="*80)

input("\nPress Enter to exit...")
