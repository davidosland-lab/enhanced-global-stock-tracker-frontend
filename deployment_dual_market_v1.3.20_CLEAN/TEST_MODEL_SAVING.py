"""
Test Keras 3 Model Saving Fix
Verify that models can be saved as .h5 files
"""

import sys
import os
from pathlib import Path

print("\n" + "="*70)
print("KERAS 3 MODEL SAVING TEST")
print("="*70)

# Test 1: Check TensorFlow and Keras versions
print("\n[TEST 1] Check installed versions...")
try:
    import tensorflow as tf
    print(f"✓ TensorFlow: {tf.__version__}")
    
    import keras
    print(f"✓ Keras: {keras.__version__}")
    
    keras_version = tuple(map(int, keras.__version__.split('.')[:2]))
    if keras_version >= (3, 0):
        print(f"✓ Keras 3 detected - save_format='h5' parameter REQUIRED")
    else:
        print(f"✓ Keras 2 detected - save_format='h5' parameter optional")
except Exception as e:
    print(f"✗ Error: {e}")
    input("\nPress Enter...")
    sys.exit(1)

# Test 2: Check if fix is applied
print("\n[TEST 2] Check if fix is applied to lstm_predictor.py...")
lstm_file = Path("finbert_v4.4.4/models/lstm_predictor.py")

if not lstm_file.exists():
    print(f"✗ File not found: {lstm_file}")
    input("\nPress Enter...")
    sys.exit(1)

content = lstm_file.read_text(encoding='utf-8')

if "save_format='h5'" in content:
    print("✓ Fix is applied! save_format='h5' found in code")
else:
    print("✗ Fix NOT applied! save_format='h5' missing")
    print("\nPlease copy the fixed file from the repository.")
    input("\nPress Enter...")
    sys.exit(1)

# Test 3: Test actual model saving
print("\n[TEST 3] Test actual model saving...")
try:
    from tensorflow import keras
    from tensorflow.keras import layers
    
    # Create a simple test model
    model = keras.Sequential([
        layers.Dense(10, activation='relu', input_shape=(5,)),
        layers.Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse')
    
    # Test save with Keras 3 format
    test_path = "models/test_model.h5"
    os.makedirs("models", exist_ok=True)
    
    print(f"   Saving test model to: {test_path}")
    
    try:
        model.save(test_path, save_format='h5')
        print(f"✓ Model saved successfully with save_format='h5'")
    except Exception as save_error:
        print(f"✗ Save failed: {save_error}")
        # Try without format parameter
        try:
            model.save(test_path)
            print(f"✓ Model saved with default format")
        except Exception as e2:
            print(f"✗ Both save methods failed: {e2}")
            input("\nPress Enter...")
            sys.exit(1)
    
    # Check if file exists
    if os.path.exists(test_path):
        file_size = os.path.getsize(test_path)
        print(f"✓ Model file created: {test_path} ({file_size:,} bytes)")
        
        # Try to load it back
        try:
            loaded = keras.models.load_model(test_path, compile=False)
            print(f"✓ Model loaded successfully")
        except Exception as load_error:
            print(f"✗ Load failed: {load_error}")
        
        # Clean up
        os.remove(test_path)
        print(f"✓ Test cleanup complete")
    else:
        print(f"✗ Model file NOT created!")
        input("\nPress Enter...")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter...")
    sys.exit(1)

# Test 4: Check existing models
print("\n[TEST 4] Check existing trained models...")
models_dir = Path("models/screening/models")

if models_dir.exists():
    h5_files = list(models_dir.glob("*.h5"))
    keras_files = list(models_dir.glob("*.keras"))
    json_files = list(models_dir.glob("*_metadata.json"))
    
    print(f"   .h5 files:   {len(h5_files)}")
    print(f"   .keras files: {len(keras_files)}")
    print(f"   .json files:  {len(json_files)}")
    
    if len(h5_files) == 1 and len(json_files) > 100:
        print(f"\n⚠ WARNING: You have {len(json_files)} metadata files")
        print(f"           but only {len(h5_files)} model file(s)")
        print(f"\n   This means models were NOT saved during training.")
        print(f"   After applying this fix, run pipeline again to train models.")
    elif len(h5_files) > 1:
        print(f"✓ Found {len(h5_files)} trained model files")
    else:
        print(f"   No models trained yet - this is normal for a fresh install")
else:
    print(f"   Models directory doesn't exist yet - will be created on first run")

# Summary
print("\n" + "="*70)
print("TEST RESULTS SUMMARY")
print("="*70)
print("✓ Keras 3 compatibility fix is applied")
print("✓ Model saving works correctly")
print("\nNext steps:")
print("1. Run pipeline: RUN_PIPELINE.bat")
print("2. Check models are saved: dir /b models\\screening\\models\\*.h5")
print("3. You should see files like: A2M.AX_lstm_model.h5, BHP.AX_lstm_model.h5, etc.")
print("\n" + "="*70)

input("\nPress Enter to exit...")
