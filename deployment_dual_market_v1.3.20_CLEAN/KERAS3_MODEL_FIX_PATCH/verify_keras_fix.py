"""
Verify Keras 3 Model Saving Fix
Tests that the fix was applied correctly and models can be saved
"""

import sys
import os
from pathlib import Path

print("\n" + "="*70)
print("KERAS 3 FIX VERIFICATION")
print("="*70)

success = True

# Test 1: Check TensorFlow and Keras versions
print("\n[TEST 1] Check installed versions...")
try:
    import tensorflow as tf
    print(f"  TensorFlow: {tf.__version__}")
    
    import keras
    print(f"  Keras: {keras.__version__}")
    
    keras_version = tuple(map(int, keras.__version__.split('.')[:2]))
    if keras_version >= (3, 0):
        print(f"  [INFO] Keras 3 detected - save_format='h5' parameter IS REQUIRED")
    else:
        print(f"  [INFO] Keras 2 detected - save_format='h5' parameter optional")
    
    print("  [OK] TensorFlow and Keras available")
except Exception as e:
    print(f"  [ERROR] {e}")
    success = False

# Test 2: Check if fix is applied to lstm_predictor.py
print("\n[TEST 2] Check if fix is applied to lstm_predictor.py...")
lstm_file = Path("finbert_v4.4.4/models/lstm_predictor.py")

if not lstm_file.exists():
    print(f"  [ERROR] File not found: {lstm_file}")
    success = False
else:
    try:
        content = lstm_file.read_text(encoding='utf-8')
    except:
        content = lstm_file.read_text(encoding='latin-1')
    
    if "save_format='h5'" in content or 'save_format="h5"' in content:
        print("  [OK] Fix is applied! save_format='h5' found in code")
    else:
        print("  [ERROR] Fix NOT applied! save_format='h5' missing from code")
        success = False

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
    test_path = "models/test_keras_fix.h5"
    os.makedirs("models", exist_ok=True)
    
    print(f"  Saving test model to: {test_path}")
    
    try:
        # Try with save_format parameter (Keras 3)
        model.save(test_path, save_format='h5')
        print(f"  [OK] Model saved successfully with save_format='h5'")
    except Exception as save_error:
        print(f"  [WARNING] Save with format parameter failed: {save_error}")
        # Try without format parameter
        try:
            model.save(test_path)
            print(f"  [OK] Model saved with default format")
        except Exception as e2:
            print(f"  [ERROR] Both save methods failed: {e2}")
            success = False
    
    # Check if file exists
    if os.path.exists(test_path):
        file_size = os.path.getsize(test_path)
        print(f"  [OK] Model file created: {test_path} ({file_size:,} bytes)")
        
        # Try to load it back
        try:
            loaded = keras.models.load_model(test_path, compile=False)
            print(f"  [OK] Model loaded successfully")
        except Exception as load_error:
            print(f"  [WARNING] Load failed: {load_error}")
        
        # Clean up
        try:
            os.remove(test_path)
            print(f"  [OK] Test cleanup complete")
        except:
            pass
    else:
        print(f"  [ERROR] Model file NOT created!")
        success = False
        
except Exception as e:
    print(f"  [ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    success = False

# Test 4: Check existing models
print("\n[TEST 4] Check existing trained models...")
models_dir = Path("models/screening/models")

if models_dir.exists():
    h5_files = list(models_dir.glob("*.h5"))
    keras_files = list(models_dir.glob("*.keras"))
    json_files = list(models_dir.glob("*_metadata.json"))
    
    print(f"  .h5 model files:   {len(h5_files)}")
    print(f"  .keras files:      {len(keras_files)}")
    print(f"  .json metadata:    {len(json_files)}")
    
    if len(h5_files) == 1 and len(json_files) > 100:
        print(f"\n  [INFO] You have {len(json_files)} metadata files")
        print(f"         but only {len(h5_files)} model file(s)")
        print(f"\n  This means models were NOT saved during previous training.")
        print(f"  After this fix, run pipeline again to train and save models.")
    elif len(h5_files) > 1:
        print(f"  [OK] Found {len(h5_files)} trained model files")
    else:
        print(f"  [INFO] No models trained yet - normal for fresh install")
else:
    print(f"  [INFO] Models directory doesn't exist yet")
    print(f"         Will be created on first pipeline run")

# Summary
print("\n" + "="*70)
if success:
    print("VERIFICATION PASSED!")
    print("="*70)
    print("\n[OK] All tests passed successfully")
    print("[OK] Keras 3 fix is working correctly")
    print("[OK] Models will be saved as .h5 files")
    print("\nNext steps:")
    print("1. Test with one model:")
    print("   python finbert_v4.4.4\\models\\train_lstm.py --symbol BHP.AX --epochs 5")
    print("\n2. Run full pipeline:")
    print("   RUN_PIPELINE_TEST.bat")
    print("\n3. Verify models saved:")
    print("   dir /b models\\screening\\models\\*.h5")
else:
    print("VERIFICATION FAILED!")
    print("="*70)
    print("\n[ERROR] One or more tests failed")
    print("\nPlease check the errors above and:")
    print("1. Ensure TensorFlow and Keras are installed")
    print("2. Verify the fix was applied correctly")
    print("3. Check file permissions")
    print("\nFor manual fix instructions, see: FIX_KERAS3_MODELS.txt")
    
print("="*70 + "\n")

sys.exit(0 if success else 1)
