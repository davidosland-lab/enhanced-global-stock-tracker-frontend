"""
Check if you have the fixed version of lstm_predictor.py and train_lstm.py
"""

import sys
from pathlib import Path

print("\n" + "="*70)
print("KERAS 3 FIX - FILE VERSION CHECKER")
print("="*70)

success = True

# Check lstm_predictor.py
print("\n[1] Checking finbert_v4.4.4/models/lstm_predictor.py...")
lstm_file = Path("finbert_v4.4.4/models/lstm_predictor.py")

if not lstm_file.exists():
    print("    ✗ FILE NOT FOUND!")
    success = False
else:
    content = lstm_file.read_text(encoding='utf-8', errors='ignore')
    
    # Check for fixes
    has_symbol_param = "symbol: str = None" in content
    has_symbol_specific_path = "f'models/{symbol}_lstm_model.keras'" in content
    has_clean_save = "self.model.save(self.model_path)" in content and "save_format=" not in content
    
    print(f"    File size: {len(content):,} bytes")
    
    if has_symbol_param:
        print("    ✓ Has 'symbol' parameter in __init__")
    else:
        print("    ✗ MISSING 'symbol' parameter in __init__")
        success = False
    
    if has_symbol_specific_path:
        print("    ✓ Uses symbol-specific path: f'models/{symbol}_lstm_model.keras'")
    else:
        print("    ✗ MISSING symbol-specific path (still using generic path)")
        success = False
    
    if has_clean_save:
        print("    ✓ Uses clean save (no save_format parameter)")
    else:
        print("    ✗ Still uses save_format parameter or wrong save method")
        success = False

# Check train_lstm.py
print("\n[2] Checking finbert_v4.4.4/models/train_lstm.py...")
train_file = Path("finbert_v4.4.4/models/train_lstm.py")

if not train_file.exists():
    print("    ✗ FILE NOT FOUND!")
    success = False
else:
    content = train_file.read_text(encoding='utf-8', errors='ignore')
    
    # Check for fixes
    passes_symbol = "symbol=symbol" in content
    
    print(f"    File size: {len(content):,} bytes")
    
    if passes_symbol:
        print("    ✓ Passes symbol to StockLSTMPredictor")
    else:
        print("    ✗ MISSING: Does NOT pass symbol to StockLSTMPredictor")
        success = False

# Summary
print("\n" + "="*70)
if success:
    print("✓ ALL CHECKS PASSED - YOU HAVE THE FIXED VERSION!")
    print("="*70)
    print("\nYour files are correct. Models should save as:")
    print("  models/BHP.AX_lstm_model.keras")
    print("  models/BHP.AX_scaler.pkl")
    print("\nIf they're not, there may be a different issue.")
else:
    print("✗ CHECKS FAILED - YOU HAVE THE OLD VERSION!")
    print("="*70)
    print("\nYou need to download and install the fixed files.")
    print("\nSTEPS:")
    print("1. Download files from GenSpark or GitHub:")
    print("   - lstm_predictor.py")
    print("   - train_lstm.py")
    print("\n2. Copy to: finbert_v4.4.4\\models\\")
    print("\n3. Run this checker again")
    print("\nSee: GENSPARK_FILE_ACCESS_INSTRUCTIONS.txt")

print("="*70 + "\n")

sys.exit(0 if success else 1)
